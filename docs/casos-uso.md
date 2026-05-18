# Casos de Uso

Os Casos de Uso orientam os fluxos funcionais do VITTAL Inventaris.

Este documento registra que a ordem de implementacao das funcionalidades deve ser guiada pelos casos de uso definidos nos documentos tecnicos do projeto.

## Papel dos casos de uso

Os Casos de Uso orientam:

- fluxos funcionais;
- ordem de implementacao;
- atores;
- permissoes;
- entradas e saidas esperadas;
- principais interacoes do sistema;
- comportamento esperado em cenarios de sucesso e falha.

## Atores principais

O projeto consolida quatro atores:

- `Aluno`
- `Professor`
- `Tecnico`
- `Coordenador`

## Regras gerais de atores

### Aluno

Ator de uso publico e simplificado.

Papel esperado:

- visualizar estado basico das estacoes;
- registrar chamado;
- nao atuar como usuario autenticado persistido.

### Professor

Ator autenticado com visao ampliada do contexto laboratorial.

Papel esperado:

- registrar chamado;
- visualizar estado dos laboratorios;
- acompanhar contexto dos chamados do laboratorio;
- acessar relatorios e dashboards compativeis com seu perfil.

### Tecnico

Ator operacional central do sistema.

Papel esperado:

- gerenciar chamados;
- abrir e conduzir ordens de servico;
- registrar manutencao;
- gerenciar inventario;
- movimentar ativos;
- manter coerencia entre estado real e estado registrado.

### Coordenador

Ator gerencial voltado a analise e apoio a decisao.

Papel esperado:

- consultar inventario;
- acompanhar manutencoes;
- visualizar relatorios;
- visualizar dashboards e indicadores.

## Regras funcionais importantes

### Camada publica minima

O sistema deve permitir uma visualizacao basica do estado dos laboratorios e estacoes sem exigir autenticacao forte para tudo.

Essa camada publica existe para facilitar consulta simples e registro de ocorrencias.

### Chamado como conceito unico

O projeto nao deve criar dois conceitos totalmente separados para chamado de estacao e chamado de laboratorio.

Existe um unico caso de uso de registrar chamado, com diferenca de contexto:

- chamado de estacao;
- chamado de laboratorio.

### Professor com relevancia institucional

O chamado aberto por professor pode receber tratamento de prioridade superior conforme a regra de negocio aprovada.

### Tecnico como principal agente de atualizacao

A maior parte das alteracoes estruturais e operacionais deve passar pelo tecnico.

### Coordenador como usuario analitico

O coordenador nao e o foco da manutencao operacional. Seu papel esta mais ligado a leitura gerencial dos dados.

## Nucleos funcionais do sistema

Os casos de uso consolidados apontam para estes nucleos:

- autenticacao;
- registrar chamado;
- consultar status;
- visualizar estado dos equipamentos;
- gerenciar chamados;
- gerenciar inventario;
- registrar manutencao;
- mover equipamento;
- visualizar historico;
- gerar relatorios;
- visualizar dashboards.

## Regras de implementacao

- Controllers devem apenas coordenar entrada e saida das requisicoes.
- Services devem executar os casos de uso.
- Repositories devem ser usados pelos services para persistencia e consulta de dados.
- Integracoes externas, incluindo GLPI, devem ser acionadas por meio da camada de integracao, nunca diretamente pelos controllers.

## Ordem funcional sugerida para o backend

Para a implementacao incremental do backend, a ordem faz sentido ser:

1. Bootstrap da aplicacao Flask.
2. Configuracao do PostgreSQL.
3. Integracao com SQLAlchemy.
4. Migrations.
5. Models iniciais do inventario.
6. Endpoints basicos.
7. Importacao JSON.
8. Integracao GLPI.

Essa ordem respeita a necessidade de estruturar primeiro a base do sistema antes da integracao externa.

## Escopo inicial

Na fase inicial do projeto, o foco deve permanecer em:

- estrutura do backend;
- organizacao arquitetural correta;
- preparacao da aplicacao para banco e futuras migrations;
- implementacao incremental coerente com os casos de uso.

Funcionalidades futuras devem ser implementadas conforme os casos de uso priorizados, sem adicionar fluxos fora do escopo aprovado.
