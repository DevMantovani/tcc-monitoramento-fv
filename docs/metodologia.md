# Metodologia da implementação

## Objetivo operacional

Estimar a potência que o sistema deveria produzir no mesmo instante das condições ambientais observadas. A diferença entre potência prevista e medida forma um indicador de desempenho relativo. A análise é retrospectiva; não equivale a prever a geração de amanhã.

## Entradas, saída e hipótese

Na primeira versão, as entradas são irradiância no plano dos módulos, temperatura do módulo e a interação entre ambas. A saída é `power_kw`. Ridge é o modelo-base interpretável e Random Forest é o modelo não linear de comparação. A hipótese de trabalho é que uma perda adicional, consistente após filtros e por vários dias, merece investigação. Ela não prova que a causa seja sujidade.

## Separação temporal

O CSV é ordenado por `timestamp` e dividido cronologicamente em treino (60%), validação (20%) e teste final (20%). Nenhum registro futuro é misturado no treino. O escalonamento do Ridge é ajustado somente com treino; isso evita vazamento de informações do futuro. As datas reais de cada partição devem ser registradas em `docs/experimentos.md` antes da abertura do teste final.

## Qualidade dos dados

Registros sem as quatro colunas obrigatórias, com potência negativa, horário inválido ou irradiância abaixo do limiar configurado são excluídos e contabilizados. Lacunas não são preenchidas automaticamente. Antes de experimentos reais, conferir: fuso horário, unidade, frequência, duplicidades, período noturno, falhas de sensor, potência nominal e possíveis registros de limpeza/chuva.

## Indicador e alerta

Para cada observação válida, o pipeline calcula:

```text
fração_de_perda = (potência_prevista - potência_observada) / potência_prevista
```

O denominador só é usado acima de uma potência mínima configurável. Em seguida, agrega a média diária e exige quantidade mínima de amostras e dias consecutivos acima do limiar. A saída se chama `alerta_perda_adicional`; não `alerta_sujidade`.

## Avaliação

A etapa de regressão informa MAE, RMSE e R². Caso exista uma referência independente de limpeza ou um cenário semissintético com perda conhecida, os alertas podem ser avaliados como classificação, por exemplo com precisão, sensibilidade e F1. Sem rótulo confiável, relatar somente consistência do indicador, cobertura e limitações — não acurácia de detecção de sujidade.
