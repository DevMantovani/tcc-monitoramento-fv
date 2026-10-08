# Fluxo operacional do protótipo

## Finalidade

O fluxo recebe um CSV de medições, verifica sua qualidade e produz um indicador diário de perda adicional persistente. O resultado prioriza uma **inspeção**; ele não identifica a causa da perda e não aciona limpeza automática.

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

Depois, execute o indicador com um modelo previamente selecionado e validado:

```bash
pv-monitor detect \
  --input dados_operacionais.csv \
  --model caminho/para/modelo.joblib \
  --output artifacts/alertas_diarios.csv \
  --daily-loss-threshold 0.15 \
  --minimum-samples-per-day 4 \
  --persistence-days 3
```

O comando cria dois arquivos: o CSV diário e um JSON de resumo com qualidade da entrada, parâmetros usados e total de dias com alerta persistente.

## Como interpretar a saída

`additional_loss_alert = true` significa que a perda média diária estimada superou o limiar, com o número mínimo de amostras, pelo número configurado de dias consecutivos. A ação recomendada é verificar dados, sombreamento, falhas, disponibilidade e condições do sistema antes de considerar uma limpeza.

Os valores de limiar, quantidade mínima de amostras e persistência dependem da frequência de medição e precisam ser escolhidos na validação. No experimento de Laghouat, a política avaliada foi 15% por três dias; ela não deve ser transferida automaticamente para uma residência brasileira.

## Limite para uso em campo

O modelo disponível neste protótipo foi desenvolvido em dados públicos de um experimento específico. Antes do uso em uma residência, é necessário coletar dados locais de potência e ambiente, definir um período de referência pós-limpeza e recalibrar/validar o modelo e os limiares nesse sistema. Até lá, o fluxo é uma demonstração técnica auditável, não um serviço de decisão de limpeza.
