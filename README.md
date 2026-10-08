# Monitoramento de perdas por sujidade em sistemas fotovoltaicos com aprendizado de máquina

Repositório do TCC de Matheus Luís Mantovani Passoni. Ele mantém juntos o artigo em LaTeX (`article/`) e a implementação reproduzível (`src/`, `docs/` e `data/`).

## O que esta versão faz

1. Treina modelos de aprendizado de máquina para estimar a potência esperada de um sistema em condição limpa usando variáveis ambientais.
2. Compara a potência esperada com a potência realmente medida para estimar perdas que podem estar associadas à sujidade.
3. Usa o experimento publicado de painel limpo versus exposto como referência supervisionada para treinar e validar o monitor, não como objeto final do projeto.
4. Exibe o desempenho do monitor e os indicadores de perda em um painel local.

Os dados sintéticos servem somente para testar o fluxo de software. Não podem ser usados como evidência de desempenho real no artigo.

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

## Treinar o monitor de perdas por sujidade

```bash
pv-monitor train-soiling-monitor \
  --input data/processed/laghouat_2022.csv \
  --output artifacts/laghouat_monitor
```

O modelo aprende a estimar a potência limpa esperada a partir de irradiância e temperatura. Na fase de monitoramento, ele compara essa estimativa com a potência medida do sistema. A potência do painel limpo do experimento é usada exclusivamente como referência supervisionada para desenvolvimento e validação.

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

## Painel visual local

Após preparar a base real, abra a análise com:

```bash
pv-dashboard
```

O painel mostra a validação cronológica do modelo de aprendizado de máquina e, em separado, a referência observada do experimento usada para verificar o monitor. Também há dados de poeira, precipitação, um filtro visual e uma simulação editável de economia potencial. O cenário começa com referências residenciais brasileiras, mas não representa orçamento, tarifa real ou economia garantida; consulte `docs/economia.md`. Ele é executado somente no computador local e não publica dados. Para encerrar, use `Ctrl+C` no terminal que iniciou o painel.

## Teste técnico com dados sintéticos

```bash
pv-monitor demo --output data/processed/demo_sintetico.csv
pv-monitor train --input data/processed/demo_sintetico.csv --output artifacts/demo
pv-monitor detect --input data/processed/demo_sintetico.csv --model artifacts/demo/random_forest.joblib --output artifacts/demo/alertas.csv
pytest
```

O comando `demo` injeta uma perda controlada apenas para verificar se o pipeline produz indicadores e alertas. Seus resultados não são evidência científica nem aparecem no painel principal.

## Versionamento com GitHub

Quando o Git estiver instalado, inicialize e faça o primeiro registro:

```bash
git init
git branch -M main
git add .
git commit -m "chore: estrutura inicial do TCC"
```

Crie um repositório vazio no GitHub e conecte-o (substitua a URL):

```bash
git remote add origin https://github.com/SEU-USUARIO/tcc-monitoramento-fv.git
git push -u origin main
```

No outro computador: `git clone URL_DO_REPOSITORIO`; antes de começar, use `git pull`; ao terminar uma etapa verificada, use `git add`, `git commit` e `git push`. O passo a passo e as regras de commit estão em [docs/versionamento.md](docs/versionamento.md).
