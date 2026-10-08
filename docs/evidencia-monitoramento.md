# Evidência operacional do monitor

O resultado principal do projeto é o comportamento do **monitor de perdas por sujidade**: estimar a potência limpa esperada, calcular a perda estimada e gerar um alerta persistente para investigação. A escolha entre estimadores ocorre somente dentro da validação e não é apresentada como comparação de técnicas de aprendizado de máquina.

## Como gerar a análise

Depois de produzir o teste final preservado, execute:

```bash
pv-monitor analyze-monitoring-evidence \
  --input data/processed/laghouat_2022.csv \
  --final-metrics artifacts/laghouat_final/metrics_test.json \
  --output artifacts/laghouat_monitoring_evidence
```

O comando refaz somente a aplicação do estimador e da política já bloqueados sobre o mesmo teste final. Ele não compara candidatos, não escolhe novo modelo e não altera limiar ou persistência.

## Saídas

| Arquivo | Pergunta respondida |
|---|---|
| `condition_performance.csv` | Em quais faixas de irradiância o erro de perda do monitor é maior ou menor? |
| `monthly_alert_stability.csv` | Como a política de alerta bloqueada se comportou em cada mês do teste final? |
| `context_correlations.csv` | Quais relações exploratórias existem entre perda observada e contexto ambiental? |
| `monitoring_evidence.json` | Qual foi a cobertura de dados, o estimador bloqueado e a política aplicada? |

## Resultados desta execução

No teste final de Laghouat, o erro absoluto médio da perda estimada foi de 0,80 ponto percentual na faixa de 50–299 W/m² e ficou entre 0,53 e 0,56 ponto percentual acima de 300 W/m². Portanto, o monitor é menos preciso em condições de menor irradiância dentro do recorte elegível; essa condição deve aparecer como ressalva operacional.

Com a política bloqueada de 15% por três dias, julho de 2022 teve F1 de 0,897 e agosto teve F1 de 1,000 no teste final. Esses recortes somam somente 35 dias e pertencem à mesma instalação experimental, portanto não são validação independente.

A associação de Spearman entre perda observada e a densidade de poeira reconstruída foi 0,734. Esse resultado é coerente com o contexto experimental, mas não prova causalidade nova: a densidade reconstruída foi fornecida na própria base e não é entrada do modelo operacional atual.

## Limites

As estratificações não aumentam a cobertura geográfica, não substituem dados residenciais reais e não provam que chuva, umidade, vento ou nuvens sejam causas isoladas da perda. Elas tornam visível onde o monitor funciona melhor ou pior dentro da única base supervisionada disponível.
