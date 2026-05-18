# Contratos JSON

Este documento registra rascunhos iniciais de contratos JSON esperados para futuras APIs do VITTAL Inventaris.

Nenhum endpoint será implementado nesta etapa.

Os contratos descritos aqui são referências iniciais para orientar implementações futuras e devem sempre ser conferidos com o DER Revisado, o Diagrama de Classes e os Casos de Uso antes da implementação.

## Regras gerais

- O PostgreSQL é a fonte de verdade do sistema.
- Entradas de usuário não devem exigir campos internos de sincronização com GLPI.
- Campos de integração, quando previstos, devem ser controlados pelo sistema.
- Contratos futuros devem respeitar o DER Revisado e o Diagrama de Classes.
- Não devem ser adicionados campos, entidades ou relacionamentos fora dos documentos técnicos aprovados.

## Gabinete

A entidade Gabinete representa o computador ou gabinete físico.

O contrato abaixo é apenas um rascunho inicial de entrada para futuras APIs. O modelo completo de Gabinete vem do DER Revisado e do Diagrama de Classes.

Campos de GLPI, como `glpi_computer_id`, `glpi_sync_status` e `glpi_last_sync_at`, não devem ser enviados obrigatoriamente pelo usuário. Eles serão controlados pelo sistema futuramente.

```json
{
  "num_patrimonio": "12345",
  "numero_serie": "ABC123XYZ",
  "fabricante": "Dell",
  "modelo": "OptiPlex 3040",
  "lote": "Lote 2022-A",
  "data_compra": "2022-03-15",
  "processador_modelo": "Intel Core i3-6100",
  "processador_frequencia_ghz": 3.7,
  "placa_mae_modelo": "Dell 0XJ8C4",
  "memoria_instalada_gb": 8,
  "memoria_tecnologia": "DDR4",
  "memoria_velocidade_mhz": 2133,
  "memoria_slots_total": 2,
  "memoria_slots_ocupacao": "1x8GB",
  "armazenamento_descricao": "SSD 240GB SATA",
  "fonte_descricao": "Fonte Dell 240W",
  "sistema_operacional": "Ubuntu MATE 22.04",
  "situacao_operacional": "EM_FUNCIONAMENTO",
  "observacao": "Equipamento importado a partir de coleta técnica inicial"
}
```

## Observação sobre evolução

Novos contratos devem ser adicionados somente quando houver caso de uso aprovado e fonte técnica correspondente.
