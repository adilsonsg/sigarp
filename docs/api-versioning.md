# Versionamento e compatibilidade da API

## Contrato canônico

A API pública canônica do SIGARP usa o prefixo `/api/v1`. O número no caminho
representa a versão principal do contrato HTTP, não a versão da aplicação.
`/health`, `/docs` e `/openapi.json` permanecem disponíveis sem autenticação para
operação e descoberta; `/api/v1/health` oferece o equivalente versionado.

As rotas sem prefixo existentes antes da `0.9.0-alpha1` permanecem ativas para
compatibilidade, mas são marcadas como depreciadas no OpenAPI. Novos
consumidores devem usar somente `/api/v1`.

## Paginação

Coleções persistidas localmente aceitam:

- `page`: página iniciada em 1;
- `page_size`: tamanho entre 1 e 200.

O corpo de resposta contém:

```json
{
  "items": [],
  "page": 1,
  "page_size": 50,
  "total": 0,
  "total_pages": 0
}
```

Consultas diretas à fonte PNCP preservam os metadados de paginação da própria
fonte, identificados pelos campos com sufixo `_fonte`.

## Erros

Erros HTTP usam o mesmo envelope:

```json
{
  "detail": "Dados de entrada inválidos.",
  "code": "validation_error",
  "request_id": "identificador-da-requisicao",
  "errors": [
    {
      "loc": ["query", "page"],
      "message": "Input should be greater than or equal to 1",
      "type": "greater_than_equal"
    }
  ]
}
```

O cabeçalho `X-Request-ID` contém o mesmo identificador de `request_id`. A lista
`errors` fica vazia quando não há detalhes por campo.

## Compatibilidade

São compatíveis dentro da v1:

- inclusão de endpoint;
- inclusão de campo de resposta opcional;
- inclusão de valor em enumeração documentada como extensível;
- correção que não altera o significado de campos existentes.

Exigem nova versão principal do caminho:

- remoção ou renomeação de endpoint ou campo;
- alteração de tipo, obrigatoriedade ou semântica;
- mudança de autenticação ou autorização que quebre consumidores existentes;
- alteração incompatível de paginação ou envelope de erro.

## Depreciação

Uma depreciação deve:

1. aparecer no OpenAPI e no changelog;
2. indicar a alternativa suportada;
3. permanecer disponível por pelo menos duas versões publicadas e 90 dias,
   prevalecendo o período mais longo;
4. ser removida apenas em uma nova versão principal da API.

Exceções por vulnerabilidade crítica exigem registro no `SECURITY.md`, nota de
release e justificativa da remoção antecipada.
