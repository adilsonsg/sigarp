from sqlalchemy.orm import Session

from app.models.pncp_contracting import PNCPContractingRecord
from app.models.pncp_contracting_document import PNCPContractingDocumentRecord
from app.models.pncp_contracting_item import PNCPContractingItemRecord
from app.services.pncp_opportunity_service import PNCPOpportunityService


def contracting(object_text: str) -> PNCPContractingRecord:
    return PNCPContractingRecord(
        id=1,
        numero_controle_pncp="00000000000000-1-000001/2026",
        objeto_compra=object_text,
    )


def test_classifies_confirmed_projector_item() -> None:
    record = contracting("Aquisição de equipamentos de TI")
    record.items = [
        PNCPContractingItemRecord(
            contracting_id=1,
            numero_item=1,
            descricao="Projetor multimídia laser Full HD",
            quantidade=20,
        )
    ]
    result = PNCPOpportunityService.classify_contracting(record)
    assert result.classificacao == "CONFIRMADA_ITEM"
    assert result.pontuacao == 100
    assert "projetor" in result.termos_encontrados


def test_classifies_object_only_as_document_candidate() -> None:
    record = contracting("Aquisição de projetores multimídia e nobreaks")
    record.items = [
        PNCPContractingItemRecord(
            contracting_id=1,
            numero_item=1,
            descricao="Monitor computador",
        )
    ]
    result = PNCPOpportunityService.classify_contracting(record)
    assert result.classificacao == "CANDIDATA_DOCUMENTO"
    assert result.pontuacao == 60


def test_discards_multimedia_false_positive() -> None:
    record = contracting("Aquisição de acessórios de informática")
    record.items = [
        PNCPContractingItemRecord(
            contracting_id=1,
            numero_item=1,
            descricao="Caixa de som para multimídia potência 5W",
        )
    ]
    result = PNCPOpportunityService.classify_contracting(record)
    assert result.classificacao == "DESCARTADA_FALSO_POSITIVO"
    assert result.pontuacao == 0


def test_classify_all_persists_assessment(db_session: Session) -> None:
    record = contracting("Aquisição de projetor interativo")
    record.id = None
    db_session.add(record)
    db_session.commit()

    stats = PNCPOpportunityService(db_session).classify_all()

    assert stats.processadas == 1
    assert stats.candidatas_documento == 1
    opportunities = PNCPOpportunityService(db_session).list_opportunities()
    assert len(opportunities) == 1
    assert opportunities[0].classificacao == "CANDIDATA_DOCUMENTO"
    assert opportunities[0].perfil_versao == "1.0.0"


def test_classifies_extracted_document_as_confirmed() -> None:
    record = contracting("Aquisição de equipamentos de TI")
    record.documents = [
        PNCPContractingDocumentRecord(
            contracting_id=1,
            sequencial_documento=1,
            titulo="Edital",
            extracao_status="SUCESSO",
            texto_extraido=(
                "Projetor multimídia laser Full HD, Wi-Fi, interativo, "
                "ultracurta distância."
            ),
        )
    ]
    result = PNCPOpportunityService.classify_contracting(record)
    assert result.classificacao == "CONFIRMADA_DOCUMENTO"
    assert result.pontuacao >= 85
    assert "projetor" in result.termos_encontrados
    assert "ultracurta distancia" in result.evidencias["especificacoes_documentos"]


def test_document_profile_is_context_aware() -> None:
    record = contracting("Aquisição de projetores")
    record.documents = [
        PNCPContractingDocumentRecord(
            contracting_id=1,
            sequencial_documento=1,
            titulo="Edital",
            extracao_status="SUCESSO",
            texto_extraido=(
                "4.1. IMPRESSORA LASER COM WI-FI E FULL HD\n"
                "4.2. TABELA DE ITENS - ITEM 21: PROJETOR MULTIMÍDIA\n"
                "4.2.1. Tipo de lâmpada UHE. Resolução: 1280 x 800.\n"
                "4.2.2. Modelo de referência: Epson PowerLite E24 ou equivalente.\n"
                "4.3. PRÓXIMO ITEM\n"
                "21\nPROJETOR MULTIMÍDIA\nUND. 15"
            ),
        )
    ]
    result = PNCPOpportunityService.classify_contracting(record)

    assert result.classificacao == "CONFIRMADA_DOCUMENTO"
    assert result.adequacao_perfil == "INCOMPATIVEL"
    assert "fonte_luz_laser" in result.requisitos_nao_atendidos
    assert "full_hd_nativo" in result.requisitos_nao_atendidos
    assert "laser" not in result.evidencias["especificacoes_documentos"]


def test_repository_refreshes_classified_timestamp(db_session: Session) -> None:
    from datetime import UTC, datetime, timedelta

    from app.models.pncp_opportunity_assessment import (
        PNCPOpportunityAssessmentRecord,
    )

    record = contracting("Aquisição de projetor")
    record.id = None
    db_session.add(record)
    db_session.flush()
    old = datetime.now(UTC) - timedelta(days=1)
    assessment = PNCPOpportunityAssessmentRecord(
        contracting_id=record.id,
        perfil="projetores",
        perfil_versao="1.0.0",
        classificacao="CANDIDATA_DOCUMENTO",
        pontuacao=60,
        classificado_em=old,
    )
    db_session.add(assessment)
    db_session.commit()

    PNCPOpportunityService(db_session).classify_all()
    db_session.refresh(assessment)

    refreshed = assessment.classificado_em
    if refreshed.tzinfo is None:
        refreshed = refreshed.replace(tzinfo=UTC)
    assert refreshed > old


def test_filters_opportunities_by_profile_suitability(
    db_session: Session,
) -> None:
    from app.models.pncp_opportunity_assessment import (
        PNCPOpportunityAssessmentRecord,
    )

    record = contracting("Aquisição de projetor")
    record.id = None
    db_session.add(record)
    db_session.flush()
    db_session.add(
        PNCPOpportunityAssessmentRecord(
            contracting_id=record.id,
            perfil="projetores",
            perfil_versao="1.0.0",
            classificacao="CONFIRMADA_DOCUMENTO",
            pontuacao=90,
            adequacao_perfil="INCOMPATIVEL",
            pontuacao_adequacao=33,
        )
    )
    db_session.commit()

    results = PNCPOpportunityService(db_session).list_opportunities(
        adequacao="INCOMPATIVEL"
    )

    assert len(results) == 1
    assert results[0].adequacao_perfil == "INCOMPATIVEL"
    assert results[0].perfil_versao == "1.0.0"


def test_keeps_assessment_history_by_profile_version(
    db_session: Session,
) -> None:
    from app.models.pncp_opportunity_assessment import (
        PNCPOpportunityAssessmentRecord,
    )

    record = contracting("Aquisição de projetor")
    record.id = None
    db_session.add(record)
    db_session.flush()
    db_session.add_all(
        [
            PNCPOpportunityAssessmentRecord(
                contracting_id=record.id,
                perfil="projetores",
                perfil_versao="legacy-alpha5",
                classificacao="CONFIRMADA_DOCUMENTO",
                pontuacao=90,
            ),
            PNCPOpportunityAssessmentRecord(
                contracting_id=record.id,
                perfil="projetores",
                perfil_versao="1.0.0",
                classificacao="CONFIRMADA_DOCUMENTO",
                pontuacao=90,
            ),
        ]
    )
    db_session.commit()

    service = PNCPOpportunityService(db_session)
    current = service.list_opportunities()
    legacy = service.list_opportunities(perfil_versao="legacy-alpha5")

    assert [item.perfil_versao for item in current] == ["1.0.0"]
    assert [item.perfil_versao for item in legacy] == ["legacy-alpha5"]
