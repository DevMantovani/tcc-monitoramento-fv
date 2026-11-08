# Passagem de bastão — TCC de monitoramento fotovoltaico

**Atualizado em:** 08 de novembro de 2026
**Objetivo:** permitir que o projeto seja retomado em outro computador ou em uma nova conversa sem depender deste ambiente.

## Onde está cada parte

- **Código e documentação técnica:** [repositório GitHub](https://github.com/DevMantovani/tcc-monitoramento-fv).
- **Artigo canônico:** mantido separadamente do repositório. O artigo, a bibliografia e as figuras não integram a entrega de código.

## O que o projeto demonstra

O TCC propõe um monitor para **identificar perdas de geração potencialmente associadas à sujidade em sistemas fotovoltaicos**, com foco inicial residencial. O aprendizado de máquina estima uma referência de potência limpa esperada a partir das variáveis ambientais e compara essa referência à potência medida. A interface apresenta o resultado de forma simplificada; não substitui inspeção em campo nem aciona limpeza automaticamente.

A comparação entre Ridge e Random Forest ocorre na validação cronológica, com as mesmas entradas e métricas. O teste final avalia apenas o monitor escolhido; os resultados não estabelecem superioridade universal entre algoritmos.

## Dados e limites que não podem ser omitidos

- O painel principal usa o experimento público de Laghouat, com painel limpo e painel exposto à poeira. A fonte, a licença, o modo de obtenção e as limitações estão documentados em `docs/dados.md`.
- A base pública da University of Cyprus (2023--2024) avalia somente a estimativa de potência em outra instalação; ela **não** possui rótulo independente de sujidade e não valida alerta ou decisão de limpeza.
- O teste de transferibilidade para Dhaka não confirmou transferência automática da política de alertas. Esse resultado negativo deve permanecer explícito no artigo e na apresentação.
- Dados sintéticos existem apenas para testar o software. Eles não são evidência científica e não devem aparecer como resultado do TCC.
- Toda afirmação no artigo precisa de referência verificável. Antes de incluir fonte nova, conferir autoria, veículo, data, método, licença/acesso e aderência ao escopo.

## Estado do trabalho nesta data

- O artigo foi revisado, teve as tabelas ajustadas e compilou sem erros no Overleaf. A conclusão começa na página 20; as referências ficam depois dela.
- O texto mantém somente conteúdo que sustenta o problema, o método, os resultados e as limitações. A extensão não deve ser reduzida artificialmente.
- O repositório reúne código, testes e documentação de reprodução. Antes de uma nova edição, execute `git pull --ff-only`; depois de validar a alteração, use `git add`, `git commit` e `git push origin main`.
- A verificação de espaços e sintaxe do diff (`git diff --check`) e os testes automatizados devem ser executados antes de cada envio.

## Como retomar em outro computador

1. Entre em uma conta pessoal que possa continuar a acessar o GitHub e o Overleaf.
2. Instale Git e Python 3.11 a 3.13.
3. Clone o repositório:

   ```bash
   git clone https://github.com/DevMantovani/tcc-monitoramento-fv.git
   cd tcc-monitoramento-fv
   ```

4. Leia `README.md`, `docs/execucao-simplificada.md` e este arquivo antes de executar o painel.
5. As bases de Laghouat, Chipre e Dhaka já acompanham o repositório. Para a análise externa de Dhaka, siga a extração e os comandos de `docs/validacao-externa.md`.
6. Para abrir o painel, no Windows use `iniciar_painel.bat`; em Linux/macOS execute `bash iniciar_painel.sh`.
7. Para editar o artigo, trabalhe no Overleaf. O artigo não faz parte deste repositório.

## Próxima ação recomendada

Revisar o conteúdo com o orientador, especialmente a interpretação do teste externo negativo e os limites de uso em uma instalação real. Alterações do artigo são feitas e preservadas no Overleaf; alterações do software e da documentação são registradas no GitHub.

## Pontos de continuidade

1. Revisar a experiência visual do painel como tela de apresentação, sem alterar o escopo metodológico.
2. Fechar a revisão final do texto com o orientador, especialmente interpretação dos resultados e limites.
3. Gerar slides a partir dos resultados reproduzíveis, deixando métricas detalhadas fora do painel leigo.
4. Antes da entrega, reproduzir os comandos documentados em `README.md` em uma instalação limpa e registrar qualquer ajuste necessário.
