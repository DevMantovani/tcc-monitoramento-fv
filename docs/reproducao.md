# Reprodução dos experimentos públicos

O comando abaixo recompõe os resultados do projeto a partir das duas fontes públicas auditadas. Ele prepara os CSVs, treina os candidatos, seleciona cada modelo somente pela validação cronológica, congela a política de alerta e executa os testes finais.

```bash
pv-monitor reproduce-public-experiments \
  --laghouat-input data/raw/laghouat_2022/Laghouat_2022_final.csv \
  --zenodo-input data/raw/zenodo_inverter_2023_2024/math_model_all_inverters_03.11.2023-25.06.2024.csv \
  --output artifacts/reproduction_summary.json
```

As entradas brutas, processadas e os artefatos gerados permanecem fora do Git. O arquivo `reproduction_summary.json` registra caminhos, modelo selecionado, política de alerta e métricas finais para cada experimento.

## O que o comando reproduz

1. **Laghouat 2022:** monitor de perdas por sujidade com par limpo/exposto. Seleciona o modelo pelo menor erro de perda na validação, escolhe limiar e persistência na validação e testa uma única vez o período final preservado.
2. **Zenodo 2023--2024:** estimação externa de potência para `inverter1`. Seleciona o modelo pelo menor MAE de potência na validação e testa o período final preservado. Não produz nem valida alertas de sujidade, pois essa fonte não tem rótulo de sujidade.

Consulte `docs/dados.md` para proveniência e limites de cada fonte e `docs/experimentos.md` para os resultados registrados.
