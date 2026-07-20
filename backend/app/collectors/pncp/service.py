from app.collectors.pncp.client import PNCPClient
from app.collectors.pncp.endpoints import CONTRACTING_BY_PUBLICATION
from app.collectors.pncp.parser import filter_contractings, parse_contracting_page
from app.collectors.pncp.schemas import PNCPSearchRequest, PNCPSearchResponse


class PNCPSearchService:
    def __init__(self, client: PNCPClient | None = None) -> None:
        self._client = client

    async def search_contractings(
        self, request: PNCPSearchRequest
    ) -> PNCPSearchResponse:
        params: dict[str, str | int] = {
            "dataInicial": request.data_inicial.strftime("%Y%m%d"),
            "dataFinal": request.data_final.strftime("%Y%m%d"),
            "codigoModalidadeContratacao": request.codigo_modalidade_contratacao,
            "pagina": request.pagina,
        }
        if request.uf:
            params["uf"] = request.uf

        owns_client = self._client is None
        client = self._client or PNCPClient()
        try:
            payload = await client.buscar_contratacoes_publicadas(
                data_inicial=request.data_inicial,
                data_final=request.data_final,
                codigo_modalidade_contratacao=(request.codigo_modalidade_contratacao),
                pagina=request.pagina,
                uf=request.uf,
            )
        finally:
            if owns_client:
                await client.close()

        page = parse_contracting_page(payload)
        items = filter_contractings(
            page.data,
            keyword=request.palavra_chave,
            only_srp=request.somente_srp,
        )

        return PNCPSearchResponse(
            endpoint=CONTRACTING_BY_PUBLICATION,
            parametros=params,
            total_registros_fonte=page.total_registros,
            total_paginas_fonte=page.total_paginas,
            pagina_fonte=page.numero_pagina,
            total_itens_retornados=len(items),
            filtro_local_aplicado=bool(request.palavra_chave or request.somente_srp),
            itens=items,
        )
