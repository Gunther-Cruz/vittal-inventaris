# Execucao local

Este documento registra os comandos minimos para executar o bootstrap Flask do VITTAL Inventaris e preparar migrations futuras.

## Dependencias

Instale as dependencias em um ambiente Python:

```powershell
python -m pip install -r requirements.txt
```

## Aplicacao

Execute a aplicacao:

```powershell
python run.py
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/health
```

## Banco de dados

Configure `DATABASE_URL` para apontar para o PostgreSQL do VITTAL.

Exemplo local:

```powershell
$env:FLASK_APP = "app:create_app"
$env:DATABASE_URL = "postgresql://vittal:vittal_dev_password@localhost:5432/vittal_inventaris"
```

## Migrations futuras

Comandos para migrations:

```powershell
flask db init
flask db migrate -m "initial migration"
flask db upgrade
```

Use `python -m flask` se o executavel `flask` nao estiver no PATH:

```powershell
python -m flask --app app:create_app db init
python -m flask --app app:create_app db migrate -m "create usuario table"
python -m flask --app app:create_app db upgrade
```

## Primeiro usuario

Depois de aplicar a migration da tabela `usuario`, crie o primeiro coordenador de desenvolvimento:

```powershell
python -m flask --app app:create_app auth criar-coordenador-inicial
```

Credenciais iniciais de desenvolvimento:

- email: `coordenador.inicial@ifrs.edu.br`
- senha: `SenhaCoordenador123!`

Tambem e possivel criar um usuario informando os dados manualmente pela CLI:

```powershell
python -m flask --app app:create_app auth criar-usuario
```

O comando solicita nome, email, perfil e senha. Os perfis persistidos validos sao:

- `PROFESSOR`
- `TECNICO`
- `COORDENADOR`

Aluno nao deve ser criado como usuario persistido do sistema.

## Fluxo web de usuarios

Depois de entrar como coordenador, acesse:

```text
http://127.0.0.1:5000/usuarios/novo
```

Somente usuarios com perfil `COORDENADOR` podem criar usuarios pela interface web.
