import re
import unicodedata
from decimal import Decimal
from typing import Any, ClassVar

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.pncp_contracting import PNCPContractingRecord
from app.models.pncp_opportunity_assessment import (
    PNCPOpportunityAssessmentRecord,
)
from app.models.pncp_processing_run import PNCPProcessingRunRecord
from app.repositories.pncp_audit_repository import PNCPAuditRepository
from app.repositories.pncp_opportunity_assessment_repository import (
    PNCPOpportunityAssessmentRepository,
)
from app.schemas.pncp_opportunities import (
    PNCPOpportunityAssessmentInput,
    PNCPOpportunityClassificationStats,
    PNCPOpportunityDocumentResponse,
    PNCPOpportunityHistoryResponse,
    PNCPOpportunityItemResponse,
    PNCPOpportunityResponse,
    PNCPProcessingRunResponse,
)
from app.services.projector_profile_analyzer import ProjectorProfileAnalyzer


class PNCPOpportunityService:
    ANALYZER_VERSION: ClassVar[str] = "1.0.0"
    PROJECTOR_PATTERNS: ClassVar[dict[str, re.Pattern[str]]] = {
        "projetor": re.compile(r"\bprojetor(?:es)?\b"),
        "videoprojetor": re.compile(
            r"\bvideo[ -]?projetor(?:es)?\b|\bvideoprojetor(?:es)?\b"
        ),
        "datashow": re.compile(r"\bdata[ -]?show\b|\bdatashow\b"),
        "equipamento de projecao": re.compile(r"\bequipamento(?:s)? de projecao\b"),
        "sistema de projecao": re.compile(r"\bsistema(?:s)? de projecao\b"),
    }
    MULTIMEDIA_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\bmultimidia\b")
    FALSE_POSITIVE_PATTERNS: ClassVar[dict[str, re.Pattern[str]]] = {
        "caixa de som multimidia": re.compile(
            r"\bcaixa(?:s)? de som.{0,80}multimidia\b"
        ),
        "kit multimidia automotivo": re.compile(
            r"\bkit multimidia\b|\bcentral multimidia\b"
        ),
        "veiculo com multimidia": re.compile(
            r"\bveiculo(?:s)?\b.{0,500}\bmultimidia\b"
        ),
        "monitor multimidia": re.compile(r"\bmonitor(?:es)?\b.{0,120}\bmultimidia\b"),
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = PNCPOpportunityAssessmentRepository(db)
        self.audit_repository = PNCPAuditRepository(db)

    def classify_all(
        self,
        *,
        perfil: str = "projetores",
        limite_contratacoes: int | None = None,
    ) -> PNCPOpportunityClassificationStats:
        if perfil != "projetores":
            raise ValueError("Perfil de classificação ainda não suportado.")

        statement = (
            select(PNCPContractingRecord)
            .options(
                selectinload(PNCPContractingRecord.items),
                selectinload(PNCPContractingRecord.documents),
            )
            .order_by(PNCPContractingRecord.id)
        )
        if limite_contratacoes:
            statement = statement.limit(limite_contratacoes)

        profile_version = ProjectorProfileAnalyzer.PROFILE.versao
        run = self.audit_repository.start_run(
            tipo="CLASSIFICACAO_OPORTUNIDADES",
            perfil=perfil,
            perfil_versao=profile_version,
            analisador_versao=self.ANALYZER_VERSION,
            parametros={"limite_contratacoes": limite_contratacoes},
        )
        self.db.commit()
        run_id = run.id
        stats = PNCPOpportunityClassificationStats(execucao_id=run_id)
        fatal_error: str | None = None

        try:
            for contracting in self.db.scalars(statement).unique():
                try:
                    payload = self.classify_contracting(contracting, perfil=perfil)
                    assessment, _ = self.repository.upsert(payload, execucao_id=run_id)
                    self.audit_repository.record_assessment(
                        run_id=run_id,
                        assessment=assessment,
                        payload=payload,
                    )
                    self.db.commit()
                    self._update_stats(stats, payload)
                except Exception:
                    stats.erros += 1
                    self.db.rollback()
        except Exception as exc:
            self.db.rollback()
            fatal_error = f"{exc.__class__.__name__}: {exc}"[:2000]
            stats.erros += 1

        run = self.db.get(PNCPProcessingRunRecord, run_id)
        if run is None:
            raise RuntimeError("Execução de auditoria não encontrada.")
        if fatal_error:
            status = "FALHOU"
        elif stats.erros:
            status = "CONCLUIDA_COM_ERROS"
        else:
            status = "CONCLUIDA"
        stats.status_execucao = status
        self.audit_repository.finish_run(
            run,
            status=status,
            estatisticas=stats.model_dump(
                mode="json", exclude={"execucao_id", "status_execucao"}
            ),
            erro=fatal_error,
        )
        self.db.commit()
        return stats

    @staticmethod
    def _update_stats(
        stats: PNCPOpportunityClassificationStats,
        payload: PNCPOpportunityAssessmentInput,
    ) -> None:
        stats.processadas += 1
        if payload.classificacao == "CONFIRMADA_ITEM":
            stats.confirmadas_item += 1
        elif payload.classificacao == "CONFIRMADA_DOCUMENTO":
            stats.confirmadas_documento += 1
        elif payload.classificacao == "CANDIDATA_DOCUMENTO":
            stats.candidatas_documento += 1
        elif payload.classificacao == "DESCARTADA_FALSO_POSITIVO":
            stats.descartadas_falso_positivo += 1
        else:
            stats.sem_correspondencia += 1

        if payload.adequacao_perfil == "ADEQUADA":
            stats.adequadas += 1
        elif payload.adequacao_perfil == "PARCIALMENTE_ADEQUADA":
            stats.parcialmente_adequadas += 1
        elif payload.adequacao_perfil == "INCOMPATIVEL":
            stats.incompativeis += 1
        elif payload.adequacao_perfil == "EXIGE_ANALISE_HUMANA":
            stats.exigem_analise_humana += 1
        else:
            stats.sem_avaliacao_tecnica += 1

    @classmethod
    def classify_contracting(
        cls,
        contracting: PNCPContractingRecord,
        *,
        perfil: str = "projetores",
    ) -> PNCPOpportunityAssessmentInput:
        raw = contracting.dados_fonte or {}
        object_text = " ".join(
            part
            for part in [
                contracting.objeto_compra,
                raw.get("informacaoComplementar"),
            ]
            if part
        )
        normalized_object = cls._normalize_text(object_text)
        object_terms = cls._projector_terms(normalized_object)
        object_multimedia = bool(cls.MULTIMEDIA_PATTERN.search(normalized_object))
        object_false = cls._false_positive_terms(normalized_object)

        item_evidence: list[dict[str, Any]] = []
        structured_item_candidates: list[dict[str, Any]] = []
        confirmed_item_terms: set[str] = set()
        multimedia_item_evidence: list[dict[str, Any]] = []
        false_positive_terms: set[str] = set(object_false)

        for item in contracting.items:
            item_text = " ".join(
                part for part in [item.descricao, item.informacao_complementar] if part
            )
            normalized_item = cls._normalize_text(item_text)
            terms = cls._projector_terms(normalized_item)
            false_terms = cls._false_positive_terms(normalized_item)
            false_positive_terms.update(false_terms)
            if terms:
                confirmed_item_terms.update(terms)
                structured = ProjectorProfileAnalyzer.analyze_pncp_item(
                    numero_item=item.numero_item,
                    descricao=item_text,
                    quantidade=cls._json_decimal(item.quantidade),
                    unidade_medida=item.unidade_medida,
                )
                structured_item_candidates.append(structured)
                item_evidence.append(
                    {
                        "numero_item": item.numero_item,
                        "descricao": item.descricao,
                        "termos": sorted(terms),
                        "quantidade": cls._json_decimal(item.quantidade),
                        "unidade_medida": item.unidade_medida,
                        "dados_estruturados": structured,
                    }
                )
            elif cls.MULTIMEDIA_PATTERN.search(normalized_item):
                multimedia_item_evidence.append(
                    {
                        "numero_item": item.numero_item,
                        "descricao": item.descricao,
                        "contextos_descartados": sorted(false_terms),
                    }
                )

        document_evidence: list[dict[str, Any]] = []
        metadata_document_terms: set[str] = set()
        content_document_terms: set[str] = set()
        document_analyses: list[dict[str, Any]] = []

        for document in contracting.documents:
            metadata_text = " ".join(
                part for part in [document.titulo, document.tipo_documento_nome] if part
            )
            metadata_normalized = cls._normalize_text(metadata_text)
            metadata_terms = cls._projector_terms(metadata_normalized)
            metadata_document_terms.update(metadata_terms)

            content_text = document.texto_extraido or ""
            content_normalized = cls._normalize_text(content_text)
            content_terms = cls._projector_terms(content_normalized)
            content_document_terms.update(content_terms)
            structured = ProjectorProfileAnalyzer.analyze_document(content_text)
            if structured["itens_projetor"]:
                document_analyses.append(structured)

            specifications = cls._structured_specifications(structured)
            if metadata_terms or content_terms or document.conteudo_analisado_em:
                document_evidence.append(
                    {
                        "sequencial_documento": document.sequencial_documento,
                        "titulo": document.titulo,
                        "termos_metadados": sorted(metadata_terms),
                        "termos_conteudo": sorted(content_terms),
                        "especificacoes": specifications,
                        "itens_estruturados": structured["itens_projetor"],
                        "trechos": cls._structured_snippets(structured, content_text),
                        "extracao_status": document.extracao_status,
                        "extrator_versao": document.extrator_versao,
                        "conteudo_sha256": document.conteudo_sha256,
                        "texto_caracteres": document.texto_caracteres,
                        "paginas_extraidas": document.paginas_extraidas,
                        "data_publicacao_pncp": (
                            document.data_publicacao_pncp.isoformat()
                            if document.data_publicacao_pncp
                            else None
                        ),
                        "conteudo_analisado_em": (
                            document.conteudo_analisado_em.isoformat()
                            if document.conteudo_analisado_em
                            else None
                        ),
                        "coletado_em": (
                            document.criado_em.isoformat()
                            if document.criado_em
                            else None
                        ),
                        "url": document.url,
                        "uri": document.uri,
                    }
                )

        best_document_analysis = cls._best_document_analysis(document_analyses)
        technical_data = cls._technical_assessment(
            structured_item_candidates=structured_item_candidates,
            document_analysis=best_document_analysis,
        )

        all_terms = (
            set(object_terms)
            | confirmed_item_terms
            | metadata_document_terms
            | content_document_terms
        )
        document_specifications = sorted(
            {
                specification
                for evidence in document_evidence
                for specification in evidence["especificacoes"]
            }
        )
        evidencias: dict[str, Any] = {
            "fonte": {
                "numero_controle_pncp": contracting.numero_controle_pncp,
                "data_publicacao_pncp": (
                    contracting.data_publicacao_pncp.isoformat()
                    if contracting.data_publicacao_pncp
                    else None
                ),
            },
            "objeto": {
                "termos": sorted(object_terms),
                "multimidia_generico": object_multimedia,
            },
            "itens_confirmados": item_evidence,
            "itens_multimidia_genericos": multimedia_item_evidence,
            "documentos": document_evidence,
            "especificacoes_documentos": document_specifications,
            "avaliacao_perfil": technical_data,
            "contextos_falso_positivo": sorted(false_positive_terms),
        }

        if confirmed_item_terms:
            classification = "CONFIRMADA_ITEM"
            score = 100
        elif content_document_terms:
            classification = "CONFIRMADA_DOCUMENTO"
            score = 90 if best_document_analysis else 85
        elif object_terms or metadata_document_terms:
            classification = "CANDIDATA_DOCUMENTO"
            score = 70 if metadata_document_terms else 60
        elif false_positive_terms and (object_multimedia or multimedia_item_evidence):
            classification = "DESCARTADA_FALSO_POSITIVO"
            score = 0
        elif object_multimedia or multimedia_item_evidence:
            classification = "CANDIDATA_DOCUMENTO"
            score = 35
            all_terms.add("multimidia")
        else:
            classification = "SEM_CORRESPONDENCIA"
            score = 0

        evaluation = technical_data.get("avaliacao") or {}
        adequacy = evaluation.get("adequacao")
        if classification not in {"CONFIRMADA_ITEM", "CONFIRMADA_DOCUMENTO"}:
            adequacy = None
            evaluation = {}
            technical_data = {}
        evidencias["rastreabilidade_requisitos"] = cls._requirement_trace(
            technical_data
        )

        return PNCPOpportunityAssessmentInput(
            contracting_id=contracting.id,
            perfil=perfil,
            perfil_versao=ProjectorProfileAnalyzer.PROFILE.versao,
            analisador_versao=cls.ANALYZER_VERSION,
            classificacao=classification,
            pontuacao=score,
            termos_encontrados=sorted(all_terms),
            evidencias=evidencias,
            adequacao_perfil=adequacy,
            pontuacao_adequacao=evaluation.get("pontuacao"),
            requisitos_atendidos=evaluation.get("requisitos_atendidos", []),
            requisitos_nao_atendidos=evaluation.get("requisitos_nao_atendidos", []),
            requisitos_nao_comprovados=evaluation.get("requisitos_nao_comprovados", []),
            dados_estruturados=technical_data,
        )

    def list_opportunities(
        self,
        *,
        perfil: str = "projetores",
        perfil_versao: str | None = None,
        classificacao: str | None = None,
        adequacao: str | None = None,
        uf: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PNCPOpportunityResponse]:
        selected_profile_version = (
            perfil_versao or ProjectorProfileAnalyzer.PROFILE.versao
        )
        statement = (
            select(PNCPOpportunityAssessmentRecord)
            .join(PNCPOpportunityAssessmentRecord.contracting)
            .options(
                selectinload(PNCPOpportunityAssessmentRecord.contracting).selectinload(
                    PNCPContractingRecord.items
                ),
                selectinload(PNCPOpportunityAssessmentRecord.contracting).selectinload(
                    PNCPContractingRecord.documents
                ),
            )
            .where(PNCPOpportunityAssessmentRecord.perfil == perfil)
            .where(
                PNCPOpportunityAssessmentRecord.perfil_versao
                == selected_profile_version
            )
            .order_by(
                PNCPOpportunityAssessmentRecord.pontuacao_adequacao.desc(),
                PNCPOpportunityAssessmentRecord.pontuacao.desc(),
                PNCPContractingRecord.data_publicacao_pncp.desc(),
            )
            .offset(skip)
            .limit(limit)
        )
        if classificacao:
            statement = statement.where(
                PNCPOpportunityAssessmentRecord.classificacao == classificacao
            )
        if adequacao:
            statement = statement.where(
                PNCPOpportunityAssessmentRecord.adequacao_perfil == adequacao
            )
        if uf:
            statement = statement.where(PNCPContractingRecord.uf == uf.strip().upper())
        return [
            self._response(record) for record in self.db.scalars(statement).unique()
        ]

    @staticmethod
    def _response(
        assessment: PNCPOpportunityAssessmentRecord,
    ) -> PNCPOpportunityResponse:
        contracting = assessment.contracting
        return PNCPOpportunityResponse(
            assessment_id=assessment.id,
            contracting_id=contracting.id,
            perfil=assessment.perfil,
            perfil_versao=assessment.perfil_versao,
            analisador_versao=assessment.analisador_versao,
            ultima_execucao_id=assessment.ultima_execucao_id,
            classificacao=assessment.classificacao,
            pontuacao=assessment.pontuacao,
            termos_encontrados=assessment.termos_encontrados or [],
            evidencias=assessment.evidencias or {},
            adequacao_perfil=assessment.adequacao_perfil,
            pontuacao_adequacao=assessment.pontuacao_adequacao,
            requisitos_atendidos=assessment.requisitos_atendidos or [],
            requisitos_nao_atendidos=(assessment.requisitos_nao_atendidos or []),
            requisitos_nao_comprovados=(assessment.requisitos_nao_comprovados or []),
            dados_estruturados=assessment.dados_estruturados or {},
            classificado_em=assessment.classificado_em,
            numero_controle_pncp=contracting.numero_controle_pncp,
            orgao_razao_social=contracting.orgao_razao_social,
            uf=contracting.uf,
            municipio=contracting.municipio,
            data_publicacao_pncp=contracting.data_publicacao_pncp,
            objeto_compra=contracting.objeto_compra,
            link_sistema_origem=contracting.link_sistema_origem,
            itens=[
                PNCPOpportunityItemResponse(
                    numero_item=item.numero_item,
                    descricao=item.descricao,
                    quantidade=(
                        float(item.quantidade) if item.quantidade is not None else None
                    ),
                    unidade_medida=item.unidade_medida,
                )
                for item in contracting.items
                if cls_has_projector(item.descricao)
            ],
            documentos=[
                PNCPOpportunityDocumentResponse(
                    sequencial_documento=document.sequencial_documento,
                    titulo=document.titulo,
                    tipo_documento_nome=document.tipo_documento_nome,
                    url=document.url,
                    uri=document.uri,
                    nome_arquivo=document.nome_arquivo,
                    conteudo_tipo=document.conteudo_tipo,
                    conteudo_tamanho=document.conteudo_tamanho,
                    conteudo_sha256=document.conteudo_sha256,
                    data_publicacao_pncp=document.data_publicacao_pncp,
                    coletado_em=document.criado_em,
                    extracao_status=document.extracao_status,
                    extrator_versao=document.extrator_versao,
                    texto_caracteres=document.texto_caracteres,
                    paginas_extraidas=document.paginas_extraidas,
                    conteudo_analisado_em=document.conteudo_analisado_em,
                )
                for document in contracting.documents
            ],
        )

    def list_processing_runs(
        self, *, limit: int = 100
    ) -> list[PNCPProcessingRunResponse]:
        return [
            PNCPProcessingRunResponse(
                id=run.id,
                tipo=run.tipo,
                status=run.status,
                perfil=run.perfil,
                perfil_versao=run.perfil_versao,
                analisador_versao=run.analisador_versao,
                parametros=run.parametros or {},
                estatisticas=run.estatisticas or {},
                erro=run.erro,
                iniciado_em=run.iniciado_em,
                concluido_em=run.concluido_em,
            )
            for run in self.audit_repository.list_runs(limit=limit)
        ]

    def list_assessment_history(
        self, assessment_id: int
    ) -> list[PNCPOpportunityHistoryResponse]:
        return [
            PNCPOpportunityHistoryResponse(
                id=history.id,
                assessment_id=history.assessment_id,
                contracting_id=history.contracting_id,
                execucao_id=history.execucao_id,
                perfil=history.perfil,
                perfil_versao=history.perfil_versao,
                analisador_versao=history.analisador_versao,
                classificacao=history.classificacao,
                pontuacao=history.pontuacao,
                adequacao_perfil=history.adequacao_perfil,
                pontuacao_adequacao=history.pontuacao_adequacao,
                snapshot=history.snapshot,
                classificado_em=history.classificado_em,
                criado_em=history.criado_em,
            )
            for history in self.audit_repository.list_assessment_history(assessment_id)
        ]

    @classmethod
    def _technical_assessment(
        cls,
        *,
        structured_item_candidates: list[dict[str, Any]],
        document_analysis: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if document_analysis and document_analysis.get("melhor_item"):
            return document_analysis
        if structured_item_candidates:
            best = max(
                structured_item_candidates,
                key=lambda item: sum(
                    value is not None
                    for key, value in item.items()
                    if key not in {"evidencias", "conflitos"}
                ),
            )
            return {
                "perfil": ProjectorProfileAnalyzer.profile_dict(),
                "origem": "item_pncp",
                "itens_projetor": structured_item_candidates,
                "melhor_item": best,
                "avaliacao": ProjectorProfileAnalyzer.evaluate(best),
            }
        return {}

    @staticmethod
    def _requirement_trace(technical_data: dict[str, Any]) -> list[dict[str, Any]]:
        evaluation = technical_data.get("avaliacao") or {}
        best_item = technical_data.get("melhor_item") or {}
        evidence = best_item.get("evidencias") or {}
        snippets = [
            str(block.get("trecho"))
            for block in evidence.get("blocos", [])
            if block.get("trecho")
        ][:5]
        origin = technical_data.get("origem") or "documento"
        trace: list[dict[str, Any]] = []
        groups = [
            ("ATENDIDO", evaluation.get("requisitos_atendidos", [])),
            ("NAO_ATENDIDO", evaluation.get("requisitos_nao_atendidos", [])),
            ("NAO_COMPROVADO", evaluation.get("requisitos_nao_comprovados", [])),
        ]
        for result, requirements in groups:
            for requirement in requirements:
                trace.append(
                    {
                        "requisito": requirement,
                        "resultado": result,
                        "origem": origin,
                        "numero_item": best_item.get("numero_item"),
                        "trechos": snippets,
                    }
                )
        return trace

    @staticmethod
    def _best_document_analysis(
        analyses: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        if not analyses:
            return None
        return max(
            analyses,
            key=lambda analysis: len(analysis.get("itens_projetor", [])),
        )

    @staticmethod
    def _structured_specifications(
        analysis: dict[str, Any],
    ) -> list[str]:
        item = analysis.get("melhor_item")
        if not item:
            return []
        values: set[str] = set()
        if item.get("modelo_referencia"):
            values.add(str(item["modelo_referencia"]))
        if item.get("tecnologia_projecao"):
            values.add(str(item["tecnologia_projecao"]).lower())
        if item.get("fonte_luz"):
            values.add(str(item["fonte_luz"]).lower())
        if item.get("resolucao_nativa"):
            values.add(str(item["resolucao_nativa"]["texto"]))
        if item.get("luminosidade_lumens"):
            values.add(f"{item['luminosidade_lumens']} lumens")
        for field in [
            "wifi",
            "interativo",
            "curta_distancia",
            "ultracurta_distancia",
        ]:
            if item.get(field) is True:
                values.add(field.replace("_", " "))
        return sorted(values)

    @staticmethod
    def _structured_snippets(analysis: dict[str, Any], content_text: str) -> list[str]:
        blocks = analysis.get("blocos_encontrados", [])
        snippets = [
            re.sub(r"\s+", " ", str(block.get("texto") or "")).strip()[:500]
            for block in blocks[:5]
            if block.get("texto")
        ]
        if snippets:
            return snippets
        return PNCPOpportunityService._snippets(content_text)

    @classmethod
    def _projector_terms(cls, text: str) -> set[str]:
        return {
            name
            for name, pattern in cls.PROJECTOR_PATTERNS.items()
            if pattern.search(text)
        }

    @classmethod
    def _false_positive_terms(cls, text: str) -> set[str]:
        return {
            name
            for name, pattern in cls.FALSE_POSITIVE_PATTERNS.items()
            if pattern.search(text)
        }

    @classmethod
    def _snippets(cls, text: str, radius: int = 220) -> list[str]:
        if not text:
            return []
        normalized = cls._normalize_text(text)
        positions: list[int] = []
        for pattern in cls.PROJECTOR_PATTERNS.values():
            positions.extend(match.start() for match in pattern.finditer(normalized))
        snippets: list[str] = []
        for position in sorted(set(positions))[:5]:
            start = max(0, position - radius)
            end = min(len(text), position + radius)
            snippet = re.sub(r"\s+", " ", text[start:end]).strip()
            if snippet and snippet not in snippets:
                snippets.append(snippet)
        return snippets

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        if not value:
            return ""
        decomposed = unicodedata.normalize("NFKD", str(value).lower())
        return "".join(
            character
            for character in decomposed
            if not unicodedata.combining(character)
        )

    @staticmethod
    def _json_decimal(value: Decimal | None) -> float | None:
        return float(value) if value is not None else None


def cls_has_projector(text: str | None) -> bool:
    normalized = PNCPOpportunityService._normalize_text(text)
    return bool(PNCPOpportunityService._projector_terms(normalized))
