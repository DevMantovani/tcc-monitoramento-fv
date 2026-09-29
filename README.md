# Monitoramento fotovoltaico por dados

Repositório do TCC de Matheus Luís Mantovani Passoni. Ele mantém juntos o artigo em LaTeX (`article/`) e a implementação reproduzível (`src/`, `docs/` e `data/`).

## O que esta primeira versão faz

1. Lê medições temporais de irradiância, temperatura do módulo e potência observada.
2. Remove registros inválidos sem preencher lacunas silenciosamente.
3. Separa treino, validação e teste respeitando a ordem do tempo.
4. Compara Ridge (referência linear regularizada) e Random Forest.
5. Estima a potência de referência e sinaliza **perda adicional persistente**. O alerta não diagnostica automaticamente sujidade: sombras, falhas, degradação e erros de medição são hipóteses alternativas.

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

## Primeiro teste do pipeline

```bash
pv-monitor demo --output data/processed/demo_sintetico.csv
pv-monitor train --input data/processed/demo_sintetico.csv --output artifacts/demo
pv-monitor detect --input data/processed/demo_sintetico.csv --model artifacts/demo/random_forest.joblib --output artifacts/demo/alertas.csv
pytest
```

O comando `demo` injeta uma perda controlada apenas para verificar se o pipeline produz indicadores e alertas. Consulte [docs/metodologia.md](docs/metodologia.md) antes de interpretar os resultados.

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
