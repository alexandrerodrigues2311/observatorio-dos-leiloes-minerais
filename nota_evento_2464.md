# Lance vencedor, pagamento e retorno à disponibilidade

O estudo passa a distinguir três objetos: valor da proposta vencedora, pagamento efetivamente confirmado e recolhimentos posteriores de CFEM. O resultado “Arrematada” no SOPLE não comprova ingresso de receita.

O processo 300.001/2020 aparece como área 390 da 4ª rodada, com lance de R$ 1.013,00. No Cadastro Mineiro, o evento 2464, “DISPONIB/LEILÃO ELET/PROPOSTA NÃO PAGA/RETORNO DISPONIB”, tem data de 14/12/2021. A associação do processo a 835.028/2011 foi registrada em 03/01/2020, antes da rodada, e não deve ser interpretada automaticamente como requerimento posterior do vencedor.

A busca reproduzível em ProcessoEvento.csv encontrou 1.095 origens distintas do universo acompanhado com evento 2464 na própria origem ou em um associado candidato, após a homologação de referência e até 30/06/2026. Os eventos são deduplicados por processo, data, código e observação. O painel recalcula o recorte temporal quando o usuário altera o marco para associação. Os grupos de restrições podem se sobrepor.

Esse indicador identifica ocorrências administrativas históricas, não dívida atual. Uma proposta pode ter atos posteriores, reoferta ou outra trajetória. É necessária conciliação por proposta, rodada e documento de arrecadação antes de deduzir valores dos lances ou divulgar receita efetivamente paga. Ausência de evento 2464 também não comprova pagamento.

Implicação: incorporar ao fluxo analítico a etapa “lance → pagamento/retorno → requerimento e associação → atividade e CFEM”. A ausência de associado não deve ser atribuída exclusivamente a falha de dados. O retorno documentado é uma hipótese administrativa verificável, a ser examinada caso a caso. Não confundir não pagamento da proposta com inadimplência de CFEM.

Fontes: ResultadoRodadaDisponibilidade.csv, Evento.csv, ProcessoEvento.csv e ProcessoAssociacao.csv, extração local de setembro/2026. Auditoria reproduzível em work/audit_unpaid_bids.py; evidências e hash em work/unpaid_bids.json. Nenhum modelo foi retreinado e os resultados anteriores não foram convertidos em estimativas de receita líquida.
