# Correções metodológicas aplicadas em 19/10/2026

Este registro documenta correções feitas após a reavaliação técnica do protótipo. O objetivo é impedir que resultados previamente reproduzidos sejam interpretados além do que os dados permitem.

## Alerta persistente

O contador de persistência agora recebe a data de cada indicador diário. Uma lacuna no calendário, uma data duplicada ou uma série fora de ordem interrompe a sequência ou gera erro de validação. Assim, o software não chama de "três dias consecutivos" três dias disponíveis separados por ausências de dados.

O fluxo operacional passou a usar a mesma definição central do experimento: mediana da perda diária estimada, limiar de 15%, irradiância mínima de 50 W/m² e persistência de três dias. O mínimo padrão de uma amostra diária existe para tornar o contrato equivalente à série experimental; antes de uso real, essa exigência deve ser recalibrada segundo a frequência da telemetria local.

## Painel

O painel usa a média diária da potência limpa **prevista pelo Ridge** e da potência medida para a curva de geração relativa. A potência do painel limpo medida por Laghouat continua disponível apenas nos artefatos de avaliação, onde é necessária para calcular o erro de previsão e a perda observada. Ela não alimenta o indicador exibido como estimativa do monitor.

## Calibração pós-limpeza

As quatro durações de calibração agora são comparadas em uma mesma janela futura: do primeiro instante após 60 dias até o fim da série. Versões anteriores avaliavam cada duração em um período futuro diferente, o que confundia efeito da duração com mudança temporal do experimento.

Essa análise é retrospectiva e exploratória. Ela indica que uma referência curta se ajusta pior ao período comum de Laghouat; não permite escolher uma duração universal, nem valida uma residência.

## Leitura dos alertas

No teste final de Laghouat, 29 de 35 dias já eram positivos segundo a referência observada. Por isso, além de precisão, sensibilidade e F1, os artefatos agora registram prevalência, especificidade e baselines de alerta constante. O F1 de 0,951 deve ser lido como aderência ao experimento controlado, e não como demonstração isolada de vantagem operacional.

## Artigo

O artigo no Overleaf permanece a versão canônica. Nenhum arquivo `.tex` foi alterado nesta etapa. A atualização do artigo deve ser feita somente depois que esta revisão técnica, incluindo a avaliação de Dhaka, estiver concluída e for possível substituir todos os números afetados em um único ciclo coerente.
