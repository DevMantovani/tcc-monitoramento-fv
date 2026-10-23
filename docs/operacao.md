# Fluxo operacional para futura integração

## Finalidade

Este fluxo de linha de comando recebe um CSV de medições, verifica sua qualidade e produz um indicador diário de perda adicional persistente. Ele está reservado para uma futura integração com dados locais de inversor, medidor ou API. A tela principal atual analisa somente o dataset público auditado de Laghouat. O resultado prioriza uma **inspeção**; ele não identifica a causa da perda e não aciona limpeza automática.

## Contrato mínimo de entrada

O CSV deve conter as seguintes colunas:

| Coluna | Unidade | Significado |
|---|---:|---|
| `timestamp` | data e hora | instante da medição; é convertido para UTC |
| `irradiance_wm2` | W/m² | irradiância no plano do módulo, ou a melhor aproximação documentada disponível |
| `temperature_c` | °C | temperatura operacional usada pelo modelo; pode ser de célula, módulo ou ambiente, desde que a origem seja registrada |
| `power_kw` | kW | potência medida no sistema fotovoltaico |

Para compatibilidade com versões anteriores, `module_temperature_c` também é aceito como entrada e registrado no relatório de qualidade. Campos como `precipitation_mm` podem ser enviados como contexto, mas não são tratados como evidência de que a chuva limpou o sistema.

## Execução

Primeiro, gere o relatório de qualidade. Ele mostra linhas inválidas, duplicadas, noturnas ou abaixo do limiar de irradiância, sem preencher dados artificialmente.

```bash
pv-monitor check-input \
  --input dados_operacionais.csv \
  --output artifacts/qualidade_entrada.json
```

Depois de uma limpeza confirmada, crie a referência local com uma janela em que o sistema permaneceu operacional. O operador é responsável por confirmar que essa janela não contém falha, sombra atípica ou nova sujeira relevante.

```bash
pv-monitor calibrate-installation \
  --input dados_operacionais.csv \
  --cleaning-timestamp 2026-01-15T00:00:00Z \
  --calibration-days 14 \
  --minimum-observations 30 \
  --output artifacts/calibracao_local
```

O comando grava o modelo `clean_baseline_ridge.joblib` e o registro auditável `calibration.json`. Depois, execute o indicador com essa referência local:

```bash
pv-monitor detect \
  --input dados_operacionais.csv \
  --model artifacts/calibracao_local/clean_baseline_ridge.joblib \
  --output artifacts/alertas_diarios.csv \
  --daily-loss-threshold 0.15 \
  --minimum-samples-per-day 1 \
  --persistence-days 3
```

O comando cria dois arquivos: o CSV diário e um JSON de resumo com qualidade da entrada, parâmetros usados e total de dias com alerta persistente.

## Como interpretar a saída

`additional_loss_alert = true` significa que a **mediana diária** da perda estimada superou o limiar, com o número mínimo de amostras, pelo número configurado de dias consecutivos. Um dia sem registros válidos interrompe a sequência; portanto, o sistema não interpreta dias separados por lacunas como consecutivos. A ação recomendada é verificar dados, sombreamento, falhas, disponibilidade e condições do sistema antes de considerar uma limpeza.

Os valores de limiar, quantidade mínima de amostras e persistência dependem da frequência de medição e precisam ser escolhidos na validação. No experimento de Laghouat, a política avaliada foi mediana de perda de 15% por três dias, após filtrar irradiância inferior a 50 W/m². Ela não deve ser transferida automaticamente para uma residência brasileira.

## Limite para uso em campo

O fluxo de calibração implementa a referência pós-limpeza, mas ainda não foi validado com telemetria residencial real. Antes do uso em uma residência, é necessário coletar dados locais de potência e ambiente, registrar eventos de limpeza e validar os limiares nesse sistema. Até lá, o fluxo é uma demonstração técnica auditável, não um serviço de decisão de limpeza.
