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

### Seleção interna do estimador

Ridge e Random Forest são avaliados internamente apenas para escolher um estimador de potência limpa adequado à base de desenvolvimento. Essa etapa não é o objeto comparativo do TCC e não sustenta uma conclusão sobre qual técnica de aprendizado de máquina é superior em geral. Após a seleção pela validação cronológica, um único estimador é bloqueado e avaliado como parte do **monitor**: potência limpa esperada, perda estimada e alerta persistente.

## Visualização e investigação

O painel local separa a visão geral, a análise de dados, a validação científica e a simulação econômica/metodológica em abas. Essa organização impede que uma comparação experimental seja confundida com a operação normal do sistema proposto. A aba de análise usa exclusivamente o dataset público de Laghouat, com DOI, licença, método e checksum documentados, e exibe somente o recorte final preservado. Ela não aceita fontes arbitrárias. O fluxo de linha de comando para CSV permanece como base técnica para uma futura integração com inversor, medidor ou API.

Um limite selecionável na interface serve apenas para filtrar e discutir dias de maior perda. Ele deve ser descrito como **limite visual exploratório**, não como ponto de limpeza validado. O painel também oferece uma simulação econômica residencial opcional, com valores editáveis de energia, limpeza e recuperação assumida. Ela é uma análise de sensibilidade para interpretação do protótipo, não uma otimização financeira nem conclusão sobre uma residência real; as premissas estão registradas em `docs/economia.md`.

A precipitação é exibida como contexto, e não como uma regra binária de “painel limpo”. Estudos apontam que o efeito da chuva depende do material depositado e de outras condições; portanto, o sistema não deve assumir que qualquer evento de chuva elimina a sujidade. O tratamento está alinhado às orientações do [IEA PVPS sobre perdas por sujidade](https://iea-pvps.org/key-topics/soiling-losses-impact-on-the-performance-of-photovoltaic-power-plants/) e à evidência experimental do [NREL sobre limpeza incompleta pela chuva](https://www.nrel.gov/news/program/2023/nrel-research-finds-rain-not-enough-to-wash-pollen-from-solar-panels).

## Avaliação, sem vazamento de alvo

O protótipo avalia internamente candidatos simples para selecionar o estimador de potência limpa esperada, mas reporta como resultado central o desempenho do monitor bloqueado. As métricas incluem erro da potência limpa estimada e erro da perda por sujidade estimada. A separação é cronológica: treino (60%), validação (20%) e teste final preservado (20%). O estimador e a política de alerta são escolhidos na validação. A política explora limiares de 5%, 10%, 15% e 20%, combinados com persistência de um, dois ou três dias, e seleciona a maior medida F1; o resultado é congelado antes de uma única avaliação no teste final.

A avaliação do monitor não pode se limitar a MAE, RMSE ou R²: ela também deve verificar a estabilidade dos alertas, falsos alertas e atraso de detecção. A generalização só poderá ser defendida após validação externa em outra base ou dados de campo. O público-alvo inicial é residencial; adaptação para outras escalas requer nova avaliação.

## Teste externo de transferibilidade do monitor de sujidade

Em Dhaka, o mesmo fluxo é aplicado a outro experimento de painéis limpo e exposto. A arquitetura Ridge permanece fixa; não há busca por outro algoritmo. O Ridge é ajustado no período de desenvolvimento cronológico de Dhaka, pois transferir literalmente pesos entre instalações de dimensões e sensores diferentes seria metodologicamente inadequado. Primeiro, a política de alerta definida em Laghouat (15% por três dias) é aplicada sem alteração para testar a transferibilidade da regra e do fluxo do monitor. Como análise adicional, a política pode ser recalibrada somente na validação local, preservando o teste final.

Os dois resultados devem ser informados: a política transferida não encontrou dias positivos no teste final de Dhaka, mas gerou 26 alertas falsos; a recalibração local também teve baixo F1 (0,043) no teste final. A MAE da perda estimada foi 41,46 pontos percentuais e o R² da perda foi negativo. Portanto, a versão atual do monitor não demonstrou generalização automática para essa fonte. Isso reforça que sensores, qualidade dos dados, referências de limpeza e limiares precisam ser validados por instalação.

## Avaliação externa limitada à potência esperada

A fonte complementar de 2023--2024 contém potência observada por inversor, irradiância no plano inclinado e temperatura ambiente, mas não contém um rótulo independente de sujidade. Nela, o pipeline seleciona o modelo pela validação cronológica e avalia uma única vez o modelo selecionado no teste final preservado. A variável-alvo é a potência observada; previsões pré-calculadas no arquivo-fonte são excluídas.

Esse experimento mede a reprodutibilidade da **previsão de potência** em outra instalação. Ele não mede perda por sujidade, não gera F1 de alertas e não justifica um limiar de limpeza. A temperatura ambiente também é identificada como tal, sem ser confundida com temperatura do módulo.

## Qualidade e limites dos dados

O pipeline não preenche lacunas silenciosamente. Ele valida datas, remove timestamps duplicados e restringe o cálculo de perda às condições em que há referência física utilizável. Antes de generalizar resultados, devem ser examinados período noturno, falhas de sensor, chuva, fuso horário, unidades, medição de poeira, capacidade dos módulos e diferenças entre local do estudo e instalação-alvo.

No fluxo operacional, essa verificação é registrada em JSON antes da geração do alerta: linhas com data inválida, campos numéricos inválidos, timestamps duplicados, potência negativa e irradiância abaixo do limiar são quantificadas. A saída diária registra a potência esperada, a potência observada, a perda estimada, a persistência e uma ação de inspeção. Ela não converte um alerta em diagnóstico de sujidade.
