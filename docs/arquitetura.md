# Arquitetura do VITTAL Inventaris

O VITTAL Inventaris segue uma arquitetura de monolito modular em camadas.

O sistema sera implementado como uma aplicacao web Flask, com PostgreSQL como fonte de verdade para os dados do dominio. O GLPI sera tratado apenas como subsistema integrado de apoio, sem assumir o papel de base principal do VITTAL.

## Objetivo arquitetural

O VITTAL nao e apenas um cadastro de computadores e tambem nao e apenas uma interface para abertura de chamados.

O sistema deve:

- centralizar o inventario tecnico e institucional dos ativos;
- registrar ocorrencias e fluxo de manutencao;
- manter historico por ativo, estacao e laboratorio;
- permitir analise por laboratorio, modelo, tipo de problema e periodo;
- apoiar a tomada de decisao da equipe de TI.

Por isso, a arquitetura precisa ser simples o bastante para o escopo do TCC e solida o bastante para ser defendida tecnicamente.

## Principios obrigatorios

- O sistema nao sera dividido em microservicos nesta fase.
- O Flask sera o framework principal da aplicacao web.
- A interface inicial sera feita com Flask Templates, HTML, CSS e JavaScript.
- O PostgreSQL sera a fonte de verdade do sistema.
- O GLPI sera um subsistema auxiliar integrado.
- A aplicacao deve salvar primeiro no PostgreSQL e sincronizar depois com o GLPI.
- Falhas em integracoes externas nao devem impedir o funcionamento central do VITTAL.
- Controllers nao devem conter regra de negocio pesada.
- Services executam os casos de uso.
- Repositories isolam o acesso ao banco de dados.
- Models e enums representam o dominio e a persistencia.
- Dashboards devem consumir dados do PostgreSQL do VITTAL, nao diretamente do GLPI.

## Decisoes centrais

### VITTAL como sistema principal

O VITTAL e a camada principal da solucao. Ele concentra:

- interface;
- autenticacao;
- regras de negocio;
- organizacao institucional dos dados;
- historicos;
- dashboards;
- relatorios;
- indicadores.

O GLPI nao substitui o VITTAL. Ele apenas apoia operacoes de inventario tecnico e chamados quando essa integracao fizer sentido.

### PostgreSQL como fonte de verdade

O PostgreSQL do VITTAL guarda os dados principais do dominio. Mesmo quando houver sincronizacao com o GLPI, os registros oficiais do sistema devem existir e ser consultados a partir do banco do VITTAL.

### GLPI como integracao encapsulada

A integracao com GLPI deve ficar isolada em `app/integrations/` e ser organizada, no minimo, com os seguintes papeis:

- `glpi_client.py`: autenticacao e chamadas HTTP para a API;
- `glpi_mapper.py`: traducao entre o dominio do VITTAL e o formato esperado pelo GLPI;
- `glpi_adapter.py`: interface interna usada pelos services do sistema.

Controllers, dominio e repositories nao devem conhecer detalhes da API do GLPI.

## Camadas previstas

### Controllers

Camada responsavel por:

- receber requisicoes HTTP;
- validar entradas simples;
- chamar services;
- retornar respostas.

Controllers nao devem conter:

- regra de negocio complexa;
- acesso direto ao banco;
- chamadas diretas ao GLPI.

### Services

Camada responsavel pela execucao dos casos de uso.

Services coordenam:

- validacoes de negocio;
- transacoes;
- repositories;
- historicos;
- integracoes externas quando necessario.

Services previstos como referencia arquitetural:

- `AuthService`
- `InventarioService`
- `ChamadoService`
- `OrdemServicoService`
- `ManutencaoService`
- `DashboardService`
- `GlpiAdapter`

### Domain

Camada responsavel por representar os conceitos do sistema.

Ela deve conter:

- models;
- enums;
- estruturas de apoio do dominio.

O dominio nao deve depender de Flask, Dash ou GLPI.

### Repositories

Camada responsavel por isolar o acesso ao PostgreSQL.

Repositories devem concentrar:

- consultas;
- persistencia;
- operacoes especificas de banco;
- uso do ORM.

Services nao devem depender de SQL bruto ou de detalhes de driver.

### Integrations

Camada responsavel por integracoes externas.

Toda integracao com GLPI deve ficar isolada em `app/integrations/`.

### Dashboards

Camada prevista para recursos analiticos com Dash, Plotly e Pandas.

Essa camada deve transformar dados persistidos em informacao gerencial.

## Estrutura sugerida de diretorios

Uma estrutura compativel com a arquitetura aprovada e:

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

## Regra central de persistencia e sincronizacao

O fluxo correto para dados do dominio e:

1. Receber e validar os dados no VITTAL.
2. Persistir os dados no PostgreSQL.
3. Registrar o estado de sincronizacao quando aplicavel.
4. Sincronizar posteriormente com o GLPI por meio da camada de integracao.

O GLPI nao deve ser requisito para que o PostgreSQL funcione, nem para que o VITTAL execute seus fluxos principais.

## Implicacoes para as proximas tarefas

Na fase inicial do backend:

- o bootstrap Flask deve nascer alinhado a essa estrutura em camadas;
- a pasta correta e `controllers/`, nao `routes/`;
- o projeto deve preparar `app factory`, configuracao central e endpoint simples de health check;
- a integracao com banco e GLPI vem depois do bootstrap, sem quebrar a organizacao arquitetural aprovada.
