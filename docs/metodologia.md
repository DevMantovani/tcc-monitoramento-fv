# Metodologia da implementação

## Objetivo operacional

O projeto é um sistema de **monitoramento de perdas por sujidade em sistemas fotovoltaicos com aprendizado de máquina**. Ele estima a potência que o sistema deveria produzir em condição limpa, dadas as condições ambientais, e a compara com a potência realmente medida. A diferença forma um indicador de perda que pode estar associada à sujidade e deve ser investigada junto com outras causas possíveis, como sombreamento, falhas e erros de medição.

Nesta fase, a análise é retrospectiva: ela usa medições já observadas, não prevê a geração de amanhã nem aciona uma limpeza automaticamente.

## Referência supervisionada para desenvolver o monitor

A base de desenvolvimento contém dois módulos idênticos: um lavado diariamente e outro exposto à poeira. Para observações com irradiância no plano de pelo menos 50 W/m² e potência positiva do módulo limpo, é calculada a fração:

```text
perda_observada = (potência_limpa − potência_exposta) / potência_limpa
```

Essa perda observada é o rótulo usado para validar o monitor; o painel limpo não deve ser entendido como parte necessária da futura instalação monitorada. O resultado é agregado por dia usando a mediana das observações válidas, que reduz a influência de valores pontuais atípicos e torna a leitura do painel mais intuitiva.

## Fluxo de aprendizado de máquina e monitoramento

1. Durante o desenvolvimento, o modelo recebe irradiância, temperatura do módulo e sua interação e aprende a estimar a potência limpa de referência.
2. Em uma instalação monitorada, o modelo recebe essas variáveis ambientais e a potência medida do próprio sistema.
3. A perda estimada é calculada por `(potência limpa esperada − potência medida) / potência limpa esperada`.
4. A base de Laghouat permite comparar essa estimativa com a perda observada entre painel limpo e exposto, usando separação cronológica entre treino, validação e teste.

Assim, `P_clean` é permitido como alvo supervisionado apenas na fase experimental. Ele não entra como variável de entrada do modelo nem é necessário na operação do monitor. A densidade de poeira reconstruída também é mantida para análise e não é usada como atalho para a predição.

## Visualização e investigação

O painel local apresenta primeiro as métricas de validação cronológica do modelo e, em separado, os gráficos do experimento usados como referência. Essa separação impede que uma comparação de laboratório seja confundida com a operação normal do sistema proposto.

Um limite selecionável na interface serve apenas para filtrar e discutir dias de maior perda. Ele deve ser descrito como **limite visual exploratório**, não como ponto de limpeza validado.

Uma recomendação operacional futura deverá combinar, no mínimo:

1. perda estimada e sua persistência;
2. custo e disponibilidade de limpeza;
3. valor da energia recuperável;
4. previsão de chuva, pois ela pode alterar o benefício da limpeza;
5. restrições locais de segurança e operação.

Na interface atual, a comparação econômica é deliberadamente retrospectiva: soma a energia não gerada observada no período selecionado e a multiplica pela tarifa ou valor de compensação informado pelo usuário. Esse montante é comparado ao custo de uma limpeza também informado pelo usuário. A tela não fixa preço de energia nem custo de limpeza, pois ambos variam por distribuidora, tipo de contrato, escala e operação. As tarifas de aplicação das distribuidoras podem ser consultadas nos [dados abertos da ANEEL](https://dadosabertos.aneel.gov.br/), mas a tarifa aplicável deve ser confirmada para a instalação estudada.

A precipitação é exibida como contexto, e não como uma regra binária de “painel limpo”. Estudos apontam que o efeito da chuva depende do material depositado e de outras condições; portanto, o sistema não deve assumir que qualquer evento de chuva elimina a sujidade. O tratamento está alinhado às orientações do [IEA PVPS sobre perdas por sujidade](https://iea-pvps.org/key-topics/soiling-losses-impact-on-the-performance-of-photovoltaic-power-plants/) e à evidência experimental do [NREL sobre limpeza incompleta pela chuva](https://www.nrel.gov/news/program/2023/nrel-research-finds-rain-not-enough-to-wash-pollen-from-solar-panels).

## Avaliação, sem vazamento de alvo

O protótipo compara Ridge e Random Forest como estimadores de potência limpa esperada. As métricas incluem erro da potência limpa estimada e erro da perda por sujidade estimada. A separação é cronológica: treino (60%), validação (20%) e teste final preservado (20%). O teste final não é usado para escolher modelo ou limiar.

A avaliação de uma política de limpeza não pode se limitar a MAE, RMSE ou R²: ela também precisa comparar energia recuperada, falsos alertas, limpezas evitadas e resultado econômico sob premissas explicitadas. A generalização só poderá ser defendida após validação externa em outra base ou dados de campo.

## Qualidade e limites dos dados

O pipeline não preenche lacunas silenciosamente. Ele valida datas, remove timestamps duplicados e restringe o cálculo de perda às condições em que há referência física utilizável. Antes de generalizar resultados, devem ser examinados período noturno, falhas de sensor, chuva, fuso horário, unidades, medição de poeira, capacidade dos módulos e diferenças entre local do estudo e instalação-alvo.
