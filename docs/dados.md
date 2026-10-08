# Dados e proveniência

## Base supervisionada de desenvolvimento e validação: experimento de Laghouat

A base de desenvolvimento e validação desta etapa é **Hourly PV Power and Dust Accumulation Dataset — Laghouat, Algeria, February–August 2022**, publicada no Mendeley Data. Ela não é o objeto final do TCC. Seu papel é fornecer um rótulo de referência que normalmente não existe numa usina em operação: a diferença medida entre módulos iguais, um lavado diariamente e outro exposto ao acúmulo natural de poeira.

- Publicação, licença e download: [Mendeley Data — DOI 10.17632/4jdt83yy43.3](https://doi.org/10.17632/4jdt83yy43.3), licença CC BY 4.0.
- Arquivo de origem: `Laghouat_2022_final.csv`.
- Período: 17/02/2022 00:00 a 17/08/2022 23:00.
- Frequência: horária.
- Linhas: 4.368, sem timestamps duplicados.
- Integridade do arquivo baixado: SHA-256 `5552bb039c5673eea21537a551b0fe8cd9ce75429027f6a334eeb404ba934d43`.

Os dados brutos ficam em `data/raw/laghouat_2022/` e a cópia preparada em `data/processed/laghouat_2022.csv`; ambos são ignorados pelo Git. O repositório versiona o código de preparação, a documentação e os testes, não a redistribuição do arquivo de origem.

### Variáveis usadas nesta fase

| Campo publicado | Nome preparado | Uso |
|---|---|---|
| `datetime` | `timestamp` | instante da observação |
| `G_POA_Wm2` | `poa_irradiance_wm2` | filtro de condição diurna e contexto ambiental |
| `P_clean_W` | `power_clean_w` | potência de referência do painel lavado diariamente |
| `P_dusty_W` | `power_dusty_w` | potência do painel exposto à poeira |
| `dust_density_reconstructed_PCHIP_gm2` | `dust_density_reconstructed_gm2` | acompanhamento exploratório do acúmulo de poeira |
| `temp_amb_C`, `T_cell_C`, `RH_pct`, `wind_speed_ms`, `cloud_cover_pct`, `precipitation_mm` | nomes normalizados quando aplicável | contexto para análises posteriores |

O indicador observado é calculado somente quando a irradiância no plano é de pelo menos 50 W/m² e a potência do painel limpo é positiva:

```text
perda_por_sujidade = (potência_limpa − potência_exposta) / potência_limpa
```

Após esse filtro, há 1.860 observações diurnas válidas. Neste recorte, a perda mediana é 15,27%, a média é 13,43% e o percentil 90 é 22,45%. Esses números descrevem essa base experimental; não devem ser generalizados automaticamente para outra usina.

### Cuidados metodológicos

1. O painel de referência foi lavado diariamente. A comparação é muito útil para observar a diferença entre painel limpo e exposto, mas não representa por si só a rotina operacional de qualquer instalação.
2. Há 48 medições diretas de densidade de poeira. A série horária de densidade reconstruída foi fornecida pelos autores por interpolação PCHIP; ela é exibida como contexto, não como uma medição direta a cada hora.
3. O estudo cobre um local e aproximadamente seis meses. Temperatura, chuva, regime de poeira, orientação, tecnologia dos módulos e operação podem mudar o comportamento em outro cenário.
4. Valores negativos pontuais de perda podem ocorrer por ruído de medição ou condições experimentais; eles não significam “sujidade negativa”.
5. O conjunto permite treinar e avaliar um monitor que estima potência limpa esperada com variáveis ambientais e a compara à potência efetivamente medida. O módulo limpo e sua potência não são requisitos da implantação: são a referência supervisionada desta fase experimental. O MVP não propõe uma regra econômica de limpeza.

## Teste externo de transferibilidade: painéis limpo e exposto em Dhaka

Foi auditada uma segunda fonte com referência independente entre painel limpo e painel exposto: **A comprehensive dataset for monitoring photovoltaic panels and weather parameters in urban Bangladesh**, DOI [10.17632/g6pxf8nnt6.2](https://doi.org/10.17632/g6pxf8nnt6.2), CC BY 4.0. O repositório informa dois módulos monocristalinos de 20 W, um limpo regularmente e outro não limpo, com medições a cada 30 segundos entre novembro de 2019 e outubro de 2020.

- Arquivo de origem: `Solar Dataset.zip`, baixado da versão 2; SHA-256 local `078e222ca8a7e614ef3b31a0ffba34f4036e1e7aff626359c78643069ce6614c`.
- Auditoria do conteúdo: o ZIP contém 295 CSVs diários, não os 365 dias sugeridos pela descrição. Os arquivos somam 408.059 leituras de 01/11/2019 a 30/10/2020.
- Variações corrigidas de forma explícita: quatro arquivos trazem grafias ou espaçamentos diferentes em `Time` ou `Clean Temperature`; a data é recuperada do nome do arquivo, pois parte dos CSVs usa datas ambíguas entre dia/mês e mês/dia.
- Preparação: as leituras de 30 segundos são agregadas por hora, produzindo 3.720 registros horários, dos quais 3.357 atendem ao filtro de irradiância e potência de referência positiva.
- Entradas operacionais mínimas: irradiância ideal fornecida pela fonte e temperatura do painel exposto. Vento, umidade e pressão são preservados como contexto, mas não entram no modelo mínimo atual.

Essa base é uma validação externa mais aderente ao objetivo de sujidade do que a fonte Zenodo, mas não é residencial brasileira. Seus campos de irradiância e potência são derivados/calculados pelos autores, e a frequência de arquivos faltantes, as variações de cabeçalho e a proporção de perdas negativas exigem cautela adicional.

## Fonte complementar auditada: inversores fotovoltaicos e meteorologia, 2023--2024

Para avaliar a parte genérica de **estimação de potência** em outra instalação e em dados mais recentes, foi auditada a base *Photovoltaic Inverter Production and Meteorological data*.

- Publicação e download: [Zenodo — DOI 10.5281/zenodo.17775544](https://doi.org/10.5281/zenodo.17775544), licença CC BY 4.0.
- Autoria e proveniência: pesquisadores da University of Cyprus e University of Nicosia, com ORCIDs declarados, artigo associado e financiamento europeu registrados na página do conjunto.
- Arquivo utilizado: `math_model_all_inverters_03.11.2023-25.06.2024.csv`; checksum publicado MD5 `56d62f535b1ee8a0270e17e225f15524` e SHA-256 local `5a5d21e1d1228860841c257dc3b5dbb24f72b9e09abb8efa92b1561a34ae814a`.
- Fonte das medições: potência observada nos inversores; as variáveis meteorológicas foram obtidas da API Open-Meteo e os ângulos solares, calculados com Astral.
- Recorte de avaliação: `inverter1`, área de painel declarada de 107,1 m²; 3.185 registros horários entre 03/11/2023 e 25/06/2024, sem valores ausentes ou timestamps duplicados dentro do inversor.

O processamento usa `inverter` como potência observada, `global_tilted_irradiance (W/m²)` como irradiância e `temperature_2m (°C)` como temperatura **ambiente**. A coluna `energy` é uma previsão já calculada pelos autores da fonte e é deliberadamente excluída: utilizá-la como entrada ou alvo criaria vazamento de informação.

Após o filtro de irradiância ≥ 50 W/m², restaram 1.316 observações. Há lacunas longas na série, de aproximadamente 33 e 69 dias, e não existe medição independente de sujidade, par de módulos limpo/exposto ou histórico de limpezas. Assim, essa base não valida alertas, limiares ou decisão de limpeza; ela avalia somente se o fluxo de previsão de potência se reproduz em outra instalação.
