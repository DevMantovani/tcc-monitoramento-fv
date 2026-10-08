# Dados selecionados para auditoria inicial

## Fonte e proveniência

O recorte de auditoria usa dados reais do sistema **PVDAQ 1433 — NREL RSF1**, disponibilizado pelo National Renewable Energy Laboratory (NREL) na Open Energy Data Initiative (OEDI), do Departamento de Energia dos Estados Unidos.

- Conjunto: *Photovoltaic Data Acquisition (PVDAQ) Public Datasets*.
- DOI do conjunto: [10.25984/1846021](https://doi.org/10.25984/1846021).
- Catálogo e licença: [página oficial OEDI](https://data.openei.org/submissions/4568).
- Documentação dos campos e do formato: [PVDAQ data documentation](https://github.com/openEDI/documentation/blob/main/pvdaq.md).
- Sistema: `1433`, NREL RSF1, Golden, Colorado, EUA.
- Metadados: sistema fixo em telhado, capacidade CC informada de 449,28 kW, inclinação de 10° e azimute de 180°.

Os arquivos brutos ficam em `data/raw/pvdaq_1433_2017/`, ignorados pelo Git. A proveniência e o código de preparação, não os arquivos, devem ser versionados.

## Recorte baixado

O primeiro recorte contém cada arquivo diário de **2017**, com medições a cada 15 minutos. O ano foi escolhido por estar completo no caminho público de CSV verificado durante a coleta. Ele é um recorte de auditoria, não a declaração definitiva de que o período ou o sistema são os melhores para a pesquisa.

As quatro variáveis candidatas, presentes nos arquivos, são:

| Campo na fonte | Papel planejado |
|---|---|
| `measured_on` | horário da medição |
| `ac_power__5069` | potência CA observada |
| `poa_irradiance__5061` | irradiância no plano dos módulos |
| `module_temp__5063` | temperatura do módulo |
| `ambient_temp__5062` | temperatura ambiente, mantida para inspeção; não entra automaticamente no modelo |

O arquivo também inclui leituras de energia. Nesta etapa elas não serão usadas como entrada nem saída do modelo.

## Auditoria executada em 08/10/2026

| Verificação | Resultado |
|---|---:|
| Arquivos diários | 365 |
| Registros | 35.040 |
| Período | 01/01/2017 00:00 a 31/12/2017 23:45 |
| Frequência observada | 15 minutos em 100% dos intervalos consecutivos |
| Timestamps duplicados | 0 |
| Irradiância, temperatura do módulo e ambiente presentes | 97,4% |
| Potência CA presente | 56,8% |
| Quatro variáveis principais presentes | 19.908 registros (56,8%) |
| Registros diurnos com irradiância ≥ 50 e potência não negativa | 8.186 (23,4%) |

## Limites e decisões pendentes

1. A potência possui lacunas; elas não serão preenchidas automaticamente. A preparação deverá registrar quantos registros são removidos.
2. Os nomes de coluna identificam as grandezas, mas a confirmação final das unidades deverá ser feita com os metadados de métricas do PVDAQ antes de o texto do TCC declarar unidades ou calcular métricas finais.
3. O conjunto não traz, neste recorte, um rótulo independente de sujeira ou uma lista de limpezas. Portanto, ele sustenta a etapa de estimativa de potência, mas **não permite afirmar detecção de sujidade real**.
4. A escolha de modelo, a regra de alerta e o período final ainda precisam ser discutidos e aprovados antes de qualquer experimento formal.
