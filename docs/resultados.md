# Materiais de resultados reproduzíveis

Este projeto separa a escolha de modelos na validação da avaliação final em teste preservado. As tabelas e figuras devem ser sempre geradas a partir dos artefatos dessa execução, sem copiar valores manualmente para o artigo.

## Como gerar

Após executar `pv-monitor reproduce-public-experiments`, rode:

```bash
pv-monitor generate-results \
  --input-dir artifacts \
  --output artifacts/result_materials
```

O diretório de saída não é versionado porque pode ser refeito localmente. O comando lê resultados já salvos; não baixa dados, não treina modelos nem muda as métricas.

## Saídas

| Arquivo | Conteúdo | Uso adequado |
|---|---|---|
| `table_validation_comparison.csv` | MAE, RMSE e R² dos candidatos na validação. | Documentar a escolha interna do estimador, sem usar o teste final e sem tratá-la como resultado central do TCC. |
| `table_final_metrics.csv` | Métricas do teste final bloqueado e dos alertas persistentes. | Relatar a avaliação final da base de Laghouat e a avaliação externa de potência. Interpretar F1 junto com prevalência, especificidade e regras de referência. |
| `figure_validation_comparison.png/.svg` | MAE de validação para a perda estimada em Laghouat e para potência no Zenodo. | Auditoria da escolha interna; não usar como ranking de técnicas. |
| `figure_laghouat_test_daily_loss.png/.svg` | Perda diária observada e estimada no teste final, com alertas persistentes e limiar bloqueado. | Ilustrar o comportamento do monitor no experimento supervisionado. |
| `figure_laghouat_alert_metrics.png/.svg` | Precisão, sensibilidade e F1 no teste final. | Resumir o desempenho da política de alertas. |

Prefira SVG no artigo quando o editor aceitar, pois permite redimensionamento sem perda de nitidez; PNG é a alternativa para apresentação e editores que não aceitam SVG.

## Limites de interpretação

Os materiais refletem somente os experimentos públicos documentados em [experimentos.md](experimentos.md). Laghouat fornece o par de painéis limpo/exposto necessário para validar a perda por sujidade. Como o teste final de Laghouat tem alta proporção de dias positivos, as métricas de alerta precisam ser comparadas com baselines simples, como alertar sempre; F1 isolado não é evidência suficiente de ganho operacional. A fonte Zenodo de 2023--2024 avalia exclusivamente a estimativa de potência em outra instalação e não possui rótulo de sujidade, histórico de limpeza ou alertas. O teste externo em Dhaka é relatado separadamente porque expõe falha de transferência e não deve ser misturado às figuras positivas de Laghouat.

Assim, os gráficos não comprovam eficácia em uma residência brasileira nem autorizam recomendar limpeza automática. Eles são evidência reproduzível do protótipo nas condições e fontes declaradas.
