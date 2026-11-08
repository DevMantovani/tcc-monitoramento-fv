# Monitoramento de perdas por sujidade em sistemas fotovoltaicos

Implementação reproduzível do protótipo do TCC de Matheus Luís Mantovani Passoni. O software estima a potência de referência a partir de variáveis ambientais, compara-a à potência medida e sinaliza perdas persistentes para **inspeção técnica**. Ele não diagnostica exclusivamente sujidade nem aciona limpeza automática.

Este repositório contém o código, os testes e a documentação que sustentam os resultados do estudo. O manuscrito acadêmico é mantido separadamente.

## Para avaliadores

O estudo avalia retrospectivamente o método em fontes públicas, com separação cronológica entre treino, validação e teste final. O painel em Streamlit é uma demonstração dos resultados já processados; a evidência científica está no fluxo reproduzível de preparação, treinamento, avaliação e testes automatizados.

- Para verificar a instalação e a lógica do software, execute `pytest -q`.
- Para reproduzir os resultados principais, siga o comando da seção [Reproduzir os experimentos-base de uma vez](#3-reproduzir-os-experimentos-base-de-uma-vez). Os dois CSVs necessários já acompanham o repositório.
- Para a interpretação dos resultados e de seus limites, consulte [docs/avaliacao-cientifica.md](docs/avaliacao-cientifica.md).

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
| `data/raw/` | Três fontes públicas auditadas, versionadas com atribuição e licença CC BY 4.0. Inclui os dois CSVs da reprodução principal e o arquivo compactado de Dhaka para a validação externa. Veja `data/raw/README.md`. |
| `data/processed/` | CSVs derivados durante a preparação. São recriados localmente e não entram no Git. |
| `artifacts/` | Modelos, métricas, gráficos e relatórios gerados pelos comandos. São locais e recriáveis. |
| `iniciar_painel.bat` / `iniciar_painel.sh` | Atalhos para preparar o ambiente e abrir o painel em Windows ou Linux/macOS. |

## Conteúdo publicado e conteúdo local

O GitHub contém o código-fonte, os testes, os scripts de execução, as dependências declaradas em `pyproject.toml`, a documentação metodológica e as três fontes públicas auditadas. Os CSVs de Laghouat e do Chipre e o arquivo compactado de Dhaka são distribuídos sob CC BY 4.0, mantêm o nome original e possuem DOI, licença e checksum registrados em [docs/dados.md](docs/dados.md).

Não são publicados arquivos processados, modelos treinados, métricas, gráficos gerados ou dados operacionais; esses são resultados locais e recriáveis.

## Pré-requisitos

- Python 3.11, 3.12 ou 3.13.

Os dois CSVs necessários à reprodução e ao painel já estão nestes caminhos:

```text
data/raw/laghouat_2022/Laghouat_2022_final.csv
data/raw/zenodo_inverter_2023_2024/math_model_all_inverters_03.11.2023-25.06.2024.csv
```

As fontes, licenças, checksums e limitações estão em [docs/dados.md](docs/dados.md). Não inclua novos dados na pasta sem verificar licença, privacidade e necessidade metodológica.

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

Usa as bases de Laghouat e do Chipre já versionadas no repositório:

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

## Reprodutibilidade

Este repositório reúne o código, os testes e a documentação técnica que sustentam o estudo. Os procedimentos de preparação dos dados, treinamento, calibração e avaliação estão descritos nas seções anteriores e detalhados em [docs/reproducao.md](docs/reproducao.md).

Para tornar os experimentos acessíveis, o repositório inclui os dois CSVs usados no fluxo principal e o arquivo compactado de Dhaka usado no teste externo, com atribuição, DOI e checksums documentados. Arquivos intermediários, artefatos gerados e dados operacionais permanecem fora do Git. A proveniência, as licenças e as limitações de cada fonte estão registradas em [docs/dados.md](docs/dados.md). O manuscrito do TCC é mantido separadamente do código.

## Licença

O código e a documentação produzidos neste repositório são disponibilizados sob a [licença MIT](LICENSE). Os conjuntos de dados preservam as licenças e as atribuições de suas fontes originais, registradas em [docs/dados.md](docs/dados.md).
