# Monitoramento de perdas por sujidade em sistemas fotovoltaicos

Implementação reproduzível do protótipo do TCC de Matheus Luís Mantovani Passoni. O software estima a potência de referência a partir de variáveis ambientais, compara-a à potência medida e sinaliza perdas persistentes para **inspeção técnica**. Ele não diagnostica exclusivamente sujidade nem aciona limpeza automática.

O artigo é mantido exclusivamente no [Overleaf](https://www.overleaf.com/project/69a9f8893e4087c8ce175833). Este repositório contém o código, os testes e a documentação que sustentam os resultados.

## O que o projeto entrega

- Pipeline para preparar a base experimental pública de Laghouat e estimar a perda entre painel limpo e exposto.
- Seleção temporal de modelo de potência, calibração de alertas e avaliação final preservada.
- Avaliação externa de potência no Chipre e teste de transferibilidade em Dhaka, cujo resultado negativo é preservado na documentação.
- Painel local em Streamlit para demonstrar a leitura dos resultados finais.
- Fluxo de linha de comando para uma futura instalação real, com verificação de qualidade e calibração pós-limpeza.

## Estrutura do repositório

| Caminho | Conteúdo e função |
| --- | --- |
| `src/pv_monitor/` | Código do projeto. `data.py` prepara dados; `models.py` seleciona modelos; `workflow.py` executa treino, alertas e calibração; `reporting.py` produz métricas e materiais; `dashboard.py` abre o painel; `cli.py` expõe os comandos `pv-monitor`. |
| `tests/` | Testes automatizados da preparação de dados, persistência dos alertas e consistência das métricas. |
| `docs/` | Documentação metodológica, proveniência das bases, reprodução dos experimentos, limitações, operação e decisões técnicas. Comece por `docs/execucao-simplificada.md` e `docs/reproducao.md`. |
| `data/raw/` | Datasets públicos baixados pelo usuário. Nunca são enviados ao GitHub. |
| `data/processed/` | CSVs derivados durante a preparação. São recriados localmente e não entram no Git. |
| `artifacts/` | Modelos, métricas, gráficos e relatórios gerados pelos comandos. São locais e recriáveis. |
| `iniciar_painel.bat` / `iniciar_painel.sh` | Atalhos para preparar o ambiente e abrir o painel em Windows ou Linux/macOS. |
| `HANDOFF_TCC.md` | Contexto resumido para retomar o projeto em outro computador ou conversa. |

## Pré-requisitos

- Python 3.11, 3.12 ou 3.13.
- Git, para clonar e atualizar o repositório.
- Para reproduzir o painel com dados reais, baixe os dois datasets públicos e mantenha-os exatamente nestes caminhos:

```text
data/raw/laghouat_2022/Laghouat_2022_final.csv
data/raw/zenodo_inverter_2023_2024/math_model_all_inverters_03.11.2023-25.06.2024.csv
```

As fontes, licenças e limitações estão em [docs/dados.md](docs/dados.md). Os arquivos brutos não são versionados.

## Forma mais simples de executar o painel

Com os dois arquivos acima no lugar:

- **Windows:** dê duplo clique em `iniciar_painel.bat`.
- **Linux/macOS:** execute `bash iniciar_painel.sh` na raiz do projeto.

Na primeira execução, o atalho cria `.venv`, instala as dependências, prepara os resultados necessários e abre `http://127.0.0.1:8501`. Nas próximas execuções, reutiliza o ambiente e os resultados locais. Para encerrar, use `Ctrl+C` no terminal que abriu o painel.

## Execução manual

Na raiz do projeto, crie e ative o ambiente:

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

Confirme a instalação:

```bash
pytest -q
pv-monitor --help
```

## Fluxos disponíveis

### 1. Demonstração técnica, sem dados públicos

Gera dados sintéticos apenas para verificar o funcionamento do software. Não use esses resultados como evidência científica.

```bash
pv-monitor demo --output data/processed/demo_sintetico.csv
pv-monitor train --input data/processed/demo_sintetico.csv --output artifacts/demo
pv-monitor detect --input data/processed/demo_sintetico.csv --model artifacts/demo/random_forest.joblib --output artifacts/demo/alertas.csv
```

### 2. Preparar e avaliar o experimento principal

Use a base de Laghouat, que possui painel limpo e painel exposto:

```bash
pv-monitor prepare-laghouat \
  --input data/raw/laghouat_2022/Laghouat_2022_final.csv \
  --output data/processed/laghouat_2022.csv

pv-monitor train-soiling-monitor \
  --input data/processed/laghouat_2022.csv \
  --output artifacts/laghouat_monitor

pv-monitor calibrate-alert-policy \
  --input data/processed/laghouat_2022.csv \
  --output artifacts/laghouat_monitor \
  --model-name ridge

pv-monitor evaluate-final \
  --input data/processed/laghouat_2022.csv \
  --policy artifacts/laghouat_monitor/alert_policy_validation.json \
  --output artifacts/laghouat_final
```

### 3. Reproduzir os experimentos-base de uma vez

Exige as bases de Laghouat e do Chipre:

```bash
pv-monitor reproduce-public-experiments \
  --laghouat-input data/raw/laghouat_2022/Laghouat_2022_final.csv \
  --zenodo-input data/raw/zenodo_inverter_2023_2024/math_model_all_inverters_03.11.2023-25.06.2024.csv \
  --output artifacts/reproduction_summary.json

pv-monitor generate-results \
  --input-dir artifacts \
  --output artifacts/result_materials
```

O segundo comando gera tabelas e figuras a partir dos artefatos já calculados. Detalhes dos resultados estão em [docs/resultados.md](docs/resultados.md).

### 4. Simular uma futura instalação real

Esse fluxo gera recomendações de inspeção a partir de telemetria local. Leia [docs/operacao.md](docs/operacao.md) e [docs/calibracao-local.md](docs/calibracao-local.md) antes de usá-lo.

```bash
pv-monitor check-input --input dados_operacionais.csv --output artifacts/qualidade_entrada.json
pv-monitor calibrate-installation \
  --input dados_operacionais.csv \
  --cleaning-timestamp 2026-01-15T00:00:00Z \
  --calibration-days 14 \
  --output artifacts/calibracao_local
pv-monitor detect \
  --input dados_operacionais.csv \
  --model artifacts/calibracao_local/clean_baseline_ridge.joblib \
  --output artifacts/alertas_diarios.csv
```

## Resultados e limites

O experimento controlado de Laghouat sustenta a avaliação do monitor. O teste externo em Dhaka não confirmou a transferência automática da regra de alerta, portanto uma instalação nova exige calibração e validação locais. A avaliação no Chipre testa a estimativa de potência em outra fonte, mas não valida sujidade por não possuir rótulo independente. A interpretação completa está em [docs/avaliacao-cientifica.md](docs/avaliacao-cientifica.md).

## GitHub e trabalho em outro computador

Clone o repositório privado uma única vez:

```bash
git clone https://github.com/DevMantovani/tcc-monitoramento-fv.git
cd tcc-monitoramento-fv
```

Antes de trabalhar, atualize a cópia. Depois de validar uma alteração, registre e envie somente código, testes e documentação:

```bash
git pull --ff-only
git status
git add src tests docs README.md HANDOFF_TCC.md
git commit -m "docs: descreve a mudança"
git push origin main
```

Não envie `.venv`, datasets, resultados gerados ou o artigo. O artigo canônico permanece no Overleaf.
