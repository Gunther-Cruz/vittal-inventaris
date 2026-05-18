# VITTAL Inventaris

Sistema web de apoio à decisão para gestão de inventário e manutenção de computadores em instituições públicas de ensino.

## Stack inicial

- Python
- Flask
- PostgreSQL
- Docker
- SQLAlchemy
- Alembic/Flask-Migrate
- Dash/Plotly
- Pandas
- Integração com GLPI

## Arquitetura

O projeto seguirá uma arquitetura de monólito modular em camadas.

Camadas principais:

- controllers
- services
- domain
- repositories
- integrations
- dashboards

## Regra central

O PostgreSQL do VITTAL é a fonte de verdade. O GLPI será integrado posteriormente como sistema operacional auxiliar.