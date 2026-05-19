# Execucao local

Este documento registra os comandos minimos para executar o VITTAL Inventaris em ambiente local.

## Dependencias

Instale as dependencias em um ambiente Python:

```powershell
python -m pip install -r requirements.txt
```

Se estiver usando a `.venv` do projeto:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Banco de dados

O PostgreSQL e a fonte de verdade do VITTAL.

Para execucao local via PowerShell, use `localhost`:

```powershell
$env:DATABASE_URL = "postgresql://vittal:vittal_dev_password@localhost:5432/vittal_inventaris"
```

Dentro do Docker Compose, o host do banco e `postgres`.

## Migrations

Comandos principais:

```powershell
python -m flask --app app:create_app db current
python -m flask --app app:create_app db upgrade
python -m flask --app app:create_app db check
```

Para criar uma nova migration depois de alterar models:

```powershell
python -m flask --app app:create_app db migrate -m "descricao da migration"
```

Nao gere migrations de entidades ainda nao validadas pelo DER Revisado.

## Aplicacao

Execute a aplicacao:

```powershell
python run.py
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/health
```

Tela de login:

```text
http://127.0.0.1:5000/auth/login
```

## Primeiro coordenador

Depois de aplicar a migration da tabela `usuario`, crie o primeiro coordenador de desenvolvimento:

```powershell
python -m flask --app app:create_app auth criar-coordenador-inicial
```

Credenciais iniciais de desenvolvimento:

- email: `coordenador.inicial@ifrs.edu.br`
- senha: `SenhaCoordenador123!`

Essas credenciais sao apenas para desenvolvimento e devem ser trocadas/removidas antes de qualquer uso real.

## Criacao de usuarios

Depois de entrar como coordenador, acesse:

```text
http://127.0.0.1:5000/usuarios/novo
```

Somente usuarios com perfil `COORDENADOR` podem criar usuarios pela interface web.

Perfis persistidos validos:

- `PROFESSOR`
- `TECNICO`
- `COORDENADOR`

Aluno nao deve ser criado como usuario persistido do sistema.

## Testes

```powershell
python -m compileall app run.py tests
python -m unittest discover -v
python -m flask --app app:create_app db check
```
