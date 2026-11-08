# Validação externa do monitor de sujidade

## Fonte auditada

O teste usa a versão 2 da base de Dhaka publicada no Mendeley Data: [A comprehensive dataset for monitoring photovoltaic panels and weather parameters in urban Bangladesh](https://doi.org/10.17632/g6pxf8nnt6.2). A fonte tem licença CC BY 4.0, dois painéis de 20 W — um limpo regularmente e outro exposto — e variáveis de potência e ambiente.

O arquivo original `Solar Dataset.zip` já acompanha o repositório em `data/raw/dhaka_2019_2020/`. Extraia-o para uma pasta local ignorada pelo Git:

```text
data/interim/dhaka_2019_2020/Solar Dataset/
```

Em seguida, prepare a fonte:

```bash
mkdir -p data/interim/dhaka_2019_2020
tar -xf "data/raw/dhaka_2019_2020/Solar Dataset.zip" -C data/interim/dhaka_2019_2020

pv-monitor prepare-bangladesh \
  --input-dir data/interim/dhaka_2019_2020 \
  --output data/processed/bangladesh_2019_2020.csv
```

No Windows PowerShell, substitua a primeira linha por `New-Item -ItemType Directory -Force data/interim/dhaka_2019_2020`; o comando `tar` do Windows extrai o mesmo arquivo.

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

A transferência falhou: a perda estimada teve MAE de 41,46 pontos percentuais e a política de Laghouat gerou 25 alertas falsos no teste final. A contagem reinicia quando há lacuna entre dias do calendário; isso evita que uma sequência atravesse período sem dados. A recalibração local não resolveu o problema (F1 de 0,043 no teste final). Esses resultados demonstram que o monitor ainda depende de validação e calibração específicas por instalação.

O conjunto possui 295 arquivos diários disponíveis, com cabeçalhos e formatos de data ligeiramente diferentes. O preparador normaliza essas diferenças de forma rastreável e agrega as leituras de 30 segundos por hora. Consulte [dados.md](dados.md) para os limites de origem e qualidade.
