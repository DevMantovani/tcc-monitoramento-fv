# Cenário econômico residencial

## Finalidade e limite

Esta tela é uma **simulação de economia potencial**, não uma recomendação de limpeza nem uma projeção financeira de uma residência específica. Ela ajuda a interpretar a ordem de grandeza de uma perda detectada pelo monitor, mas depende de premissas que o usuário pode editar.

O cálculo exibido é:

```text
valor potencial recuperável = energia não gerada observada × valor da energia × recuperação assumida
saldo do cenário = valor potencial recuperável − custo de limpeza
```

A energia não gerada observada vem da diferença entre os painéis limpo e exposto do experimento de validação. Portanto, não deve ser apresentada como economia efetivamente alcançada por uma residência brasileira.

## Valores iniciais do painel

| Premissa | Valor inicial | Fundamentação e limite |
|---|---:|---|
| Valor da energia | R$ 0,80/kWh | Cenário de referência sem tributos. Uma compilação de tarifas residenciais da ANEEL informou essa mediana para 98 distribuidoras em setembro de 2026. A própria ANEEL esclarece que as tarifas homologadas em R$/kWh não incluem tributos, iluminação pública ou bandeiras. |
| Custo de limpeza | R$ 200 por visita | Ponto médio da faixa de R$ 150–250 por visita para sistema residencial acessível de até 16 módulos, reportada por fonte de mercado. O custo varia com acesso ao telhado, quantidade de módulos, deslocamento e região. |
| Recuperação após limpeza | 100% | Hipótese inicial editável; não é garantida. Chuva ou limpeza podem remover apenas parte da sujidade, conforme o material depositado e o procedimento. |

## Uso responsável

1. Substitua o valor de energia pela tarifa ou economia marginal aplicável à residência antes de discutir resultado individual.
2. Substitua o custo por orçamento local, pois não há preço único de limpeza residencial.
3. Ajuste a recuperação para uma hipótese conservadora quando não houver evidência de que a limpeza restaura toda a geração.
4. Não use o saldo mostrado como resultado científico do TCC. Ele serve apenas como análise de sensibilidade do protótipo; validar impacto econômico exige dados locais e eventos de limpeza documentados.

## Fontes

- [Tarifas de aplicação das distribuidoras — ANEEL](https://dadosabertos.aneel.gov.br/pt_BR/dataset/tarifas-distribuidoras-energia-eletrica): base pública de TE e TUSD, atualizada periodicamente.
- [Tarifas e informações econômico-financeiras — ANEEL](https://www.gov.br/aneel/pt-br/centrais-de-conteudos/relatorios-e-indicadores/tarifas-e-informacoes-economico-financeiras): ressalva sobre itens que não estão nas tarifas homologadas.
- [Referência de faixa de limpeza residencial](https://energiasolarexplicada.com.br/blog/limpeza-painel-solar/): utilizada somente para definir o cenário inicial editável.
- [Orientação de que não há preço padrão](https://www.karcher.com.br/br/dicas-karcher/limpeza-de-placas-solares-como-lavar.html): custo depende de acesso, tempo, deslocamento, equipamentos e porte.
