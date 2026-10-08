# Avaliação científica consolidada

## Pergunta avaliada

O trabalho investiga se a diferença entre potência esperada em condição limpa e potência medida pode apoiar o monitoramento de perdas potencialmente associadas à sujidade. A pergunta não é qual algoritmo é superior nem se um modelo único funciona em qualquer sistema fotovoltaico.

## Protocolo

A base principal de Laghouat contém painéis equivalentes, um limpo diariamente e outro exposto à poeira. Ela permite calcular uma perda observada independente. Os dados foram separados cronologicamente em treino (60%), validação (20%) e teste final (20%). A escolha interna do estimador e do limiar ocorreu na validação; o teste final foi acessado somente depois.

O modelo selecionado internamente foi Ridge. A política congelada foi perda estimada de 15% por três dias consecutivos.

## Resultado no experimento controlado

No teste final de Laghouat, o monitor obteve:

| Indicador | Resultado |
|---|---:|
| Erro médio da potência limpa esperada | 0,29 W |
| Erro médio da perda estimada | 0,63 ponto percentual |
| Precisão dos alertas persistentes | 90,6% |
| Sensibilidade dos alertas persistentes | 100,0% |
| F1 dos alertas persistentes | 0,951 |

Esses valores mostram que o monitor acompanhou a diferença entre painel limpo e painel exposto **nas condições desse experimento**. Eles não representam desempenho residencial brasileiro nem autorização para limpeza automática.

## Teste externo e limite de generalização

O mesmo fluxo foi testado com uma segunda fonte pública de Dhaka, que também possui painéis limpo e exposto. A referência de potência foi ajustada no período de desenvolvimento local; a arquitetura Ridge e a política de alerta de Laghouat foram mantidas inicialmente.

O resultado não confirmou transferência automática: a MAE da perda foi 41,46 pontos percentuais e houve 26 alertas falsos no teste final com a política transferida. Mesmo com recalibração do limiar apenas na validação de Dhaka, o F1 final foi 0,043.

Portanto, o trabalho não sustenta que a regra de alerta ou a referência de geração possam ser copiadas entre instalações. O resultado externo negativo é parte central da evidência e direciona a proposta de calibração pós-limpeza por instalação.

## Escopo da contribuição

O protótipo entrega:

1. preparação rastreável de fontes públicas;
2. monitor de potência esperada, perda estimada e alerta persistente;
3. separação correta entre desenvolvimento e teste final;
4. fluxo operacional de calibração local após limpeza confirmada;
5. documentação explícita das limitações e da falha de transferência.

Ainda não entrega validação residencial real, diagnóstico exclusivo de sujidade ou decisão financeira automática. A próxima evidência necessária é telemetria de uma instalação com eventos de limpeza documentados.
