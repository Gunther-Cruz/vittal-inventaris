# Diagrama de Classes

O Diagrama de Classes é a fonte principal para a organização do domínio do VITTAL Inventaris.

Este documento registra que futuras implementações de classes, models, enums, services e repositories devem respeitar as responsabilidades e estruturas definidas no Diagrama de Classes.

## Fonte principal

O Diagrama de Classes orienta:

- classes do domínio;
- responsabilidades de cada classe;
- organização dos models;
- enums;
- services;
- repositories;
- associações entre objetos do domínio.

## Regras de implementação

As classes do domínio devem refletir os conceitos definidos nos documentos técnicos do projeto.

Services devem representar casos de uso e regras de negócio.

Repositories devem representar a interface de acesso aos dados persistidos.

Enums devem ser criados apenas quando houver definição de estados, tipos ou categorias no domínio.

## Gabinete

A entidade Gabinete representa o computador ou gabinete físico.

Gabinete não deve ser tratado como um modelo simplificado. Sua implementação futura deve respeitar o DER Revisado e o Diagrama de Classes, incluindo seus atributos técnicos, dados patrimoniais, situação operacional e campos futuros de sincronização com GLPI quando previstos.
