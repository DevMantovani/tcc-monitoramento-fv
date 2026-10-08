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
5. O conjunto permite treinar e avaliar um monitor que estima potência limpa esperada com variáveis ambientais e a compara à potência efetivamente medida. O módulo limpo e sua potência não são requisitos da implantação: são a referência supervisionada desta fase experimental. Uma regra de limpeza economicamente recomendada ainda exige custo de limpeza, valor/tarifa da energia, previsão de chuva e persistência da perda.

## Fonte secundária auditada: PVDAQ 1433 — NREL RSF1

Também foi auditado o sistema **PVDAQ 1433 — NREL RSF1**, disponibilizado pelo National Renewable Energy Laboratory (NREL) na Open Energy Data Initiative (OEDI), do Departamento de Energia dos Estados Unidos.

- Conjunto: *Photovoltaic Data Acquisition (PVDAQ) Public Datasets*.
- DOI: [10.25984/1846021](https://doi.org/10.25984/1846021).
- Catálogo e licença: [página oficial OEDI](https://data.openei.org/submissions/4568).
- Documentação dos campos: [PVDAQ data documentation](https://github.com/openEDI/documentation/blob/main/pvdaq.md).
- Recorte: 365 arquivos de 2017, 35.040 registros a cada 15 minutos, sem timestamps duplicados.

Ele possui potência CA, irradiância no plano e temperaturas úteis para estudos de desempenho. Porém, no recorte auditado não há rótulo independente de sujidade nem um histórico de limpezas. Por isso, é uma fonte secundária para análise de desempenho e possível validação externa, mas não a base principal para afirmar detecção de sujidade real.
