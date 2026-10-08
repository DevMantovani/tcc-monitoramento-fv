# Calibração local após limpeza

## Finalidade

O monitor precisa de uma referência de geração limpa para cada instalação. Em uma residência, essa referência não vem de um segundo painel lavado; ela é criada com os dados coletados após uma limpeza confirmada.

## Dados necessários

O CSV operacional deve conter `timestamp`, `irradiance_wm2`, `temperature_c` e `power_kw`. A pessoa responsável deve registrar a data da limpeza e escolher uma janela posterior sem falhas, sombra atípica ou indisponibilidade conhecida.

## Execução

```bash
pv-monitor check-input \
  --input dados_operacionais.csv \
  --output artifacts/qualidade_entrada.json

pv-monitor calibrate-installation \
  --input dados_operacionais.csv \
  --cleaning-timestamp 2026-01-15T00:00:00Z \
  --calibration-days 14 \
  --minimum-observations 30 \
  --output artifacts/calibracao_local
```

O comando salva `clean_baseline_ridge.joblib`, usado posteriormente pelo comando `detect`, e `calibration.json`, que registra o evento de limpeza, a janela e a quantidade de observações usadas.

## Avaliação da duração da calibração

No experimento público de Laghouat, a potência do painel limpo pode ser usada como aproximação experimental de uma instalação recém-limpa. O comando abaixo avalia janelas de 14, 28, 42 e 60 dias, sempre testando apenas observações futuras:

```bash
pv-monitor evaluate-local-calibration \
  --input data/processed/laghouat_2022.csv \
  --output artifacts/laghouat_local_calibration
```

O resultado mostra que 14 dias produziram MAE de perda de 8,59 pontos percentuais e F1 de 0,847; com 60 dias, os valores foram 2,84 pontos percentuais e 0,904. A regra de alerta foi mantida fixa em 15% por três dias. Isso não define uma duração universal: demonstra apenas que uma janela curta pode não representar adequadamente a geração limpa futura.

## Limite científico atual

O fluxo está implementado e testado como arquitetura operacional, mas ainda não foi validado com uma instalação residencial real. A base pública de Laghouat fornece o painel limpo como referência experimental; ela não substitui a validação local futura.
