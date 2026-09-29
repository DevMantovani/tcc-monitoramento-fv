# Registro de decisões

| ID | Decisão | Justificativa | Estado |
|---|---|---|---|
| D01 | Usar estimativa instantânea de potência, não previsão futura. | Mantém a tarefa alinhada ao monitoramento pelas condições observadas. | Aceita para o MVP |
| D02 | Comparar Ridge e Random Forest. | Permite uma referência simples e uma relação não linear, sem presumir superioridade. | Aceita para o MVP |
| D03 | Separar cronologicamente treino, validação e teste. | Reduz vazamento temporal e preserva uma avaliação final. | Aceita |
| D04 | Chamar o resultado de alerta de perda adicional persistente. | O resíduo não identifica sozinho a causa da perda. | Aceita |
| D05 | Não versionar dados brutos, processados, modelos ou resultados. | Evita distribuição indevida de dados e arquivos grandes; a proveniência fica documentada. | Aceita |
| D06 | Começar com CSV e interface de linha de comando. | Facilita auditoria e validação antes de uma interface gráfica. | Aceita |
| D07 | Fonte de dados definitiva. | Deve ter licença, potência, irradiância, temperatura e metadados conferidos. | Pendente |
| D08 | Limiar e persistência do alerta. | Precisam ser calibrados sem consultar o teste final e justificados no relatório. | Pendente |
| D09 | Criar uma interface web local com Streamlit. | A tela apresenta métricas, séries de potência prevista/observada e alertas; ela não substitui a validação metodológica. A seleção de base real permanece pendente. | Implementada para a demonstração |

As decisões D07 e D08 não devem ser tratadas como definidas no artigo antes de uma discussão com o orientador e do registro da base escolhida.
