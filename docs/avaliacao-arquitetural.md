# Avaliacao Arquitetural do VITTAL Inventaris

Este documento registra uma avaliacao arquitetural do estado atual do VITTAL
Inventaris e os principais cuidados tecnicos para os proximos blocos de
desenvolvimento.

Ele existe para preservar o raciocinio por tras das decisoes tomadas ate agora e
servir como referencia futura caso o projeto mude de contexto, branch ou conversa.

## Estado Geral

O projeto esta seguindo um caminho arquitetural adequado para o contexto de um TCC.
Ele nao esta sofisticado demais e tambem nao esta sendo construido como uma aplicacao
Flask improvisada. A decisao atual e um meio-termo saudavel: um monolito modular em
camadas, simples o bastante para manter produtividade e organizado o bastante para
ser defendido tecnicamente.

O padrao central do codigo e:

```text
Controller ou Command
  -> Service
  -> Repository
  -> Model / SQLAlchemy / PostgreSQL
```

Para autorizacao, o fluxo e:

```text
Controller
  -> Decorator
  -> app/security/permissions.py
  -> current_user / dominio
```

Essa estrutura evita que regras de negocio, persistencia e permissoes fiquem
espalhadas em rotas Flask.

## Relacao Com o Banco de Dados

A relacao atual com o PostgreSQL e sincrona.

Quando uma requisicao chega, o fluxo normal e:

```text
Browser
  -> Flask controller
  -> Service
  -> Repository
  -> SQLAlchemy
  -> PostgreSQL
  -> resposta HTTP
```

A requisicao espera o banco responder antes de devolver a resposta ao usuario. Isso
e correto para os fluxos implementados ate agora:

- login;
- logout;
- criacao de usuario;
- edicao de usuario;
- cadastro de laboratorio;
- edicao de laboratorio;
- listagens administrativas;
- validacoes simples.

Nao ha necessidade de introduzir acesso assincrono ao banco neste momento. Usar
assincronismo agora aumentaria a complexidade sem resolver um problema real.

O assincronismo deve ser considerado futuramente para operacoes demoradas ou externas,
como:

- sincronizacao com GLPI;
- importacoes grandes;
- envio de e-mails;
- processamento pesado de relatorios;
- tarefas de dashboard muito custosas;
- jobs de manutencao ou consolidacao.

A regra continua sendo:

```text
PostgreSQL primeiro.
GLPI depois, de forma isolada e preferencialmente nao bloqueante.
```

## PostgreSQL Como Fonte de Verdade

O PostgreSQL e a fonte de verdade do VITTAL. Isso significa que dados oficiais do
sistema devem existir primeiro no banco do VITTAL, mesmo quando houver integracao
com GLPI.

O GLPI nao deve assumir papel de banco principal nem definir a modelagem interna do
VITTAL. Ele sera usado como subsistema auxiliar integrado.

Fluxo futuro esperado para dados sincronizaveis:

```text
1. Receber dados no VITTAL.
2. Validar regra de negocio.
3. Persistir no PostgreSQL.
4. Registrar status de sincronizacao, quando aplicavel.
5. Sincronizar depois com GLPI por app/integrations/.
```

Falhas no GLPI nao devem impedir o funcionamento principal do VITTAL.

## Qualidade Arquitetural Atual

O codigo atual evita tres problemas comuns em aplicacoes Flask:

1. Controller com regra de negocio demais.
2. Banco acessado diretamente de qualquer lugar.
3. Permissao espalhada em condicionais soltas.

Em vez disso, o projeto usa:

- `controllers/` para entrada HTTP;
- `commands/` para entrada CLI;
- `services/` para casos de uso;
- `repositories/` para acesso ao banco;
- `domain/` para models e enums;
- `security/` para regras de permissao;
- `integrations/` para futuras integracoes externas.

Essa divisao melhora legibilidade, testabilidade e defesa tecnica.

## Controllers

Controllers devem continuar finos.

Eles podem:

- receber requisicao HTTP;
- ler `request.form`;
- chamar services;
- lidar com erros esperados;
- renderizar templates;
- redirecionar;
- emitir mensagens flash.

Eles nao devem:

- conter regra de negocio pesada;
- acessar banco diretamente;
- chamar GLPI;
- concentrar permissoes complexas;
- montar transacoes compostas.

## Services

Services representam casos de uso.

No estado atual:

- `AuthService` cuida de autenticacao e apoio direto a autorizacao;
- `UsuarioService` cuida de gestao administrativa de usuarios;
- `InventoryService` iniciou o nucleo de inventario com laboratorio.

Essa separacao e importante. Por exemplo, autenticar usuario nao e o mesmo caso de
uso que cadastrar usuario. Por isso, a gestao de usuarios foi separada de
`AuthService` e movida para `UsuarioService`.

No caso do inventario, a decisao correta foi criar `InventoryService` desde o bloco
de laboratorio, em vez de criar um `LaboratorioService`. O diagrama de classes aponta
para `InventarioService` como o nucleo que futuramente deve abranger:

- laboratorios;
- estacoes de trabalho;
- gabinetes;
- monitores;
- movimentacoes;
- upgrades;
- descartes;
- consultas de inventario.

Isso evita uma arquitetura baseada em "um service por tabela" e aproxima o codigo
dos casos de uso reais.

## Repositories

Repositories isolam persistencia.

Eles devem conter:

- buscas por id;
- buscas por campos unicos;
- listagens;
- filtros;
- `save`;
- `commit`;
- rollback em caso de erro.

Eles nao devem conter:

- regra de permissao;
- regra de negocio de alto nivel;
- validacao de formulario;
- decisao de fluxo HTTP.

Hoje os repositories fazem commit diretamente. Isso e adequado para operacoes simples.
No futuro, casos de uso compostos podem exigir controle transacional mais forte no
service ou em uma unidade de trabalho.

Exemplo futuro:

```text
abrir chamado
  + criar historico inicial
  + gerar protocolo
  + registrar status
```

Esse tipo de fluxo talvez precise que o service controle a transacao completa.

## Domain

O dominio atual contem models e enums.

Este projeto nao esta seguindo Clean Architecture pura. Os models de dominio tambem
sao models SQLAlchemy. Essa e uma escolha consciente, compativel com Flask,
SQLAlchemy, monolito modular e escopo de TCC.

Vantagens dessa decisao:

- menor complexidade;
- menos classes duplicadas;
- migrations mais diretas;
- melhor produtividade;
- arquitetura mais facil de explicar e manter.

Cuidados:

- nao colocar logica de tela no dominio;
- nao chamar Flask a partir do dominio;
- nao chamar GLPI a partir do dominio;
- nao transformar models em objetos com responsabilidades demais.

## Security e Permissionamento

As regras de permissao ficam em `app/security/permissions.py`.

Essa decisao e importante porque permissao e uma preocupacao transversal. Se cada
controller verificasse perfis diretamente, o projeto ficaria dificil de manter.

O padrao desejado e:

```python
@permissao_requerida(can_manage_laboratories)
def create_laboratory():
    ...
```

E nao:

```python
if current_user.perfil == PerfilUsuario.TECNICO:
    ...
```

Funcoes de permissao atuais incluem regras para:

- usuarios;
- dashboard;
- laboratorios.

Esse modulo deve crescer com cuidado. No futuro, se o coordenador puder conceder
permissoes mais finas por ator, este sera o ponto natural de organizacao.

## Decorators

Decorators protegem rotas antes da execucao do controller.

O projeto possui dois padroes:

- decorator por perfil;
- decorator por funcao de permissao.

O decorator por funcao de permissao e mais flexivel, porque permite regras que nao
sao apenas comparacao de perfil. O dashboard e um exemplo: coordenador acessa por
perfil, mas professor e tecnico dependem de permissao persistida.

## Commands

Commands CLI sao outra porta de entrada da aplicacao.

Fluxo:

```text
CLI
  -> Command
  -> Service
  -> Repository
  -> PostgreSQL
```

O caso mais importante e a criacao do primeiro coordenador. Como somente coordenador
pode criar usuarios pela interface, o sistema precisa de um bootstrap administrativo
fora da web.

Por isso existe o command:

```text
flask auth criar-coordenador-inicial
```

Esse comando evita cadastro publico de administrador.

## Fluxo Publico e Fluxo Interno

Uma decisao importante do Bloco 2 foi separar fluxo publico e fluxo interno.

Fluxo publico:

```text
/
/public/laboratories
```

Objetivo:

- orientar aluno ou usuario externo;
- escolher laboratorio;
- futuramente escolher estacao;
- abrir chamado;
- mostrar resumo e protocolo.

Fluxo interno:

```text
/laboratories
/laboratories/<id>/map
```

Objetivo:

- permitir visao operacional;
- mostrar mais detalhes;
- futuramente exibir chamados abertos;
- historicos;
- OSs;
- ativos vinculados;
- acoes de tecnico/coordenador.

Mesmo que as duas telas venham a ter visual parecido, elas devem continuar sendo
rotas diferentes, porque possuem intencoes e politicas de acesso diferentes.

## Performance

Para o estado atual, a performance esta adequada.

Ja existem indices importantes:

- `usuario.email`;
- `laboratorio.codigo_laboratorio`.

Esses indices sustentam buscas frequentes e unicidade.

Pontos para monitorar no futuro:

- evitar queries repetidas dentro de loops;
- evitar N+1 queries quando surgirem relacionamentos;
- paginar listagens grandes;
- filtrar no banco, nao em Python;
- criar indices para campos usados em filtros;
- cuidar com dashboards pesados;
- nao deixar integracoes externas bloquearem requisicoes;
- considerar cache ou jobs para relatorios custosos.

Nao ha motivo para otimizar prematuramente. A regra deve ser: medir ou identificar
um gargalo real antes de adicionar complexidade.

## Seguranca

A base de seguranca atual e boa para o estagio do projeto:

- senha armazenada com hash;
- login por sessao;
- logout;
- CSRF em formularios;
- cookies `HttpOnly`;
- configuracao de `SameSite`;
- rotas protegidas;
- permissionamento centralizado;
- usuario inativo nao autentica;
- `user_loader` rejeita usuario inativo;
- bloqueio de redirect externo no login.

Pontos para evoluir no futuro:

- `SECRET_KEY` forte em producao;
- HTTPS com `SESSION_COOKIE_SECURE=True`;
- politica de senha mais robusta;
- troca de senha;
- recuperacao de senha;
- logs de seguranca;
- auditoria de acoes administrativas;
- protecao contra brute force no login;
- autenticacao Google/OAuth;
- revisao de permissoes finas quando o dominio crescer.

## Autenticacao Google no Futuro

Adicionar autenticacao Google pode fazer sentido futuramente, especialmente se o
ambiente institucional usar contas Google.

Mas isso nao deve ser implementado antes de estabilizar o dominio principal. O fluxo
atual por sessao e usuario persistido ja e suficiente para os blocos iniciais.

Quando OAuth/Google entrar, pontos importantes:

- manter `Usuario` como usuario interno persistido;
- associar conta Google a um usuario do VITTAL;
- preservar perfis internos (`PROFESSOR`, `TECNICO`, `COORDENADOR`);
- nao transformar Google na fonte de regras de dominio;
- continuar usando PostgreSQL como fonte de verdade dos usuarios do sistema.

## GLPI

GLPI deve ficar isolado em `app/integrations/`.

Componentes previstos:

- `glpi_client.py`;
- `glpi_mapper.py`;
- `glpi_adapter.py`.

Controllers nao devem chamar GLPI. Models nao devem conhecer GLPI. Repositories nao
devem depender de schema do GLPI.

Fluxos com GLPI devem seguir:

```text
Service
  -> Repository/PostgreSQL
  -> status de sincronizacao
  -> Integration/GLPI
```

Idealmente, a sincronizacao futura deve ser assincrona ou pelo menos nao bloqueante.

## Riscos Arquiteturais Para Observar

Alguns pontos podem ficar sensiveis conforme o sistema crescer:

- `InventoryService` crescer demais;
- permissoes ficarem complexas demais;
- dashboards ficarem pesados;
- GLPI introduzir instabilidade;
- chamados e OSs exigirem transacoes mais robustas;
- fluxo publico e interno compartilharem visual sem duplicar logica;
- consistencia entre vinculo atual de estacao e historico de movimentacao;
- nomes em portugues no Bloco 1 e nomes em ingles nos blocos novos.

Esses pontos nao sao problemas agora, mas devem ser monitorados.

## Melhorias Futuras Recomendadas

Nao sao obrigatorias imediatamente, mas devem ficar no radar:

- padronizar Bloco 1 para ingles;
- melhorar layout base e navegacao;
- criar paginas amigaveis de erro 403 e 404;
- criar formularios mais estruturados se os templates crescerem;
- adicionar logging estruturado;
- adicionar auditoria de acoes criticas;
- criar seeds/dev fixtures controladas;
- organizar testes reais com PostgreSQL;
- adicionar paginacao;
- documentar permissoes por ator em tabela;
- preparar cache ou jobs para dashboards pesados.

## Regra de Ouro Para Proximos Blocos

Manter o seguinte criterio:

```text
Se a funcionalidade for pequena, implemente simples.
Se a regra for importante, coloque no service.
Se acessar banco, passe por repository.
Se for permissao, centralize em security.
Se for integracao externa, isole em integrations.
Se for publico vs interno, separe rota e intencao.
Se for dado oficial, PostgreSQL primeiro.
```

Essa e a base arquitetural que deve guiar o restante do VITTAL Inventaris.
