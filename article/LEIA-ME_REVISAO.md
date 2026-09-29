# Revisão de trabalho do TCC

28/09/2026 | Matheus Luís Mantovani Passoni

Esta versão organiza uma proposta para discussão com o orientador. Não contém resultados de treinamento ou validação e não comprova eficácia em campo. A base definitiva ainda precisa ser selecionada e inspecionada.

## Abrir no Overleaf

1. Importe o ZIP como projeto ou aplique os arquivos ao projeto existente.
2. Defina `TCCFinal.tex` como documento principal e use pdfLaTeX.
3. O artigo utiliza `referencias_final.bib` e o estilo `abntex2-unesc.bst` recebido.
4. São necessários `abntex2cite` e o idioma português na instalação TeX.

## Arquivos e alterações

| Arquivo | Situação |
|---|---|
| `TCCFinal.tex` | Título, autoria, resumo e abstract provisórios, introdução e metodologia proposta. Resultados e conclusão pendentes. |
| `referencias_final.bib` | Bibliografia da nova versão, com chaves únicas e fontes rastreáveis. |
| `UNESC.cls` | Corrigida uma abertura duplicada de `\@makecaption` e a formatação de seções sem numeração. Preservados tamanho da página e margens. |
| `abntex2-unesc.bst` | Corrigidas funções comentadas indevidamente, rótulo de citação, alias de relatório técnico e repetição do ano. Mantidas as escolhas visuais do estilo recebido. |
| `historico/abntex2-unesc.bst` | Estilo original recebido, antes das correções. |
| `historico/TCCFinal.tex` | Artigo original recebido, antes da revisão. |
| `historico/UNESC.cls` | Classe original recebida, antes da correção. |
| Demais arquivos recebidos | Preservados; proposta e projeto antigos representam o planejamento anterior. |

O `referencias.bib` original contém chaves duplicadas e entradas incompletas. Foi preservado para consulta, mas não participa da compilação de `TCCFinal.tex`. Compilar o projeto antigo ainda exigirá rever essa bibliografia. Uma referência no arquivo histórico não equivale à validação de seu conteúdo.

## Abordagem recomendada

- Estimar a potência de referência no mesmo instante da irradiância e temperatura observadas.
- Comparar Random Forest com Ridge contendo irradiância, temperatura e sua interação. Acrescentar um modelo físico somente se houver metadados adequados.
- Justificar uma referência de baixa sujidade. Sem essa evidência, limitar a interpretação a perdas adicionais frente ao comportamento operacional disponível.
- Separar os dados por tempo e preservar um teste final.
- Calcular o desvio diário com as mesmas amostras válidas e exigir persistência antes do alerta.
- Avaliar previsão e detecção separadamente: um bom R² não demonstra, isoladamente, detecção de sujeira.
- Construir primeiro o processamento de CSV; adicionar a interface após validar o método.

## Origem dos dados

A seleção deve começar por uma instalação do PVDAQ com potência, irradiância no plano dos módulos e temperatura. Vento, chuva e registros de limpeza podem ampliar a análise. Dados de potência de um inversor, isoladamente, não garantem a existência de medições ambientais.

O exemplo do RdTools utiliza o sistema 4 do PVDAQ e oferece um sinal de sujidade sintetizado. Ele é uma alternativa para um estudo semissintético: medições de operação com perdas adicionais impostas e conhecidas. O fator artificial serve ao controle e à avaliação, nunca à entrada do estimador. Nesta revisão foi consultada a documentação; o CSV ainda não foi baixado nem auditado.

Uma base inteiramente gerada por fórmulas pode testar o software, mas restringe as conclusões ao simulador. Números arbitrários gerados por IA não validam o comportamento de uma instalação real. A preferência é usar medições documentadas e complementar a análise com cenários controlados.

- PVDAQ: https://data.openei.org/submissions/4568
- DOI do conjunto: https://doi.org/10.25984/1846021
- Exemplo RdTools: https://rdtools.readthedocs.io/en/2.0.4/rd_example.html
- Catálogo: https://datahub.duramat.org/dataset/pvdaq-time-series-with-soiling-signal

## Fontes e limites da revisão

Foram consultadas páginas de periódicos, documentação oficial e repositórios de autores/instituições. A bibliografia distingue artigos, um preprint, documentação de software e um conjunto de dados. O acesso a metadados ou ao resumo confirma apenas o conteúdo efetivamente consultado; não representa uma revisão sistemática nem leitura integral de todas as referências.

A ampliação bibliográfica de 28/09/2026 acrescentou 14 fontes às 12 anteriores, totalizando 26 referências citadas. O arquivo `MAPA_DE_REFERENCIAS.md` relaciona cada nova fonte à sua função no artigo, informa o nível de acesso consultado e distingue as propostas dos autores das afirmações da literatura. Foram reforçados os fundamentos físicos, os trabalhos relacionados, a regressão Ridge, a avaliação temporal, a prevenção de vazamento e as métricas. As fórmulas padronizadas de avaliação passaram a ter citação explícita.

O estilo bibliográfico também foi ajustado para exibir na lista final os sufixos de desambiguação usados nas citações de fontes com mesmo autor e ano (como as páginas sem data do scikit-learn).

Referências científicas centrais da primeira revisão, complementadas pelo mapa:

| Fonte | Uso no artigo |
|---|---|
| Bessa et al. (2021), iScience, DOI 10.1016/j.isci.2021.102165 | Conceito de sujidade e panorama das estratégias de monitoramento. |
| Deceglie, Micheli e Muller (2018), IEEE Journal of Photovoltaics, DOI 10.1109/JPHOTOV.2017.2784682 | Estimativa por dados de desempenho e importância da validação independente. |
| Tramontin e Rampinelli (2024), jCEC, DOI 10.18540/jcecvl10iss3pp18630 | Análise brasileira de dados antes e depois de limpeza documentada. |
| Kalimeris et al. (2023), preprint arXiv:2301.12939 | Regressão e seleção de períodos de referência; status de preprint identificado. |
| Tsanakas et al. (2025), Solar RRL, DOI 10.1002/solr.202500576 | Distinção entre análise retrospectiva e previsão ambiental de perdas. |
| Breiman (2001), Machine Learning, DOI 10.1023/A:1010933404324 | Fundamentação de Random Forest. |
| Pedregosa et al. (2011), JMLR 12:2825–2830 | Implementação com scikit-learn. |

Os parágrafos científicos foram redigidos como citações indiretas. Não se inseriram percentuais de perda ou alegações de superioridade retirados de resumos como se fossem resultados deste TCC. A revisão ainda deve ser ampliada e discutida com o orientador antes de uma alegação forte de ineditismo.

## Correções conceituais

O resíduo não isola automaticamente a causa da perda. A expressão “perda exata por sujidade” foi substituída por uma interpretação condicionada à evidência disponível. Potência é medida em W ou kW; energia integra potência no tempo e é expressa em Wh ou kWh. O indicador é de desempenho relativo, não de eficiência física de conversão.

A fórmula simplificada de potência apresentada no projeto antigo corresponde à forma documentada do PVWatts. A IEC 60891 trata de correções de curvas I-V; não se deve atribuir a fórmula à norma sem demonstrar a correspondência no texto normativo. Fontes: https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.pvsystem.pvwatts_dc.html e https://webstore.iec.ch/en/publication/61766.

A descrição anterior de Kalimeris et al. era excessivamente restritiva: uma das abordagens utiliza chuva e admite registros de limpeza manual opcionais. Evitou-se repetir essa caracterização ou afirmar originalidade apenas por utilizar IA. Fonte: https://arxiv.org/html/2301.12939v1.

## Orientações da faculdade incorporadas

- Introdução organizada de contexto para fundamentos, trabalhos relacionados, questão delimitada, hipótese, objetivos e justificativa, conforme o material de construção da introdução, que orienta cerca de cinco páginas.
- Objetivos com verbos no infinitivo e resultados verificáveis.
- Citações indiretas com referências, evitando transcrição de parágrafos de outras obras.
- Resultados planejados com comparação, interpretação crítica e limitações.
- Conclusão reservada para retomar objetivos, contribuições, riscos à validade e novas investigações.
- O plano de ensino enviado traz datas de março a julho de 2026 e trata da etapa de projeto. Não foi adotado como calendário da entrega final atual.
- Mantida a estrutura de quatro seções e a classe UNESC. Confirmar com a disciplina o limite total de páginas e o prazo atual.

## Próximas definições

1. Selecionar e baixar a base; conferir licença, unidades, fuso, frequência, lacunas e referência de baixa sujidade.
2. Definir o alcance da validação: sujidade real com evidência independente, cenários semissintéticos ou ambos.
3. Registrar datas das partições, filtros, cobertura, parâmetros dos cenários e regras de rotulagem antes de abrir o teste final.
4. Implementar e comparar os modelos; avaliar os alertas e seus erros.
5. Substituir o resumo provisório por um resumo com os resultados efetivamente obtidos e redigir a conclusão.
6. Revisar texto e referências com o orientador e confirmar o e-mail institucional dele.

## Declaração de IA

A declaração antiga restringia o uso à revisão linguística e à organização textual. A proposta atual também registra o apoio ao levantamento de fontes e à discussão metodológica, refletindo o trabalho desta etapa. A declaração final deve corresponder ao uso efetivo das ferramentas e às orientações institucionais.
