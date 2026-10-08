# Monitoramento fotovoltaico por dados

Repositório do TCC de Matheus Luís Mantovani Passoni. Ele mantém juntos o artigo em LaTeX (`article/`) e a implementação reproduzível (`src/`, `docs/` e `data/`).

## O que esta versão faz

1. Prepara dados publicados de um experimento com painéis fotovoltaicos limpo e exposto à poeira.
2. Calcula a perda observada entre os dois painéis apenas em condições diurnas com referência utilizável.
3. Exibe a evolução da perda, da potência e do acúmulo de poeira em um painel local.
4. Mantém um pipeline sintético separado somente para testes técnicos futuros.

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

## Painel visual local

Após preparar a base real, abra a análise com:

```bash
pv-dashboard
```

O painel mostra perda diária observada, potência média dos painéis limpo e exposto, densidade de poeira, precipitação e os dias que superam um limite visual escolhido. A lateral permite inserir tarifa/valor da energia e custo de limpeza para uma comparação retrospectiva do período. Esses valores não são preenchidos automaticamente: devem corresponder à instalação estudada. Ele é executado somente no computador local e não publica dados. Para encerrar, use `Ctrl+C` no terminal que iniciou o painel.

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
