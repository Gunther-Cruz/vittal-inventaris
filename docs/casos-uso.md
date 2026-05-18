# Casos de Uso

Os Casos de Uso orientam os fluxos funcionais do VITTAL Inventaris.

Este documento registra que a ordem de implementação das funcionalidades deve ser guiada pelos casos de uso definidos nos documentos técnicos do projeto.

## Fonte principal

Os Casos de Uso orientam:

- fluxos funcionais;
- ordem de implementação;
- atores;
- permissões;
- entradas e saídas esperadas;
- principais interações do sistema;
- comportamento esperado em cenários de sucesso e falha.

## Regras de implementação

Controllers devem apenas coordenar a entrada e saída das requisições.

Services devem executar os casos de uso.

Repositories devem ser usados pelos services para persistência e consulta de dados.

Integrações externas, incluindo GLPI, devem ser acionadas por meio da camada de integração, nunca diretamente pelos controllers.

## Escopo inicial

Funcionalidades futuras devem ser implementadas conforme os casos de uso priorizados, sem adicionar fluxos fora do escopo aprovado.
