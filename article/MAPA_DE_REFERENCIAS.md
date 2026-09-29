# Mapa de referências e cobertura do artigo

Revisão de 28/09/2026. Documento auxiliar para conferência com o orientador; não integra o corpo do artigo.

A bibliografia de `TCCFinal.tex` passou de 12 para 26 fontes: 15 artigos de periódicos, um preprint, dois relatórios técnicos, uma publicação metrológica institucional, seis páginas de documentação de software e um conjunto de dados. As 14 fontes adicionadas estão citadas no texto. Não foi usado `\nocite{*}` para aumentar artificialmente a lista.

## Como interpretar as citações

- Conceitos, descrições de algoritmos, equações padronizadas e resultados de terceiros devem ter uma fonte que sustente a afirmação específica.
- As citações indiretas não significam transcrição nem aprovação de todo o conteúdo de uma publicação.
- Objetivos, hipótese, escolhas de entradas, regra de persistência e recortes de avaliação são propostas deste TCC. As fontes justificam sua fundamentação, sem provar antecipadamente a eficácia do protocolo.
- As equações do desvio e da agregação diária foram identificadas como definições operacionais do estudo. A relação entre potência observada e modelada tem antecedentes, mas não se atribui a outro autor a regra completa de alerta aqui proposta.
- O resumo provisório sintetiza o próprio projeto. Os fundamentos correspondentes são citados no corpo do texto; não se inseriram citações em cada frase do resumo.
- Futuras tabelas e gráficos com resultados próprios precisarão informar dados, unidades, procedimento e origem. Uma referência externa não pode substituir os experimentos pendentes.

## As 14 fontes acrescentadas

| Chave BibTeX | Referência e acesso | Aplicação no artigo | Conteúdo consultado nesta revisão |
|---|---|---|---|
| `king2004` | King, Boyson e Kratochvil (2004). **Photovoltaic Array Performance Model**. Sandia, SAND2004-3535. [DOI](https://doi.org/10.2172/919131); [PDF institucional](https://www.osti.gov/servlets/purl/919131). | Influência ambiental; distinção entre temperaturas; irradiância no plano dos módulos. | Relatório: definições das variáveis, modelo térmico e discussão da irradiância. |
| `dobos2014` | Dobos (2014). **PVWatts Version 5 Manual**. NREL/TP-6A20-62641. [DOI](https://doi.org/10.2172/1158421); [registro institucional](https://research-hub.nlr.gov/en/publications/pvwatts-version-5-manual/). | Fundamentação física complementar e distinção entre saída CC e CA. | Resumo institucional e trechos indexados do manual sobre os submodelos e o inversor. O PDF integral não pôde ser recuperado nesta revisão; a equação CC foi conferida também na documentação oficial do pvlib já citada. |
| `li2024` | Li, Chen e Jain (2024). **Power modeling of degraded PV systems: Case studies using a dynamically updated physical model (PV-Pro)**. Renewable Energy, 236, 121493. [DOI](https://doi.org/10.1016/j.renene.2024.121493); [repositório dos autores](https://escholarship.org/uc/item/4f75n0bx). | Monitoramento com ambiente observado, previsão futura, comparação de modelos e preparação de dados. | Texto do artigo: introdução e método, incluindo variáveis e comparação com modelos de ML. Não foram transferidos seus resultados numéricos ao TCC. |
| `skomedal2020` | Skomedal e Deceglie (2020). **Combined Estimation of Degradation and Soiling Losses in Photovoltaic Systems**. IEEE Journal of Photovoltaics, 10(6), 1788–1796. [DOI](https://doi.org/10.1109/JPHOTOV.2020.3018219); [registro institucional](https://research-hub.nlr.gov/en/publications/combined-estimation-of-degradation-and-soiling-losses-in-photovol-2/). | Coexistência de sujidade, degradação e sazonalidade; limite da atribuição causal do desvio. | Resumo e metadados institucionais. A redação se limita à decomposição explicitamente descrita no resumo; não reproduz detalhes internos do algoritmo. |
| `mejia2013` | Mejia e Kleissl (2013). **Soiling losses for solar photovoltaic systems in California**. Solar Energy, 95, 357–363. [DOI](https://doi.org/10.1016/j.solener.2013.06.028); [texto dos autores](https://escholarship.org/uc/item/5kd297nm). | Evidência empírica sobre chuva e recuperação do desempenho; cuidado ao transferir critérios entre instalações. | Resumo e método, particularmente o critério de evento de chuva. Não foi adotado um limiar de precipitação universal. |
| `hoerl1970` | Hoerl e Kennard (1970). **Ridge Regression: Biased Estimation for Nonorthogonal Problems**. Technometrics, 12(1), 55–67. [DOI](https://doi.org/10.1080/00401706.1970.10488634); [texto em repositório acadêmico](https://www.stat.cmu.edu/technometrics/70-79/VOL-12-01/v1201055.pdf). | Origem e fundamentação da regressão Ridge usada como referência. | Resumo e formulação da estimação regularizada. A referência é a publicação de 1970, não sua republicação de 2000 nem a data de digitalização. |
| `cerqueira2020` | Cerqueira, Torgo e Mozetič (2020). **Evaluating time series forecasting models: an empirical study on performance estimation methods**. Machine Learning, 109, 1997–2028. [DOI e página da editora](https://doi.org/10.1007/s10994-020-05910-7). | Justificativa da avaliação temporal e atenção às características da série. | Resumo e metadados da editora. O artigo não é apresentado como prova de que qualquer validação cruzada é inválida em séries temporais. |
| `kapoor2023` | Kapoor e Narayanan (2023). **Leakage and the reproducibility crisis in machine-learning-based science**. Patterns, 4(9), 100804. [DOI](https://doi.org/10.1016/j.patter.2023.100804); [texto depositado na NSF](https://par.nsf.gov/servlets/purl/10513990). | Vazamento de dados, variáveis que reproduzem o alvo, separação entre preparação e teste, registro das decisões. | Texto e material de apoio: tipos de vazamento e documentação da avaliação. Não fundamenta sozinho a eficácia do detector fotovoltaico. |
| `hyndman2006` | Hyndman e Koehler (2006). **Another look at measures of forecast accuracy**. International Journal of Forecasting, 22(4), 679–688. [DOI](https://doi.org/10.1016/j.ijforecast.2006.03.001); [página do autor](https://robjhyndman.com/publications/another-look-at-measures-of-forecast-accuracy/). | Métricas de erro e instabilidade de razões com valores próximos de zero. | Texto disponibilizado pelo autor, especialmente discussão de erros percentuais. Dados bibliográficos da versão publicada de 2006; o manuscrito disponível é datado de 2005. |
| `saito2015` | Saito e Rehmsmeier (2015). **The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets**. PLOS ONE, 10(3), e0118432. [Artigo](https://doi.org/10.1371/journal.pone.0118432). | Avaliação da detecção quando eventos e dias sem evento tiverem frequências distintas. | Resumo e discussão de precisão e sensibilidade em classes desbalanceadas. A aplicação ao TCC é uma escolha fundamentada, não um resultado do artigo sobre painéis solares. |
| `hevner2004` | Hevner et al. (2004). **Design Science in Information Systems Research**. MIS Quarterly, 28(1), 75–106. [DOI](https://doi.org/10.2307/25148625); [registro da AIS](https://aisel.aisnet.org/misq/vol28/iss1/6/). | Relação entre construção e avaliação do artefato computacional. | Resumo e metadados do periódico. Não se afirma adesão integral a um método de design science ainda não executado. |
| `bipm2026` | Bureau International des Poids et Mesures (2026). **The International System of Units (SI)**. 9ª ed., versão 4.01. [Publicação oficial](https://www.bipm.org/en/publications/si-brochure); [DOI](https://doi.org/10.59161/AUEZ1291). | Unidades de potência e energia; coerência dimensional. | Publicação e definições de unidades. A 9ª edição é de 2019; a versão consultada foi revista em junho de 2026. |
| `sklearn_metricas` | Scikit-learn. **Metrics and scoring: quantifying the quality of predictions**. [Documentação oficial](https://scikit-learn.org/stable/modules/model_evaluation.html). | Definições de MAE, RMSE, R², precisão, sensibilidade e F1. | Seções de métricas de regressão e classificação. Fonte técnica para as fórmulas e a implementação, identificada como documentação. |
| `sklearn_praticas` | Scikit-learn. **Common pitfalls and recommended practices**. [Documentação oficial](https://scikit-learn.org/stable/common_pitfalls.html). | Ajustar transformações no treinamento e aplicá-las ao teste sem reajuste. | Seção sobre vazamento durante o pré-processamento. Complementa a fundamentação científica de Kapoor e Narayanan. |

## Cobertura das 12 fontes já presentes

| Chave | Função mantida |
|---|---|
| `bessa2021` | Definição, monitoramento e limitações da análise de sujidade. Revisão em periódico. |
| `breiman2001` | Fundamentação do Random Forest. Artigo original. |
| `deceglie2018` | Estimativa de sujidade por desempenho e validação independente. Artigo. |
| `Tramontin_Rampinelli_2024` | Estudo brasileiro antes/depois de limpeza e regressão. Artigo. |
| `kalimeris2023data` | Seleção da referência e regressão para sujidade. Mantido explicitamente como preprint. |
| `tsanakas2025` | Modelagem retrospectiva e previsão ambiental de perdas. Artigo. |
| `pedregosa2011` | Biblioteca scikit-learn e tarefas de aprendizagem supervisionada. Artigo. |
| `pvdaq2021` | Proveniência da base candidata; não comprova que ela já foi baixada ou validada. Conjunto de dados. |
| `rdtools_exemplo` | Fluxo de análise e fator artificial de sujidade no exemplo. Documentação técnica. |
| `sklearn_rf` | Parâmetros e comportamento da implementação da floresta. Documentação técnica. |
| `sklearn_temporal` | Funcionamento e hipóteses de TimeSeriesSplit. Documentação técnica. |
| `pvlib_pvwatts` | Implementação da equação de potência CC do PVWatts. Documentação técnica. |

Os endereços completos e dados bibliográficos dessas fontes estão em `referencias_final.bib` e nas referências do PDF.

## Limites da revisão e continuidade

Esta ampliação é uma revisão dirigida às afirmações e decisões do projeto, não uma revisão sistemática exaustiva. Parte das fontes foi consultada em texto completo nas seções pertinentes e parte em resumo oficial, conforme registrado acima. Não se presume leitura integral onde ela não ocorreu.

Antes da entrega final, os autores devem conferir as paráfrases contra os textos originais, aprofundar a leitura dos trabalhos relacionados e discutir a delimitação com o orientador. A quantidade de referências não substitui sua pertinência e qualidade. A escolha definitiva da base, os parâmetros de filtragem, os limiares e qualquer alegação de desempenho dependem das próximas etapas.
