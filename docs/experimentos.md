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

## EXP-002 — preparação e inspeção da base supervisionada de Laghouat

- Data: 08/10/2026
- Commit Git: a registrar no commit desta etapa.
- Base: *Hourly PV Power and Dust Accumulation Dataset — Laghouat, Algeria, February–August 2022*, DOI [10.17632/4jdt83yy43.3](https://doi.org/10.17632/4jdt83yy43.3), CC BY 4.0.
- Cobertura: 4.368 observações horárias entre 17/02/2022 e 17/08/2022, sem timestamps duplicados.
- Filtros: a perda foi calculada somente com irradiância no plano ≥ 50 W/m² e potência positiva do painel limpo; 1.860 registros diurnos ficaram elegíveis.
- Modelo e parâmetros: não aplicável nesta etapa. Não foi treinado modelo de aprendizado de máquina.
- Resultado descritivo: mediana de perda 15,27%; média 13,43%; percentil 90 22,45%.
- Limitações: referência de painel lavado diariamente; um local e seis meses; só 48 medidas diretas de poeira e série horária reconstruída por PCHIP.
- Próxima decisão: validar os alertas do monitor e procurar uma fonte complementar; otimização econômica de limpeza está fora do escopo do MVP.

## EXP-003 — validação inicial do monitor de perdas por sujidade

- Data: 08/10/2026
- Commit Git: a registrar no commit desta etapa.
- Base: mesma base de Laghouat do EXP-002; o painel limpo foi usado apenas como alvo supervisionado e referência de validação.
- Entradas operacionais do modelo: irradiância no plano, temperatura de célula e interação entre ambas. A potência do painel limpo, a perda observada e a densidade de poeira reconstruída não entraram como variáveis preditoras.
- Sinal monitorado: potência do painel exposto, representando a potência que seria medida pelo sistema em operação.
- Partições: cronológicas, 60% treino, 20% validação e 20% teste preservado.
- Modelos: Ridge e Random Forest.
- Métrica de validação da perda estimada: Ridge — MAE 0,00661 (0,66 ponto percentual), RMSE 0,00851 e R² 0,989; Random Forest — MAE 0,02308 (2,31 pontos percentuais), RMSE 0,03125 e R² 0,851.
- Resultado: nesta validação cronológica, Ridge teve o menor erro de perda estimada. O teste final permanece sem uso para escolha de modelo.
- Limitações: um único local e período; a potência limpa de referência está disponível nesta base, mas não numa implantação comum. A próxima etapa deve validar o modelo em outra fonte ou em dados de campo e definir como períodos pós-limpeza serão identificados para recalibração.

## EXP-004 — calibração de alertas e teste final preservado

- Data: 08/10/2026
- Commit Git: a registrar no commit desta etapa.
- Modelo bloqueado: Ridge, selecionado pela menor MAE de perda estimada na validação (EXP-003).
- Calibração: somente na validação, avaliando limiares de 5%, 10%, 15% e 20% com persistência de um, dois ou três dias. A seleção por F1 escolheu 15% por três dias consecutivos; na validação, precisão, sensibilidade e F1 foram 1,000 (33 dias positivos).
- Teste final: o modelo foi refitado uma vez com treino e validação, sem alterar política; o último período cronológico permaneceu separado até a execução.
- Métricas do teste: MAE da potência limpa esperada 0,000291 kW; MAE da perda estimada 0,00632 (0,63 ponto percentual); precisão dos alertas 0,906; sensibilidade 1,000; F1 0,951; 29 dias verdadeiros positivos, 3 falsos positivos e nenhum falso negativo.
- Interpretação: os resultados demonstram desempenho promissor **nesta base experimental**, não eficácia comprovada em residências brasileiras ou em outra localidade.
- Próxima decisão: produzir gráficos e tabelas reproduzíveis do teste final e buscar validação complementar em fonte externa.

## EXP-005 — avaliação externa da estimação de potência em dados de 2023--2024

- Data: 08/10/2026
- Commit Git: a registrar no commit desta etapa.
- Base: *Photovoltaic Inverter Production and Meteorological data*, DOI [10.5281/zenodo.17775544](https://doi.org/10.5281/zenodo.17775544), CC BY 4.0. Autores vinculados à University of Cyprus e University of Nicosia; arquivo associado a publicação e com checksum divulgado.
- Recorte: `inverter1` (107,1 m² declarados), 3.185 registros horários de 03/11/2023 a 25/06/2024. Depois do filtro de irradiância no plano inclinado ≥ 50 W/m², 1.316 registros foram preservados. Há lacunas de cerca de 33 e 69 dias.
- Entradas: irradiância global no plano inclinado, temperatura ambiente e interação entre ambas. Alvo: potência observada do inversor, em kW. A coluna `energy`, uma previsão já fornecida pela fonte, foi excluída para impedir vazamento.
- Partições: cronológicas; 789 registros de treino (03/11/2023--31/01/2024), 263 de validação (31/01/2024--03/05/2024) e 264 de teste final (03/05/2024--24/06/2024).
- Seleção pela validação: Ridge — MAE 2,423 kW, RMSE 3,017 kW, R² 0,482; Random Forest — MAE 2,317 kW, RMSE 2,795 kW, R² 0,555. Random Forest foi selecionado sem acessar o teste.
- Teste final: após refit com treino e validação, Random Forest obteve MAE 2,469 kW, RMSE 2,910 kW e R² 0,540.
- Interpretação: a fonte mostra que o fluxo de previsão de potência pode ser executado em outra instalação e período mais recente, mas seu desempenho é moderado e não equivale a desempenho de detecção de sujidade.
- Limitações: uma instalação não residencial, lacunas temporais e dados meteorológicos externos; não há painel limpo, rótulo de perda por sujidade ou evento de limpeza. Não foram calculados alertas nem F1 neste experimento.

## EXP-006 — materiais reproduzíveis dos resultados consolidados

- Data: 08/10/2026
- Commit Git: a registrar no commit desta etapa.
- Entradas: artefatos preservados de validação e teste final dos EXP-003, EXP-004 e EXP-005.
- Procedimento: o comando `pv-monitor generate-results` transforma as métricas já produzidas em duas tabelas CSV e três figuras em PNG/SVG. Não há novo treino, seleção de modelo, calibração de limiar ou acesso aos dados brutos.
- Materiais: comparação de MAE na validação; série de perda observada e estimada no teste final de Laghouat; métricas de precisão, sensibilidade e F1 dos alertas persistentes; tabelas distintas para validação e teste final.
- Controle contra interpretação indevida: a figura da fonte Zenodo apresenta somente erro de potência; ela não é rotulada como validação de sujidade. Os resultados continuam restritos às bases públicas descritas nos experimentos anteriores.
- Limitação: as figuras resumem os experimentos já executados; não adicionam evidência de generalização para residências brasileiras.

## EXP-007 — evidência operacional do monitor selecionado

- Data: 08/10/2026
- Commit Git: a registrar no commit desta etapa.
- Objetivo: examinar o monitor bloqueado por condições operacionais e estabilidade temporal, sem comparar algoritmos nem selecionar novos parâmetros.
- Entradas: recorte de teste final preservado do EXP-004, modelo Ridge e política de 15% por três dias definidos antes do teste.
- Cobertura: 372 observações horárias elegíveis, agregadas em 35 dias entre 14/07/2022 e 17/08/2022.
- Resultado por irradiância: MAE da perda de 0,80 ponto percentual entre 50–299 W/m²; entre 0,53 e 0,56 ponto percentual acima de 300 W/m². O monitor apresenta menor precisão próxima ao limite inferior de irradiância.
- Resultado por mês: julho (18 dias) obteve F1 0,897, com 3 falsos positivos e nenhum falso negativo; agosto (17 dias) obteve F1 1,000. Os dois períodos pertencem ao mesmo teste final e não são validações independentes.
- Contexto exploratório: a perda observada teve correlação de Spearman 0,734 com a densidade de poeira reconstruída da fonte. A variável não foi usada como entrada e a associação não comprova causalidade.
- Limitação: o relatório estratifica uma única base experimental e não acrescenta uma nova instalação, localidade ou evento de limpeza.

## EXP-008 — teste externo de transferibilidade em Dhaka

- Data: 08/10/2026
- Commit Git: a registrar no commit desta etapa.
- Base: *A comprehensive dataset for monitoring photovoltaic panels and weather parameters in urban Bangladesh*, DOI [10.17632/g6pxf8nnt6.2](https://doi.org/10.17632/g6pxf8nnt6.2), CC BY 4.0. Dois painéis de 20 W, um limpo regularmente e outro exposto; 295 arquivos diários disponíveis entre 01/11/2019 e 30/10/2020.
- Preparação auditável: 408.059 leituras de 30 segundos foram agregadas em 3.720 registros horários; 3.357 registros diurnos ficaram elegíveis. Cabeçalhos variantes e datas ambíguas foram normalizados pelo código de preparação e documentados em `dados.md`.
- Protocolo: Ridge permanece como estimador selecionado internamente e é ajustado no período cronológico de desenvolvimento de Dhaka; não há transferência literal de pesos entre painéis. O teste principal transfere, sem alteração, a política de 15% por três dias escolhida em Laghouat. O conjunto é separado cronologicamente e o último período contém 672 observações horárias entre 30/08/2020 e 30/10/2020.
- Resultado de potência limpa: MAE 0,002324 kW (2,32 W), RMSE 0,002814 kW e R² 0,630.
- Resultado de perda: MAE 0,4146 (41,46 pontos percentuais), RMSE 0,5188 e R² -31,02. A política transferida gerou 26 alertas falsos e nenhum verdadeiro positivo porque não houve dias positivos no teste acima de 15% por três dias.
- Calibração local adicional: mesmo escolhendo o melhor limiar somente na validação (5% por um dia; F1 0,197 na validação), o teste final teve F1 0,043, com 1 verdadeiro positivo e 45 falsos positivos.
- Interpretação: o monitor atual não generaliza automaticamente de Laghouat para Dhaka. A diferença de sensores, qualidade, clima, configuração dos painéis e definição operacional de referência impede tratar o limiar ou o desempenho de Laghouat como universais.
- Limitação: resultado externo negativo não prova que a abordagem seja inviável em toda instalação; ele mostra que esta implementação mínima precisa de calibração local, controle de qualidade e validação adicional antes de uso residencial.

## EXP-009 — sensibilidade à duração da calibração pós-limpeza

- Data: 08/10/2026
- Commit Git: a registrar no commit desta etapa.
- Base: Laghouat 2022, DOI [10.17632/4jdt83yy43.3](https://doi.org/10.17632/4jdt83yy43.3), CC BY 4.0.
- Protocolo: o painel limpo foi usado exclusivamente na janela inicial para simular uma referência pós-limpeza. Ridge foi ajustado com 14, 28, 42 ou 60 dias iniciais; as observações futuras do painel exposto foram avaliadas contra a referência limpa independente. A política permaneceu fixa em 15% por três dias.
- Resultados: 14 dias — MAE da perda 8,59 p.p., F1 0,847 e 27 falsos alertas; 28 dias — 5,57 p.p., F1 0,867 e 23 falsos alertas; 42 dias — 4,41 p.p., F1 0,872 e 22 falsos alertas; 60 dias — 2,84 p.p., F1 0,904 e 16 falsos alertas. Em todos os cenários, a sensibilidade foi 1,000 e não houve falsos negativos.
- Interpretação: mais dados limpos históricos melhoraram a referência de potência e reduziram falsos alertas no experimento. O resultado não define uma duração de calibração universal.
- Limitação: o painel limpo é uma aproximação experimental de uma instalação recém-limpa; a avaliação não representa uma residência brasileira ou uma operação em campo.
