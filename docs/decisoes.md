# Registro de decisões

| ID | Decisão | Justificativa | Estado |
|---|---|---|---|
| D01 | Usar estimativa instantânea de potência limpa esperada, não previsão futura. | Mantém a tarefa alinhada ao monitoramento pelas condições observadas e permite comparar a expectativa com a potência medida. | Aceita para o MVP |
| D02 | Comparar Ridge e Random Forest. | Permite uma referência simples e uma relação não linear, sem presumir superioridade. | Aceita para o MVP |
| D03 | Separar cronologicamente treino, validação e teste. | Reduz vazamento temporal e preserva uma avaliação final. | Aceita |
| D04 | Chamar o resultado de alerta de perda adicional persistente. | O resíduo não identifica sozinho a causa da perda. | Aceita |
| D05 | Não versionar dados brutos, processados, modelos ou resultados. | Evita distribuição indevida de dados e arquivos grandes; a proveniência fica documentada. | Aceita |
| D06 | Começar com CSV e interface de linha de comando. | Facilita auditoria e validação antes de uma interface gráfica. | Aceita |
| D07 | Usar o experimento Laghouat 2022 como base supervisionada de desenvolvimento e validação. | A fonte pública compara módulos idênticos, um limpo diariamente e outro exposto à poeira, permitindo medir uma perda de referência sem transformar o experimento no objeto final do projeto. | Aceita para protótipo; validação externa pendente |
| D08 | Não fixar limiar de limpeza nesta fase. | O limite no painel é exploratório e serve para priorizar investigação; otimização econômica de limpeza está fora do escopo. | Aceita |
| D09 | Criar uma interface web local com Streamlit e abas separadas. | As abas distinguem visão geral, análise de dados, validação científica e cenário econômico, sem recomendar limpeza automática. | Implementada |
| D18 | Restringir a aba principal de análise ao dataset público auditado de Laghouat. | Evita que a demonstração misture fontes sem proveniência; a futura integração de dados locais permanece disponível apenas como fluxo técnico de linha de comando. | Implementada |
| D19 | Reproduzir os experimentos públicos por um único comando. | Reduz etapas manuais, fixa a seleção na validação e registra em JSON os resultados finais de cada fonte. | Implementada |
| D20 | Gerar tabelas e figuras somente a partir dos artefatos de experimentos já concluídos. | Evita recálculo acidental, mantém a separação entre validação e teste final e torna os materiais do artigo reproduzíveis. | Implementada |
| D21 | Oferecer atalhos de abertura que preparam os resultados locais somente quando faltarem. | Reduz a barreira para demonstrar o painel sem esconder a origem dos dados ou executar novamente os experimentos a cada abertura. | Implementada |
| D10 | Usar a fonte Zenodo de inversores de 2023--2024 somente como avaliação externa de potência. | Ela tem autoria institucional rastreável, DOI, licença, checksums e método documentado; contudo, não possui rótulo de sujidade ou histórico de limpeza. | Aceita como complementar limitada |
| D11 | Incluir cenário econômico residencial opcional. | Complementa o monitor com valores editáveis de energia, limpeza e recuperação assumida, sem alegar economia real ou substituir orçamento. | Aceita para visualização |
| D12 | Tratar chuva como contexto, não como limpeza automática. | A eficácia depende do tipo de sujeira e das condições locais; eventos de chuva não garantem recuperação total. | Aceita |
| D13 | Direcionar o MVP a sistemas residenciais. | É o público-alvo inicial definido para o artefato; o código permanece organizado para permitir futura adaptação a outras escalas. | Aceita |
| D14 | Não depender de dados locais nesta etapa. | Não há dataset residencial de campo disponível; os resultados serão delimitados à base pública e à necessidade de validação externa futura. | Aceita |
| D15 | Calibrar alertas exclusivamente na validação e testar uma única vez no período final. | Evita escolher limiar ou persistência olhando o conjunto de teste e torna a métrica de alerta auditável. | Aceita |
| D16 | Excluir previsões prontas da fonte externa e usar a potência observada do inversor como alvo. | Evita vazamento de informação e mantém o experimento comparável a uma estimação de potência operacional. | Aceita |
| D17 | Exigir relatório de qualidade antes de gerar alertas operacionais. | Torna exclusões de dados auditáveis e evita que valores inválidos sejam ocultados por preenchimento automático. | Implementada |

O escopo do MVP é o monitoramento em sistemas residenciais, com arquitetura passível de escalonamento. A validação usa dados públicos; não há, nesta etapa, dados de uma instalação residencial local nem afirmação de generalização para outras instalações.
