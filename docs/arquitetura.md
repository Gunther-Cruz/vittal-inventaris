# Arquitetura do VITTAL Inventaris

O VITTAL Inventaris segue uma arquitetura de monólito modular em camadas.

O sistema será implementado como uma aplicação web Flask, com PostgreSQL como fonte de verdade para os dados do domínio. O GLPI será tratado apenas como subsistema integrado de apoio, sem assumir o papel de base principal do VITTAL.

## Princípios

- O sistema não será dividido em microserviços nesta fase.
- O Flask será o framework principal da aplicação web.
- O PostgreSQL será a fonte de verdade do sistema.
- O GLPI será um subsistema auxiliar integrado.
- A aplicação deve salvar primeiro no PostgreSQL e sincronizar depois com o GLPI.
- Falhas em integrações externas não devem impedir o funcionamento central do VITTAL.
- Controllers não devem conter regra de negócio pesada.
- Services executam os casos de uso.
- Repositories isolam o acesso ao banco de dados.
- Models e enums representam o domínio e a persistência.

## Camadas previstas

### Controllers

Camada responsável por receber requisições web, validar entradas simples, acionar services e retornar respostas.

Controllers não devem conter regras de negócio complexas, acesso direto ao banco de dados ou chamadas diretas ao GLPI.

### Services

Camada responsável pela execução dos casos de uso do sistema.

Services coordenam regras de negócio, transações, repositories e integrações quando necessário.

### Repositories

Camada responsável por isolar o acesso ao PostgreSQL.

Repositories devem concentrar consultas, persistência e operações específicas de banco, evitando que controllers e services dependam diretamente de detalhes de SQLAlchemy.

### Domain

Camada responsável por representar o domínio da aplicação.

Inclui models, enums e estruturas associadas às entidades descritas pelo DER Revisado e pelo Diagrama de Classes.

### Integrations

Camada responsável por integrações externas.

Toda integração com GLPI deve ficar isolada em `app/integrations/`.

### Dashboards

Camada prevista para recursos analíticos com Dash, Plotly e Pandas.

Dashboards devem consumir dados do PostgreSQL do VITTAL, não diretamente do GLPI.

## Regra central de persistência e sincronização

O fluxo correto para dados do domínio é:

1. Receber e validar os dados no VITTAL.
2. Persistir os dados no PostgreSQL.
3. Registrar o estado de sincronização quando aplicável.
4. Sincronizar posteriormente com o GLPI por meio da camada de integração.

O GLPI não deve ser requisito para que o PostgreSQL funcione, nem para que o VITTAL execute seus fluxos principais.
