# Mapa de referências e validação de uso

Revisado em 08/10/2026. Este é um arquivo auxiliar, separado do artigo, para conferir se cada afirmação externa possui fonte adequada. Ele não substitui a leitura das publicações originais nem a lista de referências gerada pelo LaTeX.

## Critério adotado

- **Artigos, relatórios e conjuntos de dados com DOI** são as fontes preferidas para afirmações científicas e para a proveniência dos dados.
- **Documentação oficial** é usada apenas para comportamento de bibliotecas, métricas ou modelos de software; não é apresentada como evidência de eficácia do protótipo.
- **Resultados do TCC** são identificados como elaboração própria e apontam para os dados, o protocolo e os artefatos reproduzíveis. Não recebem uma citação externa no lugar da evidência experimental.
- Uma referência é citada somente quando sustenta a afirmação imediatamente associada. A quantidade de fontes não prova a qualidade do argumento.

## Referências efetivamente citadas na versão atual

| Chave | Tipo e validação | O que acrescenta ao texto |
|---|---|---|
| `seghir2026` | Conjunto de dados, Mendeley Data, DOI 10.17632/4jdt83yy43.3, versão 3, CC BY 4.0. | Fonte primária do experimento principal: dois módulos idênticos, um limpo diariamente e outro exposto; variáveis, período e limites da série interpolada de poeira. Sustenta a proveniência dos resultados próprios, não uma generalização residencial. |
| `akter2025` | Conjunto de dados, Mendeley Data, DOI 10.17632/g6pxf8nnt6.2, versão 2, CC BY 4.0. | Fonte primária do teste externo em Dhaka: configuração de dois painéis de 20 W, um limpo e outro não limpo, e frequência original de medição. |
| `symeonides2024` | Conjunto de dados, Zenodo, DOI 10.5281/zenodo.17775544, versão 1. | Proveniência da fonte complementar de potência de inversores e meteorologia. Justifica limitar esse experimento à potência, pois o conjunto não fornece rótulo independente de sujidade. |
| `bessa2021` | Artigo de revisão, *iScience*, DOI 10.1016/j.isci.2021.102165. | Define sujidade e mapeia estratégias de monitoramento; fundamenta que existem diferentes tecnologias e limitações. |
| `king2004` | Relatório técnico Sandia, DOI 10.2172/919131. | Fundamenta que irradiância e temperatura influenciam a potência fotovoltaica e que as grandezas precisam ser corretamente identificadas. |
| `dobos2014` | Manual técnico NREL, DOI 10.2172/1158421. | Sustenta a necessidade de compatibilizar referência de potência e ponto de medição; é fundamentação física complementar, não o modelo usado nos resultados. |
| `li2024` | Artigo, *Renewable Energy*, DOI 10.1016/j.renene.2024.121493. | Apoia a distinção entre monitoramento com condições observadas e previsão futura de potência. |
| `deceglie2018` | Artigo, *IEEE Journal of Photovoltaics*, DOI 10.1109/JPHOTOV.2017.2784682. | Antecedente para estimar perdas de sujidade a partir do rendimento, sem substituir a avaliação independente do TCC. |
| `skomedal2020` | Artigo, *IEEE Journal of Photovoltaics*, DOI 10.1109/JPHOTOV.2020.3018219. | Fundamenta o limite causal: degradação, sazonalidade e sujidade podem coexistir no desempenho observado. |
| `Tramontin_Rampinelli_2024` | Artigo brasileiro, *The Journal of Engineering and Exact Sciences*, DOI 10.18540/jcecvl10iss3pp18630. | Relaciona dados de inversor, ambiente e limpeza no contexto brasileiro; não transfere seus percentuais ao TCC. |
| `cerqueira2020` | Artigo, *Machine Learning*, DOI 10.1007/s10994-020-05910-7. | Apoia a avaliação temporal e a atenção à não estacionariedade das séries. |
| `kapoor2023` | Artigo, *Patterns*, DOI 10.1016/j.patter.2023.100804. | Fundamenta prevenção de vazamento, separação entre desenvolvimento e teste e registro das decisões. |
| `hoerl1970` | Artigo original, *Technometrics*, DOI 10.1080/00401706.1970.10488634. | Fundamenta a regressão Ridge usada como candidato interno. |
| `breiman2001` | Artigo original, *Machine Learning*, DOI 10.1023/A:1010933404324. | Fundamenta Random Forest usado como candidato interno. |
| `sklearn_metricas` | Documentação oficial do scikit-learn. | Define MAE, RMSE, $R^2$, precisão, sensibilidade e F1 conforme a implementação utilizada. |
| `saito2015` | Artigo, *PLOS ONE*, DOI 10.1371/journal.pone.0118432. | Apoia o uso de precisão e sensibilidade na análise de classes desbalanceadas. |
| `mejia2013` | Artigo, *Solar Energy*, DOI 10.1016/j.solener.2013.06.028. Conferido em 09/10/2026 na página da editora Elsevier. | Fundamenta que perdas e acúmulo de sujidade variam entre instalações e períodos; não fornece parâmetro universal para o protótipo. |
| `tsanakas2025` | Artigo de acesso aberto, *Solar RRL*, DOI 10.1002/solr.202500576. Conferido em 09/10/2026 na página da Wiley. | Apoia a dependência local das variáveis e a necessidade de distinguir previsão, quantificação de perdas e calibração por instalação. |
| `hevner2004` | Artigo, *MIS Quarterly*, DOI 10.2307/25148625. Conferido em 09/10/2026 no repositório oficial AIS eLibrary. | Fundamenta a apresentação do protótipo como artefato avaliado, articulando problema, construção e evidência. |

## Referências preservadas na bibliografia do projeto

As fontes abaixo permanecem no arquivo `referencias_final.bib` porque foram validadas na revisão de literatura e podem ser usadas em revisão futura. Elas **não são citadas na versão atual** se não sustentam uma afirmação necessária; o BibTeX não deve incluí-las no PDF sem citação explícita.

| Chave | Tipo e validação | Contribuição potencial |
|---|---|---|
| `kalimeris2023data` | Preprint arXiv, DOI 10.48550/arXiv.2301.12939. | Detecção orientada a dados, seleção de referência e uso de Ridge. Deve permanecer identificado como preprint. |
| `pedregosa2011` | Artigo, *Journal of Machine Learning Research*. | Referência da biblioteca scikit-learn e de tarefas de aprendizagem supervisionada. |
| `pvdaq2021` | Conjunto de dados, DOI 10.25984/1846021. | Fonte pública candidata para expansões futuras; não é base dos resultados apresentados. |
| `rdtools_exemplo` | Documentação oficial do RdTools. | Exemplo técnico de fluxo de degradação/sujidade e sinal sintético; não é evidência de dados reais. |
| `sklearn_rf` | Documentação oficial do scikit-learn. | Descreve parâmetros da implementação `RandomForestRegressor`. |
| `sklearn_temporal` | Documentação oficial do scikit-learn. | Descreve `TimeSeriesSplit`; consultar apenas se a estratégia de divisão for alterada. |
| `pvlib_pvwatts` | Documentação oficial do pvlib. | Implementação da equação CC do PVWatts; útil se for incluído um modelo físico. |
| `hyndman2006` | Artigo, *International Journal of Forecasting*, DOI 10.1016/j.ijforecast.2006.03.001. | Discute limitações de métricas percentuais perto de zero. |
| `bipm2026` | Publicação institucional do BIPM, DOI 10.59161/AUEZ1291. | Define unidades do SI, incluindo potência e energia. |
| `sklearn_praticas` | Documentação oficial do scikit-learn. | Complementa a prevenção de vazamento no pré-processamento. |

## Como checar antes da entrega

1. Para cada parágrafo com afirmação externa, confirme que a referência da tabela realmente sustenta a paráfrase.
2. Para cada tabela de resultado próprio, confira no registro de experimento o conjunto, partição, unidade e métrica correspondentes.
3. Não transformar dados do experimento de Laghouat em percentuais de perda residencial, economia em reais ou frequência de limpeza.
4. Atualizar este arquivo e a entrada BibTeX se a versão de um conjunto de dados, DOI, licença ou fonte for alterada.
