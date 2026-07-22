from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.pncp_contracting import PNCPContractingRecord
from app.models.pncp_opportunity_assessment import (
    PNCPOpportunityAssessmentRecord,
)


def create_assessment(db_session: Session) -> PNCPOpportunityAssessmentRecord:
    contracting = PNCPContractingRecord(
        numero_controle_pncp="00000000000000-1-000001/2026",
        objeto_compra="Aquisição de projetores",
    )
    db_session.add(contracting)
    db_session.flush()
    assessment = PNCPOpportunityAssessmentRecord(
        contracting_id=contracting.id,
        perfil="projetores",
        perfil_versao="1.0.0",
        analisador_versao="1.0.0",
        classificacao="CONFIRMADA_DOCUMENTO",
        pontuacao=90,
    )
    db_session.add(assessment)
    db_session.commit()
    return assessment


def test_reader_cannot_review_opportunity(
    unauthenticated_client: TestClient,
    db_session: Session,
    role_headers: dict[str, dict[str, str]],
) -> None:
    assessment = create_assessment(db_session)
    response = unauthenticated_client.patch(
        f"/pncp/oportunidades/{assessment.id}/revisao",
        json={"decisao": "APROVADA", "justificativa": "Conferência documental."},
        headers=role_headers["leitor"],
    )
    assert response.status_code == 403


def test_analyst_review_records_actor_justification_and_before_after(
    unauthenticated_client: TestClient,
    db_session: Session,
    role_headers: dict[str, dict[str, str]],
) -> None:
    assessment = create_assessment(db_session)
    response = unauthenticated_client.patch(
        f"/pncp/oportunidades/{assessment.id}/revisao",
        json={
            "decisao": "APROVADA",
            "justificativa": "Documento e requisitos conferidos manualmente.",
        },
        headers=role_headers["analista"],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["actor_subject"] == "analyst@ifmt.test"
    assert body["actor_role"] == "analista"
    assert body["execucao_id"] is None
    assert body["resultado_avaliado"]["classificacao"] == ("CONFIRMADA_DOCUMENTO")
    assert body["resultado_avaliado"]["perfil_versao"] == "1.0.0"
    assert body["valor_anterior"]["revisao_status"] is None
    assert body["valor_novo"]["revisao_status"] == "APROVADA"

    db_session.refresh(assessment)
    assert assessment.revisao_status == "APROVADA"
    assert assessment.revisado_por == "analyst@ifmt.test"
    assert assessment.revisado_em is not None


def test_repeated_review_preserves_immutable_history(
    unauthenticated_client: TestClient,
    db_session: Session,
    role_headers: dict[str, dict[str, str]],
) -> None:
    assessment = create_assessment(db_session)
    url = f"/pncp/oportunidades/{assessment.id}/revisao"
    first = unauthenticated_client.patch(
        url,
        json={
            "decisao": "EXIGE_ANALISE_ADICIONAL",
            "justificativa": "É necessário conferir a resolução nativa.",
        },
        headers=role_headers["analista"],
    )
    second = unauthenticated_client.patch(
        url,
        json={
            "decisao": "REJEITADA",
            "justificativa": "A resolução nativa não atende ao perfil vigente.",
        },
        headers=role_headers["administrador"],
    )
    history = unauthenticated_client.get(
        f"/pncp/oportunidades/{assessment.id}/revisoes",
        headers=role_headers["leitor"],
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert history.status_code == 200
    records = history.json()
    assert len(records) == 2
    assert records[0]["decisao"] == "REJEITADA"
    assert records[0]["valor_anterior"]["revisao_status"] == ("EXIGE_ANALISE_ADICIONAL")
    assert records[1]["decisao"] == "EXIGE_ANALISE_ADICIONAL"


def test_review_justification_is_required(
    unauthenticated_client: TestClient,
    db_session: Session,
    role_headers: dict[str, dict[str, str]],
) -> None:
    assessment = create_assessment(db_session)
    response = unauthenticated_client.patch(
        f"/pncp/oportunidades/{assessment.id}/revisao",
        json={"decisao": "APROVADA", "justificativa": "curta"},
        headers=role_headers["analista"],
    )
    assert response.status_code == 422
