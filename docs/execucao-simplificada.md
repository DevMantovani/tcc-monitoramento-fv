# Execução simplificada do painel

O painel pode ser aberto sem digitar comandos de Python. Os atalhos criam o ambiente local na primeira vez, instalam as dependências do projeto e abrem o navegador. Nas execuções seguintes, apenas verificam se os resultados locais necessários já existem.

## Antes da primeira execução

1. Instale Python entre as versões 3.11 e 3.13.
2. As duas fontes públicas usadas pelo painel já acompanham o repositório nestes caminhos e nomes:

   ```text
   data/raw/laghouat_2022/Laghouat_2022_final.csv
   data/raw/zenodo_inverter_2023_2024/math_model_all_inverters_03.11.2023-25.06.2024.csv
   ```

   Elas são distribuídas sob CC BY 4.0, preservam os nomes originais e têm DOI, licença e checksum descritos em [dados.md](dados.md). O primeiro preparo executa os experimentos reproduzíveis localmente.

## Abrir o painel

- **Windows:** dê duplo clique em `iniciar_painel.bat`.
- **Linux/macOS:** abra um terminal na pasta do projeto e execute `bash iniciar_painel.sh`.

Quando estiver pronto, o navegador abrirá o endereço `http://127.0.0.1:8501`. Para encerrar, feche o terminal que abriu o painel ou pressione `Ctrl+C` nele.

Caso os resultados ainda não existam, o atalho os prepara automaticamente a partir das duas fontes públicas. A fonte de Dhaka usada apenas no teste externo também acompanha o repositório; seu protocolo está em [validacao-externa.md](validacao-externa.md).

## Atualizar o projeto

Depois de receber uma atualização pelo GitHub, use o mesmo atalho. Ele instala a versão atual do projeto antes de abrir o painel. Se for necessário reproduzir os resultados deliberadamente, use o comando documentado em [reproducao.md](reproducao.md).
