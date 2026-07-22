from sqlalchemy.orm import Session

from app.repositories.pncp_opportunity_review_repository import (
    PNCPOpportunityReviewRepository,
)
from app.schemas.pncp_reviews import (
    PNCPOpportunityReviewCreate,
    PNCPOpportunityReviewResponse,
)
from app.security.models import AuthenticatedPrincipal


class PNCPOpportunityReviewService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = PNCPOpportunityReviewRepository(db)

    def review(
        self,
        assessment_id: int,
        payload: PNCPOpportunityReviewCreate,
        principal: AuthenticatedPrincipal,
    ) -> PNCPOpportunityReviewResponse:
        record = self.repository.review(assessment_id, payload, principal)
        self.db.commit()
        self.db.refresh(record)
        return PNCPOpportunityReviewResponse.model_validate(record)

    def list_by_assessment(
        self, assessment_id: int
    ) -> list[PNCPOpportunityReviewResponse]:
        return [
            PNCPOpportunityReviewResponse.model_validate(record)
            for record in self.repository.list_by_assessment(assessment_id)
        ]
