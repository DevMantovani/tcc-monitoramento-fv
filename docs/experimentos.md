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
