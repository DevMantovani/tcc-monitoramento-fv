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

## Limite científico atual

O fluxo está implementado e testado como arquitetura operacional, mas ainda não foi validado com uma instalação residencial real. A base pública de Laghouat fornece o painel limpo como referência experimental; ela não substitui a validação local futura.
