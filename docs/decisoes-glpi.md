# Decisões Sobre GLPI

O GLPI será integrado ao VITTAL Inventaris como subsistema auxiliar.

O VITTAL é o sistema principal para os fluxos definidos neste projeto. O PostgreSQL do VITTAL é a fonte de verdade.

## Decisões principais

- O VITTAL é o sistema principal.
- O GLPI é auxiliar.
- O PostgreSQL não deve depender do GLPI para funcionar.
- A integração com GLPI deve ficar isolada em `app/integrations/`.
- Controllers não devem chamar o GLPI diretamente.
- Falhas de sincronização com GLPI não devem impedir o funcionamento do VITTAL.
- Dados sincronizáveis devem possuir status de sincronização quando previsto pelo DER Revisado.

## Componentes previstos

### GlpiClient

Responsável pela comunicação direta com a API do GLPI.

Deve concentrar autenticação, requisições HTTP, tratamento básico de respostas e erros da API externa.

### GlpiMapper

Responsável por converter dados entre o formato do domínio do VITTAL e o formato esperado pelo GLPI.

Não deve conter regras de negócio do caso de uso.

### GlpiAdapter

Responsável por orquestrar operações de integração usando `GlpiClient` e `GlpiMapper`.

Deve expor uma interface interna mais estável para os services do VITTAL.

## Fluxo de sincronização

O fluxo correto é:

1. Persistir o dado no PostgreSQL.
2. Marcar ou atualizar o status de sincronização quando aplicável.
3. Acionar a integração com GLPI posteriormente.
4. Registrar sucesso, falha ou pendência de sincronização.

Campos como `glpi_computer_id`, `glpi_sync_status` e `glpi_last_sync_at`, quando previstos, devem ser controlados pelo sistema.
