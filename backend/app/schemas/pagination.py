from pydantic import BaseModel, Field


class Page[ItemT](BaseModel):
    items: list[ItemT]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)
