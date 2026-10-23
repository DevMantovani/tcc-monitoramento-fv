# Monitoramento de perdas por sujidade em sistemas fotovoltaicos com aprendizado de máquina

Repositório do TCC de Matheus Luís Mantovani Passoni. Ele mantém juntos o artigo em LaTeX (`article/`) e a implementação reproduzível (`src/`, `docs/` e `data/`).

## O que esta versão faz

1. Seleciona internamente um estimador de potência limpa esperada usando variáveis ambientais; essa seleção não é o objetivo comparativo do TCC.
2. Compara a potência esperada com a potência realmente medida para estimar perdas que podem estar associadas à sujidade.
3. Usa o experimento publicado de painel limpo versus exposto como referência supervisionada para treinar e validar o monitor, não como objeto final do projeto.
4. Exibe o desempenho do monitor e os indicadores de perda em um painel local.

Os dados sintéticos servem somente para testar o fluxo de software. Não podem ser usados como evidência de desempenho real no artigo.

## Abrir o painel sem usar comandos Python

Depois de colocar os dois datasets públicos nos caminhos descritos em [docs/execucao-simplificada.md](docs/execucao-simplificada.md), use o atalho adequado:

- **Windows:** duplo clique em `iniciar_painel.bat`.
- **Linux/macOS:** execute `bash iniciar_painel.sh` na pasta do projeto.

Na primeira abertura, o atalho cria o ambiente local, instala o projeto e prepara os resultados auditáveis. Nas demais, abre diretamente o painel em `http://127.0.0.1:8501`.

## Estrutura

```text
article/              Artigo LaTeX e bibliografia recebidos
data/raw/             Dados de origem (não versionados)
data/processed/       CSVs preparados localmente (não versionados)
docs/                 Método, decisões e registro de experimentos
src/pv_monitor/       Código do pipeline
tests/                Testes automatizados
artifacts/            Modelos e resultados gerados localmente
```

## Preparação no Linux ou Windows

Instale Python 3.11–3.13 e Git. Depois, na raiz do repositório:

```bash
python -m venv .venv
```

Ative o ambiente:

```bash
# Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Instale o projeto e suas dependências:

```bash
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Preparar a base real de sujidade

Baixe o arquivo `Laghouat_2022_final.csv` da [fonte pública no Mendeley Data](https://doi.org/10.17632/4jdt83yy43.3) e mantenha-o localmente em `data/raw/laghouat_2022/`. Em seguida:

```bash
pv-monitor prepare-laghouat \
  --input data/raw/laghouat_2022/Laghouat_2022_final.csv \
  --output data/processed/laghouat_2022.csv
pytest
```

O conjunto compara um painel limpo diariamente a outro exposto ao acúmulo natural de poeira. Consulte [docs/dados.md](docs/dados.md) para proveniência, limitações e auditoria. O limite apresentado na interface é visual e exploratório; ainda não é uma ordem de limpeza.

## Reproduzir os experimentos-base

Depois de baixar as duas fontes auditadas, execute um único comando para preparar os dados, selecionar internamente os estimadores pela validação e refazer os testes finais dos experimentos-base:

```bash
pv-monitor reproduce-public-experiments \
  --laghouat-input data/raw/laghouat_2022/Laghouat_2022_final.csv \
  --zenodo-input data/raw/zenodo_inverter_2023_2024/math_model_all_inverters_03.11.2023-25.06.2024.csv \
  --output artifacts/reproduction_summary.json
```

O resumo consolidado fica em `artifacts/reproduction_summary.json`. O teste adicional de transferibilidade com a base de Dhaka é reproduzido separadamente, conforme [docs/validacao-externa.md](docs/validacao-externa.md), pois usa um arquivo compactado com estrutura própria. Consulte [docs/reproducao.md](docs/reproducao.md) para o escopo dos experimentos-base.

## Gerar tabelas e figuras dos resultados

Depois de reproduzir os experimentos, gere os materiais que poderão ser usados no artigo e na apresentação:

```bash
pv-monitor generate-results \
  --input-dir artifacts \
  --output artifacts/result_materials
```

O comando cria tabelas CSV e gráficos em PNG e SVG a partir dos artefatos já calculados. Ele não baixa novas bases, não retreina modelos e não altera as métricas. Veja [docs/resultados.md](docs/resultados.md) para o significado de cada material.

## Treinar o monitor de perdas por sujidade

```bash
pv-monitor train-soiling-monitor \
  --input data/processed/laghouat_2022.csv \
  --output artifacts/laghouat_monitor
```

O modelo aprende a estimar a potência limpa esperada a partir de irradiância e temperatura. Na fase de monitoramento, ele compara essa estimativa com a potência medida do sistema. A potência do painel limpo do experimento é usada exclusivamente como referência supervisionada para desenvolvimento e validação.

## Teste externo de transferibilidade do monitor

Uma segunda fonte pública de Dhaka contém painéis limpo e exposto, em outro clima e por um período maior. Ela é usada para verificar se a política e o fluxo do monitor se transferem automaticamente — e o resultado negativo também é preservado. Após baixar e extrair a fonte conforme [docs/validacao-externa.md](docs/validacao-externa.md):

```bash
pv-monitor prepare-bangladesh \
  --input-dir data/raw/bangladesh_2019_2020/extracted \
  --output data/processed/bangladesh_2019_2020.csv

pv-monitor evaluate-final \
  --input data/processed/bangladesh_2019_2020.csv \
  --policy artifacts/laghouat_monitor/alert_policy_validation.json \
  --output artifacts/bangladesh_transfer
```

O teste não confirma generalização automática: a política calibrada em Laghouat não se transferiu para Dhaka. Essa limitação é resultado do projeto, não um resultado a ser omitido.

## Avaliação externa recente de potência

Uma fonte externa só é incluída depois de auditoria de proveniência, licença, método e aderência ao objetivo. A fonte de 2023--2024 da University of Cyprus é usada exclusivamente para verificar a estimativa de potência em outra instalação: ela não possui rótulo independente de sujidade e, portanto, não valida alertas nem a decisão de limpeza.

```bash
pv-monitor prepare-zenodo-inverter \
  --input data/raw/zenodo_inverter_2023_2024/math_model_all_inverters_03.11.2023-25.06.2024.csv \
  --inverter-id inverter1 \
  --output data/processed/zenodo_inverter1_2023_2024.csv

pv-monitor train \
  --input data/processed/zenodo_inverter1_2023_2024.csv \
  --output artifacts/zenodo_inverter1

# Execute apenas após escolher o modelo pelas métricas de validação acima.
pv-monitor evaluate-final-power \
  --input data/processed/zenodo_inverter1_2023_2024.csv \
  --model-name random_forest \
  --output artifacts/zenodo_inverter1_final
```

## Calibrar alertas e executar o teste final

Após selecionar o modelo pela validação, calibre os alertas somente na mesma partição de validação e preserve o teste final:

```bash
pv-monitor calibrate-alert-policy \
  --input data/processed/laghouat_2022.csv \
  --output artifacts/laghouat_monitor \
  --model-name ridge

pv-monitor evaluate-final \
  --input data/processed/laghouat_2022.csv \
  --policy artifacts/laghouat_monitor/alert_policy_validation.json \
  --output artifacts/laghouat_final
```

O último comando refaz o treinamento com treino e validação, mas mantém bloqueados o modelo e a política de alerta escolhidos antes de acessar o teste final.

Consulte [docs/avaliacao-cientifica.md](docs/avaliacao-cientifica.md) para a interpretação consolidada dos resultados positivos no experimento controlado, do teste externo negativo e do escopo que o TCC pode afirmar.

## Painel visual local

Após preparar a base real, abra a análise com:

```bash
pv-dashboard
```

O painel é uma única tela de apresentação para pessoas leigas: mostra a geração medida em relação ao esperado, a perda identificada e a quantidade de dias que pedem inspeção. Métricas de validação, tabelas detalhadas e cenário econômico permanecem na documentação, nos slides e no artigo. A tela utiliza exclusivamente o dataset público de Laghouat, já documentado e baixado para o projeto, e apresenta apenas o recorte de teste final preservado. Para encerrar, use `Ctrl+C` no terminal que iniciou o painel.

## Fluxo operacional para futura integração

O protótipo também possui um fluxo de linha de comando para uma futura integração com inversor, medidor ou API. Ele inspeciona a qualidade dos dados e gera um alerta diário de perda adicional persistente. Esse fluxo não é a fonte da tela principal atual, que é restrita ao dataset público auditado. Ele recomenda investigação, não limpeza automática nem atribuição certa de causa.

```bash
pv-monitor check-input --input dados_operacionais.csv --output artifacts/qualidade_entrada.json
pv-monitor calibrate-installation \
  --input dados_operacionais.csv \
  --cleaning-timestamp 2026-01-15T00:00:00Z \
  --calibration-days 14 \
  --output artifacts/calibracao_local
pv-monitor detect --input dados_operacionais.csv --model artifacts/calibracao_local/clean_baseline_ridge.joblib --output artifacts/alertas_diarios.csv
```

O comando de calibração usa somente o período posterior a uma limpeza confirmada para formar a referência de geração daquela instalação. Consulte [docs/calibracao-local.md](docs/calibracao-local.md) antes de usar esse fluxo.

Consulte [docs/operacao.md](docs/operacao.md) para o formato do CSV, parâmetros e limites para uso em campo.

## Teste técnico com dados sintéticos

```bash
pv-monitor demo --output data/processed/demo_sintetico.csv
pv-monitor train --input data/processed/demo_sintetico.csv --output artifacts/demo
pv-monitor detect --input data/processed/demo_sintetico.csv --model artifacts/demo/random_forest.joblib --output artifacts/demo/alertas.csv
pytest
```

O comando `demo` injeta uma perda controlada apenas para verificar se o pipeline produz indicadores e alertas. Seus resultados não são evidência científica nem aparecem no painel principal.

## Versionamento com GitHub

O repositório privado do projeto está em [github.com/DevMantovani/tcc-monitoramento-fv](https://github.com/DevMantovani/tcc-monitoramento-fv). Em outro computador, depois de obter acesso ao GitHub, clone-o uma única vez:

```bash
git clone https://github.com/DevMantovani/tcc-monitoramento-fv.git
cd tcc-monitoramento-fv
```

Antes de iniciar uma etapa de trabalho, atualize a cópia local; ao concluir uma alteração coerente e verificada, registre-a e envie-a:

```bash
git pull --ff-only
# editar, executar e verificar
git status
git add src docs tests README.md article
git commit -m "docs: descreve a mudança"
git push origin main
```

Os datasets públicos, os artefatos gerados e o ambiente virtual não fazem parte do repositório. O passo a passo e as regras de commit estão em [docs/versionamento.md](docs/versionamento.md).
