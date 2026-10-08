# Metodologia da implementação

## Objetivo operacional

O sistema é concebido como apoio à decisão para identificar períodos em que a perda de geração associada à sujidade merece investigação e possível limpeza. Nesta fase, a análise é retrospectiva: ela usa medições já observadas, não prevê a geração de amanhã nem aciona uma limpeza automaticamente.

## Referência observada de sujidade

A primeira base de trabalho contém dois módulos idênticos: um lavado diariamente e outro exposto à poeira. Para observações com irradiância no plano de pelo menos 50 W/m² e potência positiva do módulo limpo, é calculada a fração:

```text
perda_por_sujidade = (potência_limpa − potência_exposta) / potência_limpa
```

O resultado é agregado por dia usando a mediana das observações válidas. A mediana reduz a influência de valores pontuais atípicos e torna a leitura do painel mais intuitiva. Esta medida descreve a diferença observada no experimento; ainda não é uma regra econômica de limpeza.

## Visualização e investigação

O painel local mostra a perda diária observada, as potências médias dos módulos limpo e exposto, e a densidade de poeira reconstruída fornecida pelos autores. Um limite selecionável na interface serve apenas para filtrar e discutir dias de maior perda. Ele deve ser descrito como **limite visual exploratório**, não como ponto de limpeza validado.

Uma recomendação operacional futura deverá combinar, no mínimo:

1. perda estimada ou observada e sua persistência;
2. custo e disponibilidade de limpeza;
3. valor da energia recuperável;
4. previsão de chuva, pois ela pode alterar o benefício da limpeza;
5. restrições locais de segurança e operação.

Na interface atual, a comparação econômica é deliberadamente retrospectiva: soma a energia não gerada observada no período selecionado e a multiplica pela tarifa ou valor de compensação informado pelo usuário. Esse montante é comparado ao custo de uma limpeza também informado pelo usuário. A tela não fixa preço de energia nem custo de limpeza, pois ambos variam por distribuidora, tipo de contrato, escala e operação. As tarifas de aplicação das distribuidoras podem ser consultadas nos [dados abertos da ANEEL](https://dadosabertos.aneel.gov.br/), mas a tarifa aplicável deve ser confirmada para a instalação estudada.

A precipitação é exibida como contexto, e não como uma regra binária de “painel limpo”. Estudos apontam que o efeito da chuva depende do material depositado e de outras condições; portanto, o sistema não deve assumir que qualquer evento de chuva elimina a sujidade. O tratamento está alinhado às orientações do [IEA PVPS sobre perdas por sujidade](https://iea-pvps.org/key-topics/soiling-losses-impact-on-the-performance-of-photovoltaic-power-plants/) e à evidência experimental do [NREL sobre limpeza incompleta pela chuva](https://www.nrel.gov/news/program/2023/nrel-research-finds-rain-not-enough-to-wash-pollen-from-solar-panels).

## Modelagem futura, sem vazamento de alvo

Modelos de regressão ou classificação poderão ser comparados somente depois de definir quais variáveis estariam disponíveis na instalação real no instante da decisão. A potência do painel limpo e uma medição de poeira usada como referência podem servir para construir ou avaliar o alvo, mas não devem ser usadas como entrada de um modelo que alegue funcionar onde essas referências não existem.

Quando a modelagem for iniciada, a separação deverá permanecer cronológica (treino, validação e teste) e as métricas serão registradas em `docs/experimentos.md`. A avaliação de uma política de limpeza não pode se limitar a MAE, RMSE ou R²: ela também precisa comparar energia recuperada, falsos alertas, limpezas evitadas e resultado econômico sob premissas explicitadas.

## Qualidade e limites dos dados

O pipeline não preenche lacunas silenciosamente. Ele valida datas, remove timestamps duplicados e restringe o cálculo de perda às condições em que há referência física utilizável. Antes de generalizar resultados, devem ser examinados período noturno, falhas de sensor, chuva, fuso horário, unidades, medição de poeira, capacidade dos módulos e diferenças entre local do estudo e instalação-alvo.
