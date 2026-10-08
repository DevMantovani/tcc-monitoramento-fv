# Validação externa do monitor de sujidade

## Fonte auditada

O teste usa a versão 2 da base de Dhaka publicada no Mendeley Data: [A comprehensive dataset for monitoring photovoltaic panels and weather parameters in urban Bangladesh](https://doi.org/10.17632/g6pxf8nnt6.2). A fonte tem licença CC BY 4.0, dois painéis de 20 W — um limpo regularmente e outro exposto — e variáveis de potência e ambiente.

Baixe `Solar Dataset.zip` pelo DOI e extraia os dois níveis de ZIP para que os CSVs fiquem em:

```text
data/raw/bangladesh_2019_2020/extracted/Solar Dataset/
```

Em seguida, prepare a fonte:

```bash
pv-monitor prepare-bangladesh \
  --input-dir data/raw/bangladesh_2019_2020/extracted \
  --output data/processed/bangladesh_2019_2020.csv
```

## Protocolo de transferência

O objetivo não é escolher outro algoritmo. Ridge permanece o estimador interno selecionado no experimento principal. Para evitar uma alegação incorreta de transferência de pesos, o ajuste do Ridge é feito com o período de desenvolvimento cronológico da própria base de Dhaka; o que fica congelado a partir de Laghouat é a arquitetura escolhida e, no primeiro teste, a política de alerta. Assim, o protocolo testa se o **fluxo do monitor** e sua regra de alerta se sustentam em outra instalação, e não se pesos treinados em um painel de 20 W podem ser reutilizados literalmente em outro painel.

Primeiro aplica-se a política de Laghouat sem qualquer adaptação:

```bash
pv-monitor evaluate-final \
  --input data/processed/bangladesh_2019_2020.csv \
  --policy artifacts/laghouat_monitor/alert_policy_validation.json \
  --output artifacts/bangladesh_transfer
```

Como verificação de adaptação local, a política pode ser escolhida apenas na validação de Dhaka e testada uma única vez depois:

```bash
pv-monitor calibrate-alert-policy \
  --input data/processed/bangladesh_2019_2020.csv \
  --model-name ridge \
  --output artifacts/bangladesh_monitor

pv-monitor evaluate-final \
  --input data/processed/bangladesh_2019_2020.csv \
  --policy artifacts/bangladesh_monitor/alert_policy_validation.json \
  --output artifacts/bangladesh_final_local_policy
```

## Resultado e interpretação

A transferência falhou: a perda estimada teve MAE de 41,46 pontos percentuais e a política de Laghouat gerou 26 alertas falsos no teste final. A recalibração local não resolveu o problema (F1 de 0,043 no teste final). Esses resultados devem permanecer no artigo, pois demonstram que o monitor ainda depende de validação e calibração específicas por instalação.

O conjunto possui 295 arquivos diários disponíveis, com cabeçalhos e formatos de data ligeiramente diferentes. O preparador normaliza essas diferenças de forma rastreável e agrega as leituras de 30 segundos por hora. Consulte [dados.md](dados.md) para os limites de origem e qualidade.
