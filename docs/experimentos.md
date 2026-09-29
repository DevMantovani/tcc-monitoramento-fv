# Registro de experimentos

Preencha uma entrada antes de executar um experimento que será citado no artigo. Mantenha os resultados gerados em `artifacts/` localmente e registre aqui os valores relevantes.

## Modelo de registro

```md
## EXP-001 — título
- Data:
- Commit Git:
- Base: nome, URL/DOI, licença e período
- Cobertura: número de linhas, frequência, fuso e lacunas
- Filtros: limiar de irradiância, exclusões e justificativa
- Partições: datas de treino, validação e teste
- Modelo e parâmetros:
- Métricas de validação: MAE, RMSE, R²
- Resultado do indicador/alerta:
- Limitações e próxima decisão:
```

## EXP-001 — teste de integração com dados sintéticos

- Data: 29/09/2026
- Commit Git: posterior ao commit inicial; não representa experimento científico.
- Base: `pv-monitor demo`, 90 dias e 1.080 registros horários simulados.
- Cobertura: após o filtro de irradiância, 545 observações diurnas foram separadas cronologicamente em 327 de treino, 109 de validação e 109 de teste preservado.
- Cenário controlado: perda artificial de 20% nos cinco dias finais. Ela existe apenas para verificar o software.
- Modelos: Ridge (`alpha=1.0`) e Random Forest (300 árvores, `min_samples_leaf=5`).
- Métricas de validação: Ridge — MAE 0,069 kW, RMSE 0,088 kW, R² 0,996; Random Forest — MAE 0,076 kW, RMSE 0,098 kW, R² 0,996.
- Regra de alerta: perda média diária de pelo menos 12%, no mínimo 12 amostras válidas e três dias consecutivos.
- Resultado: o alerta foi ativado no terceiro dia consecutivo acima do limiar, compatível com o sinal artificial inserido.
- Limitação: métricas altas e alerta correto nesse cenário não demonstram desempenho em instalação real nem detecção de sujidade.
