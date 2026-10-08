# Revisão técnica final

## Escopo da revisão

Esta revisão cobre a versão do protótipo que usa as fontes públicas de Laghouat (sujidade), Dhaka (teste externo de sujidade) e Zenodo (potência externa). Ela não reescreve o artigo em LaTeX, pois essa etapa foi deliberadamente reservada para depois da estabilização da implementação.

## Consistência verificada

- **Fluxo de dados:** a normalização das colunas obrigatórias (`timestamp`, irradiância, temperatura e potência) é compartilhada entre a carga e o relatório de qualidade. Isso evita regras divergentes para a mesma entrada.
- **Avaliação:** treino, validação e teste continuam cronológicos. Modelo e política são escolhidos somente na validação; o teste final é acessado depois de bloqueados.
- **Escopo das fontes:** Laghouat é a base supervisionada principal. Dhaka fornece um segundo par limpo/exposto e demonstrou que a versão atual do monitor não se transfere automaticamente. Zenodo avalia apenas potência esperada em outra instalação; não é usado para alegar detecção de sujidade.
- **Interface:** a análise visual permanece restrita ao dataset público auditado e ao teste final preservado. Não existe importação livre de CSV na tela principal.
- **Operação futura:** alertas indicam inspeção e não limpeza automática ou diagnóstico definitivo de causa.
- **Calibração local:** após limpeza confirmada, o comando operacional cria uma referência de potência específica da instalação e registra sua janela de origem. Essa arquitetura ainda não possui validação residencial real.
- **Reprodutibilidade:** um comando recompõe os experimentos; outro gera tabelas e figuras a partir dos resultados já salvos. Os atalhos de abertura não recriam resultados que já existam.

## Simplificações e refatorações aplicadas

- Centralizada a validação e conversão de colunas dos CSVs, eliminando lógica duplicada entre leitura e relatório de qualidade.
- Centralizada a lógica de dias consecutivos para os alertas, usada tanto na avaliação científica como no fluxo operacional futuro.
- Criado `pv-launch`, além de `iniciar_painel.bat` e `iniciar_painel.sh`, para preparar artefatos faltantes e abrir o painel sem exigir que a pessoa conheça os comandos do pipeline.
- Mantidos dados, modelos e resultados fora do versionamento. Eles são regeneráveis e não devem ser substituídos por dados sintéticos ou fontes não auditadas.
- Incorporada preparação auditável para os 295 CSVs de Dhaka, tratando cabeçalhos e datas divergentes sem preencher valores ausentes.

## Limites que permanecem

1. Não há dados reais de uma residência brasileira; portanto, os resultados não representam uma implantação local.
2. O painel limpo do experimento é uma referência supervisionada de desenvolvimento, não uma condição disponível em uma residência comum.
3. A transferência para Dhaka falhou mesmo após recalibração local do limiar, logo a versão atual não pode alegar generalização entre instalações.
4. O resíduo entre potência esperada e medida pode resultar de sujidade, sombra, falha, degradação, indisponibilidade ou erro de sensor. O protótipo não identifica a causa sozinho.
5. A regra de alerta de 15% por três dias foi escolhida no experimento público; uma instalação futura deve ser recalibrada com seus próprios dados e eventos de limpeza verificados.
6. Nenhum cenário econômico é exibido na tela operacional: uma estimativa financeira exige geração, tarifa, custo e recuperação próprios da instalação.

## Resultado da execução de verificação

A verificação final deve incluir testes automatizados, compilação dos módulos, reprodução dos dois experimentos públicos, geração dos materiais de resultado e abertura local do painel. Os comandos e resultados da execução ficam registrados no histórico do Git junto desta revisão.
