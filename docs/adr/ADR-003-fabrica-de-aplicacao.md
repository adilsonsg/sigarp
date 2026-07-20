# ADR-003 — Fábrica de aplicação FastAPI

## Status

Aceito.

## Contexto

A inicialização concentrada em um módulo dificulta testes e evolução.

## Decisão

A aplicação será criada por `create_app()`, responsável por registrar
middleware, handlers e rotas.

## Consequências

- Inicialização testável.
- Registro centralizado de componentes.
- Preparação para configurações por ambiente.
