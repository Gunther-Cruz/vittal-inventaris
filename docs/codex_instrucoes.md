# Instruções para o Codex — VITTAL Inventaris

## Contexto

O VITTAL Inventaris é um sistema web de apoio à decisão para gestão de inventário e manutenção de computadores em instituições públicas de ensino.

A arquitetura definida é um monólito modular em camadas.

## Stack

- Python
- Flask
- PostgreSQL
- Docker
- SQLAlchemy
- Alembic/Flask-Migrate
- Flask Templates
- Dash/Plotly
- Pandas
- GLPI via camada de integração

## Regras obrigatórias

1. Não criar microserviços.
2. Não usar React nesta fase inicial.
3. PostgreSQL é a fonte de verdade.
4. GLPI é apenas subsistema integrado.
5. Salvar primeiro no PostgreSQL e sincronizar depois com GLPI.
6. Integração com GLPI deve ficar somente em app/integrations/.
7. Controllers não devem conter regra de negócio pesada.
8. Services executam casos de uso.
9. Repositories isolam persistência.
10. Domain/models/enums representam o domínio.
11. Não chamar API do GLPI diretamente em controllers.
12. Não alterar a arquitetura sem explicar antes.
13. Antes de modificar arquivos, apresentar plano curto de alteração.
14. Depois de modificar arquivos, apresentar resumo, comandos de teste e sugestão de commit.

## Fluxo de trabalho

Cada tarefa deve ter escopo pequeno e critérios de aceite claros.

O Codex deve evitar alterações fora do pedido.