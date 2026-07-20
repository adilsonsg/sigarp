import unicodedata
from collections.abc import Iterable
from typing import Any

from app.collectors.exceptions import RemoteAPIError
from app.collectors.pncp.schemas import PNCPContracting, PNCPPage


def parse_contracting_page(payload: Any) -> PNCPPage:
    if not isinstance(payload, dict):
        raise RemoteAPIError("PNCP returned an unexpected response structure.")
    return PNCPPage.model_validate(payload)


def filter_contractings(
    items: Iterable[PNCPContracting],
    *,
    keyword: str | None = None,
    only_srp: bool = False,
) -> list[PNCPContracting]:
    normalized_keyword = _normalize(keyword) if keyword else None
    result: list[PNCPContracting] = []

    for item in items:
        if only_srp and item.srp is not True:
            continue

        if normalized_keyword:
            searchable_text = " ".join(
                filter(
                    None,
                    [
                        item.objeto_compra,
                        item.informacao_complementar,
                        item.numero_compra,
                        item.processo,
                    ],
                )
            )
            normalized_text = _normalize(searchable_text)
            if not all(term in normalized_text for term in normalized_keyword.split()):
                continue

        result.append(item)

    return result


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return " ".join(without_accents.casefold().split())
