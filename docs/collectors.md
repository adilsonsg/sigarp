# Arquitetura de coletores

O módulo `app.collectors` padroniza o consumo de fontes oficiais externas.

## Componentes

- `BaseCollector`: contrato abstrato comum.
- `CollectorRegistry`: registro e resolução de coletores por nome.
- `PNCPClient`: cliente HTTP assíncrono para a API oficial PNCP Consulta.
- `PNCPCollector`: fachada do coletor PNCP.
- `exceptions.py`: erros de domínio para timeout, limite de requisições e respostas remotas.

## Configuração

As variáveis abaixo podem ser definidas no `.env`:

```env
PNCP_BASE_URL=https://pncp.gov.br/api/consulta
PNCP_TIMEOUT_SECONDS=30
PNCP_MAX_RETRIES=4
PNCP_BACKOFF_SECONDS=1
PNCP_USER_AGENT=SIGARP/0.3 (IFMT)
```

`PNCP_MAX_RETRIES` representa repetições após a tentativa inicial. Com o valor 4,
o cliente pode executar até cinco tentativas. O intervalo usa backoff exponencial.

## Uso interno

```python
from app.collectors import collector_registry
from app.collectors.pncp.endpoints import ATAS_BY_VALIDITY

collector = collector_registry.get("pncp")
resultado = await collector.collect(
    endpoint=ATAS_BY_VALIDITY,
    params={
        "dataInicial": "20260701",
        "dataFinal": "20260720",
        "pagina": 1,
    },
)
```

A definição dos filtros de negócio, normalização e persistência será adicionada nas
próximas etapas da Sprint 3.
