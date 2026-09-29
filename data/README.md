# Contrato dos dados

O pipeline recebe um CSV com cabeçalho e, no mínimo, estas colunas:

| Coluna | Unidade | Significado |
|---|---:|---|
| `timestamp` | data/hora ISO 8601 | instante da medição, com fuso consistente |
| `irradiance_wm2` | W/m² | irradiância no plano dos módulos, se disponível |
| `module_temperature_c` | °C | temperatura do módulo; não substituir por temperatura ambiente sem registrar a mudança |
| `power_kw` | kW | potência observada no mesmo instante |

Colunas adicionais, como chuva, vento, estado de limpeza e identificador do inversor, podem ser preservadas. Não entram no modelo inicial até haver justificativa, disponibilidade temporal e verificação de vazamento.

`data/raw/` guarda o arquivo recebido e não entra no Git. Registre no experimento a origem, licença, período, unidade, fuso horário, frequência, lacunas e filtros aplicados. Arquivos em `data/processed/` também são locais; o código que os produz e o registro das decisões são o que permitem a reprodução.
