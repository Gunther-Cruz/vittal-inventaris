# Modelo Relacional

O DER Revisado e a fonte principal para a modelagem relacional do VITTAL Inventaris.

Este documento registra que futuras implementacoes de banco de dados, models SQLAlchemy e migrations devem seguir o DER Revisado antes de qualquer outra fonte.

## Papel do banco

O PostgreSQL e a fonte de verdade do VITTAL Inventaris.

Mesmo quando houver sincronizacao com o GLPI, os dados principais do inventario, da manutencao, do historico e dos chamados devem ser armazenados e consultados a partir do PostgreSQL.

## Regras obrigatorias

- Nenhuma tabela, campo, chave, constraint ou relacionamento deve ser criado fora do que estiver definido nos documentos tecnicos do projeto sem justificativa previa e aprovacao.
- O modelo relacional do VITTAL nao deve depender estruturalmente do schema do GLPI.
- O banco do GLPI nao deve ser tratado como banco principal.
- Campos de sincronizacao com GLPI nao devem ser obrigatorios em entradas de usuario.
- A modelagem deve privilegiar rastreabilidade, historico e apoio a decisao.

## Estruturas centrais do dominio

O nucleo relacional do projeto gira em torno destes blocos:

### Estrutura fisica

- `LABORATORIO`
- `ESTACAO_TRABALHO`
- `GABINETE`
- `MONITOR`
- `ALOCACAO_GABINETE_ESTACAO`
- `ALOCACAO_MONITOR_ESTACAO`

### Atendimento e fluxo tecnico

- `USUARIO`
- `CHAMADO`
- `HISTORICO_CHAMADO`
- `TIPO_PROBLEMA`
- `ORDEM_SERVICO`
- `MANUTENCAO_REGISTRO`

### Ciclo de vida do ativo

- `UPGRADE_GABINETE`
- `DESCARTE_ATIVO`

## Regras conceituais importantes

### Estacao como ancora fisica

Laboratorio e fixo.

Estacao de trabalho e fixa dentro do laboratorio.

Gabinete e monitor podem mudar de estacao ao longo do tempo.

Por isso:

- a estacao e a ancora fisica/lógica do sistema;
- o vinculo atual pode ficar na estacao;
- o historico de movimentacao deve ser preservado em tabelas de alocacao.

### Ativos separados

Gabinete e monitor sao ativos separados, com patrimonio e historico proprios.

Nao devem ser tratados como um unico objeto simplificado.

### Chamado com escopos diferentes

O projeto trabalha com um unico conceito de chamado, mas com escopos diferentes:

- chamado de estacao;
- chamado de laboratorio.

O modelo relacional deve permitir esse comportamento sem duplicar a ideia de chamado em duas tabelas separadas.

### Historico como requisito central

O sistema deve manter historico util de:

- movimentacao;
- manutencao;
- upgrades;
- descarte;
- evolucao de chamados;
- mudanca de estado operacional.

## Regras derivadas do DER

### CHAMADO

O chamado deve suportar:

- abertura por usuario autenticado;
- abertura externa por requerente nao persistido;
- vinculo com laboratorio;
- vinculo opcional com estacao;
- escopo e alvo coerentes com o fluxo funcional;
- status, prioridade e historico proprios;
- campos de sincronizacao com GLPI quando previstos.

### ORDEM_SERVICO

O tipo de problema entra na ordem de servico, nao no chamado inicial.

Essa separacao deve ser preservada no banco e no backend.

### MANUTENCAO_REGISTRO

O registro de manutencao materializa o resultado tecnico da ordem de servico.

Em manutencoes de laboratorio, o sistema pode precisar gerar multiplos registros a partir de uma mesma ordem, um para cada ativo efetivamente avaliado ou manipulado.

### USUARIO

Os perfis persistidos do sistema sao:

- `PROFESSOR`
- `TECNICO`
- `COORDENADOR`

Aluno nao deve ser persistido como usuario do banco na versao atual.

## Campos de sincronizacao GLPI

Campos de apoio a sincronizacao com o GLPI, como identificadores externos, status de sincronizacao e data da ultima sincronizacao, devem existir somente quando previstos pelo DER Revisado.

Exemplos previstos:

- `glpi_computer_id`
- `glpi_monitor_id`
- `glpi_ticket_id`
- `glpi_sync_status`
- `glpi_last_sync_at`

Esses campos serao controlados pelo sistema e nao devem ser tratados como campos obrigatorios enviados pelo usuario em contratos de entrada.

## Implicacoes para implementacao

Antes de criar models e migrations, o Codex deve confirmar:

- nomes exatos das tabelas e colunas no DER;
- cardinalidades principais;
- campos obrigatorios e unicos;
- regras de vinculacao atual versus historico;
- campos de sincronizacao com GLPI;
- regras especiais de chamado, OS e manutencao.

Se houver divergencia entre uma ideia nova e o DER, a implementacao deve parar e explicar a divergencia antes de prosseguir.
