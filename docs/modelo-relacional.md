# Modelo Relacional

O DER Revisado é a fonte principal para a modelagem relacional do VITTAL Inventaris.

Este documento registra que futuras implementações de banco de dados, models SQLAlchemy e migrations devem seguir o DER Revisado antes de qualquer outra fonte.

## Fonte principal

O DER Revisado orienta:

- tabelas;
- campos;
- tipos de dados;
- chaves primárias;
- chaves estrangeiras;
- relacionamentos;
- constraints;
- obrigatoriedade de campos;
- campos futuros de sincronização com GLPI.

## Regra de implementação

Nenhuma tabela, campo, chave, constraint ou relacionamento deve ser criado fora do que estiver definido nos documentos técnicos do projeto sem justificativa prévia e aprovação.

## PostgreSQL como fonte de verdade

O PostgreSQL é a fonte de verdade do VITTAL Inventaris.

Mesmo quando houver sincronização com o GLPI, os dados principais do inventário e da manutenção devem ser armazenados e consultados a partir do PostgreSQL.

## Campos de sincronização GLPI

Campos de apoio à sincronização com o GLPI, como identificadores externos, status de sincronização e data da última sincronização, devem existir somente quando previstos pelo DER Revisado.

Esses campos serão controlados pelo sistema e não devem ser tratados como campos obrigatórios enviados pelo usuário em contratos de entrada.
