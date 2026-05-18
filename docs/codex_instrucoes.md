# Instrucoes para o Codex - VITTAL Inventaris

## Contexto

O VITTAL Inventaris e um sistema web de apoio a decisao para gestao de inventario e manutencao de computadores em instituicoes publicas de ensino.

A arquitetura definida e um monolito modular em camadas.

O projeto nao deve ser tratado como um helpdesk generico. Ele precisa atender ao contexto institucional do campus, com organizacao por laboratorio, historico de ativos, relatorios por laboratorio e modelo, e dashboards voltados a tomada de decisao.

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
- GLPI via camada de integracao

## Regras obrigatorias

1. Nao criar microservicos.
2. Nao usar React nesta fase inicial.
3. PostgreSQL e a fonte de verdade.
4. GLPI e apenas subsistema integrado.
5. Salvar primeiro no PostgreSQL e sincronizar depois com GLPI.
6. Integracao com GLPI deve ficar somente em `app/integrations/`.
7. Controllers nao devem conter regra de negocio pesada.
8. Services executam casos de uso.
9. Repositories isolam persistencia.
10. Domain, models e enums representam o dominio.
11. Nao chamar API do GLPI diretamente em controllers.
12. Nao alterar a arquitetura sem explicar antes.
13. Antes de modificar arquivos, apresentar plano curto de alteracao.
14. Depois de modificar arquivos, apresentar resumo, comandos de teste e sugestao de commit.
15. Nao criar campos, entidades ou relacionamentos fora das fontes tecnicas sem explicar antes.
16. Nao tratar o GLPI como banco principal ou origem principal de edicao.
17. Nao persistir aluno como usuario do sistema na versao atual.
18. Nao trocar `controllers/` por `routes/` na organizacao arquitetural principal.

## Decisoes consolidadas do projeto

### Sistema principal

O VITTAL e o sistema principal da solucao.

Ele concentra:

- interface;
- regras de negocio;
- autenticacao;
- historicos;
- dashboards;
- indicadores;
- organizacao institucional dos dados.

### Banco principal

O PostgreSQL do VITTAL e a fonte de verdade.

Tudo que for central para o dominio deve existir primeiro no banco do VITTAL, mesmo quando houver sincronizacao com o GLPI.

### GLPI

O GLPI sera utilizado como subsistema auxiliar de apoio para:

- inventario tecnico;
- chamados.

A integracao deve ser encapsulada por adaptador proprio, com client, mapper e adapter.

### Regras de dominio importantes

- Laboratorio e fixo.
- Estacao de trabalho e fixa dentro do laboratorio.
- Gabinete e monitor sao ativos separados.
- Gabinete e monitor podem mudar de estacao e precisam de historico.
- Chamado e um conceito unico com escopos diferentes: estacao e laboratorio.
- O tipo de problema entra na ordem de servico, nao no chamado inicial.
- Historico e requisito central do projeto.
- O sistema nao e de monitoramento em tempo real.

## Fluxo de trabalho esperado

Cada tarefa deve ter escopo pequeno e criterios de aceite claros.

O Codex deve evitar alteracoes fora do pedido.

O Codex deve preferir implementacoes incrementais que preservem a arquitetura ja aprovada.

## Fontes tecnicas obrigatorias

Antes de criar models, migrations, services, repositories ou endpoints, o Codex deve consultar os documentos em `docs/`:

- `docs/arquitetura.md`
- `docs/modelo-relacional.md`
- `docs/diagrama-classes.md`
- `docs/casos-uso.md`
- `docs/decisoes-glpi.md`
- `docs/contratos-json.md`

## Hierarquia das fontes

- O DER Revisado e a fonte principal para nomes de tabelas, campos, chaves e relacionamentos.
- O Diagrama de Classes e a fonte principal para organizacao do dominio, responsabilidades, enums e services.
- Os Casos de Uso sao a fonte principal para ordem dos fluxos funcionais e comportamento dos atores.
- A Arquitetura e a fonte principal para organizacao em camadas, papel de cada modulo e decisao de persistencia e sincronizacao.

## Estrutura arquitetural esperada

O projeto deve caminhar para uma estrutura parecida com esta:

```text
app/
  __init__.py
  controllers/
  services/
  domain/
    models/
    enums.py
  repositories/
  integrations/
  dashboards/
  templates/
  static/
  config/
migrations/
tests/
run.py
```

## Orientacao para bootstrap inicial

As tarefas 3 e 3.1 devem preparar a base da aplicacao sem inventar funcionalidade fora de escopo.

### Tarefa 3

Objetivo:

- criar o bootstrap Flask alinhado a arquitetura aprovada.

Entregas esperadas:

- `app/__init__.py` com app factory;
- estrutura inicial de pastas em camadas;
- configuracao central minima;
- registro inicial de blueprint ou controller simples;
- endpoint de health check;
- `run.py` ou ponto de entrada equivalente;
- base pronta para depois conectar SQLAlchemy e migrations.

### Tarefa 3.1

Objetivo:

- refinar o bootstrap para deixar a base pronta para crescimento controlado.

Entregas esperadas:

- placeholders ou arquivos-base coerentes para `controllers`, `services`, `repositories`, `integrations` e `domain`;
- organizacao clara de configuracao;
- dependencias basicas definidas;
- documentacao curta de execucao local, se necessario.

## Comportamento esperado do Codex

Ao executar tarefas neste projeto, o Codex deve:

1. ler primeiro os documentos tecnicos;
2. explicar rapidamente o plano;
3. implementar apenas o que foi pedido;
4. validar a coerencia com arquitetura, DER, classes e casos de uso;
5. informar como testar;
6. sugerir mensagem de commit.

Se houver duvida entre uma ideia nova e o material do projeto, o Codex deve priorizar os documentos tecnicos e explicar a divergencia antes de seguir.
