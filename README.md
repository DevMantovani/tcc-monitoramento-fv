# Monitoramento de perdas por sujidade em sistemas fotovoltaicos

Implementação reproduzível do protótipo do TCC de Matheus Luís Mantovani Passoni. O software estima a potência de referência a partir de variáveis ambientais, compara-a à potência medida e sinaliza perdas persistentes para **inspeção técnica**. Ele não diagnostica exclusivamente sujidade nem aciona limpeza automática.

Este repositório contém o código, os testes e a documentação que sustentam os resultados do estudo. O manuscrito acadêmico é mantido separadamente.

## Para avaliadores

O estudo avalia retrospectivamente o método em fontes públicas, com separação cronológica entre treino, validação e teste final. O painel em Streamlit é uma demonstração dos resultados já processados; a evidência científica está no fluxo reproduzível de preparação, treinamento, avaliação e testes automatizados.

- Para verificar a instalação e a lógica do software, execute `pytest -q`.
- Para reproduzir os resultados principais, siga o comando da seção [Experimentos-base em um comando](#experimentos-base-em-um-comando). Os dois CSVs necessários já acompanham o repositório.
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

## Dados e reprodutibilidade

O GitHub contém o código-fonte, os testes, os scripts de execução, a documentação metodológica e as três fontes públicas auditadas. Os CSVs de Laghouat e do Chipre reproduzem o fluxo principal; o arquivo compactado de Dhaka reproduz o teste externo. Todos preservam o nome original e possuem DOI, licença CC BY 4.0 e checksum registrados em [docs/dados.md](docs/dados.md). Arquivos processados, modelos, métricas, gráficos e dados operacionais são gerados localmente e não entram no Git.

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

## Reprodução dos experimentos

### Experimento principal

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

### Experimentos-base em um comando

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

O teste externo de Dhaka, a demonstração sintética e a proposta de operação futura estão documentados separadamente em [docs/validacao-externa.md](docs/validacao-externa.md), [docs/execucao-simplificada.md](docs/execucao-simplificada.md) e [docs/operacao.md](docs/operacao.md). Eles não substituem os resultados principais do TCC.

## Resultados e limites

O experimento controlado de Laghouat sustenta a avaliação do monitor. O teste externo em Dhaka não confirmou a transferência automática da regra de alerta, portanto uma instalação nova exige calibração e validação locais. A avaliação no Chipre testa a estimativa de potência em outra fonte, mas não valida sujidade por não possuir rótulo independente. A interpretação completa está em [docs/avaliacao-cientifica.md](docs/avaliacao-cientifica.md).

## Licença

O código e a documentação produzidos neste repositório são disponibilizados sob a [licença MIT](LICENSE). Os conjuntos de dados preservam as licenças e as atribuições de suas fontes originais, registradas em [docs/dados.md](docs/dados.md).
