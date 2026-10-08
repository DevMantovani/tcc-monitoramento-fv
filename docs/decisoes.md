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
| D08 | Não fixar limiar de limpeza nesta fase. | O limite no painel é exploratório; uma decisão econômica exige custo de limpeza, valor de energia, chuva e persistência. | Aceita |
| D09 | Criar uma interface web local com Streamlit. | A tela mostra a validação do monitor de ML e, em separado, a referência observada do experimento; ela apoia análise, sem recomendar limpeza automática. | Implementada |
| D10 | Manter o PVDAQ 1433 (NREL RSF1) como fonte secundária auditada. | A fonte institucional possui potência e variáveis ambientais, mas não rótulo de sujidade ou histórico de limpezas no recorte avaliado. | Aceita como complementar |
| D11 | Usar valores econômicos configurados pelo operador. | Tarifa e custo de limpeza variam conforme local, contrato e operação; a interface compara o período observado sem impor valores arbitrários. | Aceita para o protótipo |
| D12 | Tratar chuva como contexto, não como limpeza automática. | A eficácia depende do tipo de sujeira e das condições locais; eventos de chuva não garantem recuperação total. | Aceita |

A escolha da base e o escopo do protótipo estão registrados. A política econômica de limpeza continua dependente de premissas que devem ser definidas com o orientador e documentadas antes de ser usada como conclusão do artigo.
