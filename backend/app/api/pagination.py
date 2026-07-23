from math import ceil

from app.schemas.pagination import Page


def create_page[ItemT](
    items: list[ItemT],
    *,
    page: int,
    page_size: int,
    total: int,
) -> Page[ItemT]:
    return Page[ItemT](
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=ceil(total / page_size) if total else 0,
    )
