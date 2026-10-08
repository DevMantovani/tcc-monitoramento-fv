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
| D09 | Criar uma interface web local com Streamlit. | A tela mostra a validação do monitor de ML e, em separado, a referência observada do experimento; ela apoia análise, sem recomendar limpeza automática. | Implementada |
| D10 | Manter o PVDAQ 1433 (NREL RSF1) como fonte secundária auditada. | A fonte institucional possui potência e variáveis ambientais, mas não rótulo de sujidade ou histórico de limpezas no recorte avaliado. | Aceita como complementar |
| D11 | Incluir cenário econômico residencial opcional. | Complementa o monitor com valores editáveis de energia, limpeza e recuperação assumida, sem alegar economia real ou substituir orçamento. | Aceita para visualização |
| D12 | Tratar chuva como contexto, não como limpeza automática. | A eficácia depende do tipo de sujeira e das condições locais; eventos de chuva não garantem recuperação total. | Aceita |
| D13 | Direcionar o MVP a sistemas residenciais. | É o público-alvo inicial definido para o artefato; o código permanece organizado para permitir futura adaptação a outras escalas. | Aceita |
| D14 | Não depender de dados locais nesta etapa. | Não há dataset residencial de campo disponível; os resultados serão delimitados à base pública e à necessidade de validação externa futura. | Aceita |
| D15 | Calibrar alertas exclusivamente na validação e testar uma única vez no período final. | Evita escolher limiar ou persistência olhando o conjunto de teste e torna a métrica de alerta auditável. | Aceita |

O escopo do MVP é o monitoramento em sistemas residenciais, com arquitetura passível de escalonamento. A validação usa dados públicos; não há, nesta etapa, dados de uma instalação residencial local nem afirmação de generalização para outras instalações.
