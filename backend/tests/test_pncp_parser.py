import pytest

from app.collectors.exceptions import RemoteAPIError
from app.collectors.pncp.parser import filter_contractings, parse_contracting_page


def sample_payload() -> dict:
    return {
        "data": [
            {
                "numeroControlePNCP": "12345678000100-1-000001/2026",
                "numeroCompra": "1/2026",
                "anoCompra": 2026,
                "sequencialCompra": 1,
                "objetoCompra": "Aquisição de projetor multimídia",
                "informacaoComplementar": "Tecnologia laser e resolução Full HD",
                "srp": True,
                "modalidadeId": 6,
                "modalidadeNome": "Pregão - Eletrônico",
                "orgaoEntidade": {
                    "cnpj": "12345678000100",
                    "razaoSocial": "Instituto Federal de Teste",
                },
                "unidadeOrgao": {"ufSigla": "MT", "municipioNome": "Cuiabá"},
            },
            {
                "numeroControlePNCP": "12345678000100-1-000002/2026",
                "objetoCompra": "Aquisição de notebooks",
                "srp": False,
            },
        ],
        "totalRegistros": 2,
        "totalPaginas": 1,
        "numeroPagina": 1,
        "paginasRestantes": 0,
        "empty": False,
    }


def test_parser_maps_official_camel_case_fields() -> None:
    page = parse_contracting_page(sample_payload())

    assert page.total_registros == 2
    assert page.data[0].objeto_compra == "Aquisição de projetor multimídia"
    assert page.data[0].orgao_entidade is not None
    assert page.data[0].orgao_entidade.razao_social == "Instituto Federal de Teste"


def test_filter_is_accent_insensitive_and_can_limit_to_srp() -> None:
    page = parse_contracting_page(sample_payload())

    result = filter_contractings(page.data, keyword="aquisicao projetor", only_srp=True)

    assert len(result) == 1
    assert result[0].srp is True


def test_parser_rejects_unexpected_payload() -> None:
    with pytest.raises(RemoteAPIError):
        parse_contracting_page([{"data": []}])
