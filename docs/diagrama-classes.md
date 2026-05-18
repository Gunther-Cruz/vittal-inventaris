# Diagrama de Classes

O Diagrama de Classes e a fonte principal para a organizacao do dominio do VITTAL Inventaris.

Este documento registra que futuras implementacoes de classes, models, enums, services e repositories devem respeitar as responsabilidades e estruturas definidas no Diagrama de Classes.

## Papel do diagrama de classes

O Diagrama de Classes orienta:

- classes do dominio;
- responsabilidades de cada classe;
- enums;
- services;
- repositories;
- associacoes entre objetos do dominio;
- separacao entre camada de dominio e camada de aplicacao.

## Regras obrigatorias

- As classes do dominio devem refletir os conceitos definidos nos documentos tecnicos do projeto.
- Services devem representar casos de uso e regras de negocio.
- Repositories devem representar a interface de acesso aos dados persistidos.
- Enums devem ser criados apenas quando houver definicao de estados, tipos ou categorias no dominio.
- O dominio nao deve conter chamadas HTTP para GLPI, detalhes de Flask ou logica de tela.

## Enums centrais

Os enums ja consolidados no projeto incluem, no minimo:

- `PerfilUsuario`
- `EscopoChamado`
- `AlvoTipo`
- `Prioridade`
- `StatusChamado`
- `StatusOS`
- `TipoManutencao`
- `SituacaoOperacional`

Esses estados e categorias devem guiar tanto a modelagem do dominio quanto a futura persistencia.

## Classes de dominio principais

### Laboratorio

Representa o espaco fisico institucional onde as estacoes estao organizadas.

Responsabilidades esperadas:

- identificar o laboratorio;
- agrupar estacoes;
- servir de contexto para inventario, chamados e manutencoes.

### EstacaoTrabalho

Representa a posicao fixa dentro do laboratorio.

Regras importantes:

- e a ancora fisica do sistema;
- pode ter um gabinete atual e um monitor atual;
- precisa preservar historico de alocacoes.

### AtivoTI

Classe de software abstrata para concentrar o que gabinete e monitor tem em comum.

Essa abstracao organiza o dominio, mas nao obriga a existencia de uma tabela unica no banco.

### Gabinete

Representa o ativo computacional principal.

Deve respeitar o DER e o Diagrama de Classes, incluindo:

- dados patrimoniais;
- atributos tecnicos;
- situacao operacional;
- historico de alocacao;
- upgrades;
- manutencoes;
- descarte;
- campos futuros de sincronizacao com GLPI quando previstos.

### Monitor

Representa o monitor como ativo individualizado.

Tambem deve possuir patrimonio, estado operacional, historico e eventual sincronizacao com GLPI quando prevista.

### Usuario

Representa os usuarios persistidos do sistema.

Perfis persistidos:

- professor;
- tecnico;
- coordenador.

Aluno nao entra como usuario persistido na versao atual.

### Chamado

Representa a ocorrencia relatada.

Regras importantes:

- pode ser aberto por usuario autenticado ou por requerente externo;
- pode ser de estacao ou de laboratorio;
- nao deve absorver a classificacao tecnica final do problema;
- deve manter historico de status;
- deve suportar protocolo de consulta para fluxo externo.

### HistoricoChamado

Representa os eventos do ciclo de vida do chamado.

Serve para rastrear alteracoes de status e observacoes relevantes.

### TipoProblema

Padroniza os codigos de problema utilizados no diagnostico tecnico.

A classificacao tecnica fica mais associada a ordem de servico do que ao chamado inicial.

### OrdemServico

Representa a execucao tecnica do atendimento.

Responsabilidades esperadas:

- associar tecnico responsavel;
- associar tipo de problema;
- registrar diagnostico;
- registrar servico executado;
- controlar andamento tecnico.

### ManutencaoRegistro

Materializa o registro final da manutencao executada.

Em chamados de laboratorio, uma ordem de servico pode resultar em mais de um registro de manutencao, um por ativo efetivamente avaliado ou manipulado.

### AlocacaoGabineteEstacao e AlocacaoMonitorEstacao

Representam o historico de movimentacao dos ativos entre estacoes.

Essas classes sao essenciais para manter rastreabilidade do contexto fisico.

### UpgradeGabinete

Representa alteracoes tecnicas relevantes no gabinete, preservando historico.

### DescarteAtivo

Representa o descarte de gabinete, monitor ou peca vinculada.

## Services de referencia

Os services aprovados como referencia arquitetural incluem:

- `AuthService`
- `InventarioService`
- `ChamadoService`
- `OrdemServicoService`
- `ManutencaoService`
- `DashboardService`
- `GlpiAdapter`

### AuthService

Centraliza autenticacao e autorizacao dos usuarios persistidos.

### InventarioService

Centraliza:

- cadastro e atualizacao de ativos;
- importacao de JSON tecnico;
- vinculacao e movimentacao;
- atualizacao de situacao operacional;
- upgrade;
- descarte;
- consulta de historico.

### ChamadoService

Centraliza:

- abertura de chamado autenticado;
- abertura de chamado externo;
- geracao e consulta de protocolo;
- atribuicao de tecnico;
- alteracao de status;
- encerramento;
- consulta de historico.

### OrdemServicoService

Centraliza a execucao tecnica do atendimento.

### ManutencaoService

Centraliza a geracao dos registros finais de manutencao.

### DashboardService

Centraliza consolidacao e entrega de indicadores analiticos.

### GlpiAdapter

Encapsula toda a integracao externa entre o VITTAL e o GLPI.

## Regras de implementacao

- Services nao devem ser substituidos por controllers com logica pesada.
- Repositories nao devem conter regra de negocio de alto nivel.
- Integracao com GLPI deve ficar fora do dominio.
- O bootstrap inicial do projeto pode criar a estrutura de pastas e classes-base, mas nao deve inventar entidades fora do DER e do Diagrama de Classes.

## Implicacoes para as tarefas 3 e 3.1

Na fase de bootstrap:

- a estrutura de diretorios deve refletir a divisao em `controllers`, `services`, `domain`, `repositories`, `integrations`, `dashboards` e `config`;
- a implementacao inicial deve preparar o terreno para esses modulos, mesmo que nem todos tenham conteudo funcional ainda;
- o objetivo e alinhar o esqueleto do backend com o desenho de classes e responsabilidades ja aprovados.
