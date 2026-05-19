# VITTAL Inventaris

Sistema web de apoio a decisao para gestao de inventario e manutencao de computadores em instituicoes publicas de ensino, com foco inicial no Pavilhao 10 do IFRS.

## Stack

- Python
- Flask
- PostgreSQL
- Docker
- SQLAlchemy
- Alembic/Flask-Migrate
- Flask Templates, HTML, CSS e JavaScript
- Dash/Plotly e Pandas em etapa futura
- Integracao futura com GLPI via camada isolada

## Arquitetura

O projeto segue uma arquitetura de monolito modular em camadas.

Camadas principais:

- `controllers`
- `services`
- `domain`
- `repositories`
- `integrations`
- `dashboards`
- `config`

## Regra central

O PostgreSQL do VITTAL e a fonte de verdade. O GLPI sera integrado posteriormente como subsistema auxiliar.

O fluxo correto para dados do dominio e salvar primeiro no PostgreSQL e sincronizar depois com o GLPI, quando essa integracao existir.

## Estado atual

Ja existem:

- bootstrap Flask com app factory;
- health check em `/health`;
- configuracao central;
- SQLAlchemy e Flask-Migrate;
- migration real da tabela `usuario`;
- autenticacao por sessao com Flask-Login;
- protecao CSRF com Flask-WTF;
- controle de acesso por perfil;
- criacao do primeiro coordenador por CLI;
- criacao web de usuarios por coordenador;
- testes automatizados para autenticacao, usuarios e permissionamento.

## Execucao local

Crie ou atualize o ambiente Python e instale as dependencias:

```powershell
python -m pip install -r requirements.txt
```

Para comandos locais fora do Docker, configure o banco em `localhost`:

```powershell
$env:DATABASE_URL = "postgresql://vittal:vittal_dev_password@localhost:5432/vittal_inventaris"
```

Execute a aplicacao:

```powershell
python run.py
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/health
```

## Primeiro coordenador

Depois de aplicar as migrations, crie o coordenador inicial de desenvolvimento:

```powershell
python -m flask --app app:create_app auth criar-coordenador-inicial
```

Credenciais de desenvolvimento:

- email: `coordenador.inicial@ifrs.edu.br`
- senha: `SenhaCoordenador123!`

Essas credenciais devem ser trocadas/removidas antes de qualquer uso real.

## Testes

```powershell
python -m compileall app run.py tests
python -m unittest discover -v
python -m flask --app app:create_app db check
```
