"""All auction origins, CFEM payer means, observed through June 2026.
Standalone analysis of source files. Never overwrites frozen 2025 experiments.
"""
import pathlib,json,csv,collections,decimal,hashlib,zipfile,io,datetime,statistics
P=pathlib.Path(__file__).resolve().parent.parent;W=P/'work';O=P/'outputs';CUT='2026-06-30'
dates={1:'2020-12-24',2:'2021-05-18',3:'2021-07-30',4:'2021-10-29',5:'2022-09-14',8:'2024-10-21'}
sources={
1:'https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?captchafield=firstAccess&data=24%2F12%2F2020&jornal=530&pagina=137',
2:'https://anmlegis.datalegis.net/action/ActionDatalegis.php?acao=abrirTextoAto&cod_menu=8938&cod_modulo=351&link=S&numeroAto=18052021&orgao=ANM%2FMME&seqAto=000&tipo=DIP&valorAno=2021',
3:'https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?captchafield=firstAccess&data=30%2F07%2F2021&jornal=530&pagina=120',
4:'https://anmlegis.datalegis.net/action/ActionDatalegis.php?acao=abrirTextoAto&cod_menu=9226&cod_modulo=351&link=S&numeroAto=29102021&orgao=ANM%2FMME&seqAto=000&tipo=DIP&valorAno=2021',
5:'https://anmlegis.datalegis.net/action/ActionDatalegis.php?acao=abrirResenhaAnoNumero&ano=2022&cod_menu=8938&cod_modulo=351',
8:'https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?captchafield=firstAccess&data=21%2F10%2F2024&jornal=530&pagina=101'}
override_source='https://www.gov.br/anp/pt-br/assuntos/consultas-e-audiencias-publicas/consulta-previa/2024/cp-03-2024/aviso-alteracao-prazo.pdf'
def key(s):
    a,b=s.replace('.','').strip().split('/');return a.zfill(6)+'/'+b
def idx(s):
    y,m=map(int,s[:7].split('-'));return y*12+m-1
def proc(k):return k[:3]+'.'+k[3:]
def digest(f):return hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
names=['ResultadoRodadaDisponibilidade.csv','scm.zip','cfem_historico_2002/CFEM_Arrecadacao_2002_2006.csv','cfem_historico_2002/CFEM_Arrecadacao_2007_2011.csv','cfem_historico_2002/CFEM_Arrecadacao_2012_2016.csv','CFEM_Arrecadacao_2017_2021.csv','CFEM_Arrecadacao_2022_2026.csv']
hashes={n:digest(W/n) for n in names}
won=collections.defaultdict(list);seen=set()
with (W/names[0]).open(encoding='utf-8-sig',newline='') as f:
    for r in csv.DictReader(f,delimiter=';'):
        if r['Situacao']!='Arrematada':continue
        identity=(r['Rodada'],r['NumeroArea'],key(r['ProcessoMinerario']))
        if identity in seen:continue
        seen.add(identity);rd=int(r['Rodada']);assert rd in dates
        dt='2024-12-16' if rd==8 and r['NumeroArea']=='1609' else dates[rd]
        won[identity[2]].append({'rodada':rd,'area':r['NumeroArea'],'homologacao_referencia':dt})
anchors={a:min(r['homologacao_referencia'] for r in rr) for a,rr in won.items()}
links={};protocols={};link_issues=collections.Counter()
with zipfile.ZipFile(W/'scm.zip') as z:
    assert z.testzip() is None
    for r in csv.DictReader(io.TextIOWrapper(z.open('microdados-scm/ProcessoAssociacao.txt'),encoding='cp1252'),delimiter=';'):
        if None in r or any(v is None for v in r.values()):continue
        if r['IDTipoAssociacao']!='8':continue
        a,b=key(r['DSProcesso']),key(r['DSProcessoAssociado']);dt=r['DTAssociacao']
        for parent,child in [(a,b)]:
            if parent not in won or child==parent:continue
            if not dt or dt>CUT or dt<'2020-01-01' or not 2020<=int(child.split('/')[1])<=2026:continue
            pair=(parent,child)
            if pair not in links or dt<links[pair]['date']:links[pair]={'date':dt,'end':r['DTDesassociacao']}
    keys=set(won)|{b for a,b in links}
    for r in csv.DictReader(io.TextIOWrapper(z.open('microdados-scm/Processo.txt'),encoding='cp1252'),delimiter=';'):
        if None in r or any(v is None for v in r.values()):continue
        k=key(r['DSProcesso'])
        if k in keys:protocols[k]=r['DTProtocolo']
print('Origins and links loaded',len(won),len(links),flush=True)
# Pre-existing branches are history, not children created after this award.
# Keep all raw links auditable. Only exclude earlier branches when a dated,
# post-award successor exists; isolated date conflicts remain unresolved.
historical_links={}
for a in won:
    candidates=[(b,v) for (parent,b),v in links.items() if parent==a]
    has_post=any(v['date']>=anchors[a] and protocols.get(b) and protocols[b][:10]>=anchors[a] for b,v in candidates)
    if has_post:
        for b,v in candidates:
            if v['date']<anchors[a] and (not protocols.get(b) or protocols[b][:10]<anchors[a]):
                historical_links[(a,b)]=v
for pair in historical_links:del links[pair]
reverse=collections.defaultdict(set);families=collections.defaultdict(dict)
for (a,b),v in links.items():reverse[b].add(a);families[a][b]=v
values=collections.defaultdict(collections.Counter);counts=collections.defaultdict(collections.Counter);dedup=collections.defaultdict(collections.Counter)
coverage=set();source_audit={}
for name in names[2:]:
    seen=set();n=0;matched=0
    with (W/name).open(encoding='cp1252',newline='') as f:
        for r in csv.DictReader(f):
            n+=1;y,m=int(r['Ano']),int(r['Mês']);assert 1<=m<=12
            if (y,m)<(2002,1) or (y,m)>(2026,6):continue
            t=y*12+m-1;coverage.add(t);k=key(r['Processo']+'/'+r['AnoDoProcesso'])
            if k not in keys:continue
            matched+=1;v=int(decimal.Decimal(r['ValorRecolhido'].replace('.','').replace(',','.'))*100)
            values[k][t]+=v;counts[k][t]+=1;fp=tuple(r.values())
            if fp not in seen:dedup[k][t]+=v;seen.add(fp)
    source_audit[name]={'source_rows':n,'matched_rows_through_cutoff':matched}
START=min(coverage);END=idx('2026-06');missing_months=sorted(set(range(START,END+1))-coverage);assert set(range(idx('2020-12'),END+1)).issubset(coverage)
def measure(processes,months):
    cents=sum(values[k][m] for k in processes for m in months)
    n=sum(counts[k][m] for k in processes for m in months)
    positive=[m for m in months if sum(values[k][m] for k in processes)>0]
    return {'reais':cents/100,'registros':n,'meses_observados':len(months),'meses_com_positivo':len(positive),
            'positivo':bool(positive),'media_mensal':cents/100/len(months) if months else None,
            'reais_sem_linhas_identicas_sensibilidade':sum(dedup[k][m] for k in processes for m in months)/100}
rows=[]
for a,awards in sorted(won.items()):
    dt=anchors[a];t=idx(dt);protocol=protocols.get(a)
    # Missing protocol stays in inventory. Process year is a conservative denominator proxy, explicitly flagged.
    first=max(START,idx(protocol)+1 if protocol else int(a.split('/')[1])*12)
    premonths=[m for m in range(first,t) if m in coverage];postmonths=list(range(t+1,END+1))
    assert premonths and postmonths
    before=measure([a],premonths);issues=[];children=sorted(families[a])
    if len(awards)>1:issues.append('origem_com_multiplas_arrematacoes')
    if not children:issues.append('sem_sucessor_tipo8_identificado')
    for b,v in families[a].items():
        if len(reverse[b])>1:issues.append('sucessor_compartilhado')
        if b in won:issues.append('sucessor_tambem_origem_arrematada')
        if v['end'] and v['end']<=CUT:issues.append('vinculo_desassociado')
        if v['date']<dt:issues.append('associacao_anterior_homologacao')
    issues=sorted(set(issues))
    after=measure(children,postmonths) if not issues else None
    transition=None
    if after is not None:
        transition={(True,True):'recolhia_e_continuou',(False,True):'passou_a_recolher',(True,False):'sem_positivo_depois',(False,False):'sem_positivo_antes_e_depois'}[(before['positivo'],after['positivo'])]
    rows.append({'origem':proc(a),'arrematacoes':awards,'data_referencia':dt,'protocolo_origem':protocol,
                 'inicio_media_estimado_pelo_ano':not bool(protocol),'inicio_observacao':f'{first//12:04}-{first%12+1:02}',
                 'antes':before,'sucessores_candidatos':[proc(b) for b in children],'problemas_vinculo':issues,
                 'depois':after,'transicao':transition,
                 'cfem_no_numero_original_depois_diagnostico':measure([a],postmonths),
                 'serie_anual_antes':{str(y):sum(values[a][m] for m in premonths if m//12==y)/100 for y in range(2002,2027)},
                 'serie_anual_depois':{str(y):sum(values[b][m] for b in children for m in postmonths if m//12==y)/100 for y in range(2002,2027)} if after is not None else None})
def summary(rr,side):
    valid=[r for r in rr if r[side] is not None];pay=[r for r in valid if r[side]['positivo']]
    total=sum(r[side]['reais'] for r in valid);payer_total=sum(r[side]['reais'] for r in pay)
    exposure=sum(r[side]['meses_observados'] for r in pay);active=sum(r[side]['meses_com_positivo'] for r in pay)
    return {'processos_avaliaveis':len(valid),'com_recolhimento_positivo':len(pay),
            'sem_registro':sum(r[side]['registros']==0 for r in valid),
            'com_registro_sem_positivo':sum(r[side]['registros']>0 and not r[side]['positivo'] for r in valid),
            'cfem_total_encontrada_reais':round(total,2),'cfem_dos_recolhedores_reais':round(payer_total,2),
            'media_mensal_so_recolhedores_ponderada':payer_total/exposure if exposure else None,
            'media_simples_das_medias_mensais_so_recolhedores':statistics.mean(r[side]['media_mensal'] for r in pay) if pay else None,
            'media_anual_equivalente_so_recolhedores':payer_total/exposure*12 if exposure else None,
            'meses_processo_dos_recolhedores':exposure,'media_por_mes_com_pagamento_diagnostico':payer_total/active if active else None,
            'sensibilidade_sem_linhas_identicas_reais':round(sum(r[side]['reais_sem_linhas_identicas_sensibilidade'] for r in valid),2)}
paired=[r for r in rows if r['depois'] is not None]
transitions=dict(collections.Counter(r['transicao'] for r in paired));assert sum(transitions.values())==len(paired)
summary_all={'arrematacoes_area_rodada':sum(len(v) for v in won.values()),'processos_distintos_arrematados':len(won),
             'antes_todos':summary(rows,'antes'),'depois_com_vinculo_avaliavel':summary(rows,'depois'),
             'antes_mesma_coorte_pareada':summary(paired,'antes'),'transicoes':transitions,
             'depois_nao_avaliaveis':len(rows)-len(paired),
             'sucessores_distintos_na_coorte':len({b for r in paired for b in r['sucessores_candidatos']}),
             'antes_recolhedores_sem_seguimento':sum(r['antes']['positivo'] for r in rows if r['depois'] is None),
             'meses_sem_registro_na_base_inteira_excluidos_denominador':[f'{m//12:04}-{m%12+1:02}' for m in missing_months],
             'meses_2026_presentes':sorted({m%12+1 for m in coverage if m//12==2026}),
             'origens_media_com_ano_aproximado':sum(r['inicio_media_estimado_pelo_ano'] for r in rows),
             'recolhedores_antes_media_com_ano_aproximado':sum(r['inicio_media_estimado_pelo_ano'] and r['antes']['positivo'] for r in rows),
             'problemas_nao_exclusivos':dict(collections.Counter(x for r in rows for x in r['problemas_vinculo']))}
by_round={str(rd):{'antes':summary([r for r in rows if any(x['rodada']==rd for x in r['arrematacoes'])],'antes'),
                   'depois':summary([r for r in rows if any(x['rodada']==rd for x in r['arrematacoes'])],'depois')} for rd in dates}
assert all(digest(W/n)==h for n,h in hashes.items()),'Source mutated during analysis'
report={'executed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cutoff':CUT,'start':f'{START//12:04}-{START%12+1:02}-01','status':'descritivo_exploratorio_homologacao_por_rodada',
        'summary':summary_all,'by_round':by_round,'records':rows,'hashes':hashes,'source_audit':source_audit,
        'homologacoes':dates,'fontes_homologacao':sources,'excecao_area_1609_rodada_8':{'data':'2024-12-16','fonte':override_source},
        'limits':['Marco e a publicacao da homologacao por rodada, com excecao conhecida da area 1609; nao e data individual de lance ou pagamento.',
                  'Retificacoes e situacoes individuais ainda exigem conferencia documental. Universo e situacao Arrematada no SOPLE; Conquistada nao incluida.',
                  'Historico inicia em agosto/2002 e tem lacunas globais ate abril/2003, excluidas do denominador; nao sao meses de CFEM zero.',
                  'Antes desde o inicio disponivel ou primeiro mes completo apos protocolo; onde protocolo falta, ano do processo usado como proxy de inicio e sinalizado.',
                  'Depois do mes seguinte a homologacao ate junho/2026. Mes da homologacao excluido. Valores nominais, nao efeito causal.',
                  'Medias principais restritas a processos com CFEM positiva, mas denominador inclui todos seus meses observados, inclusive sem pagamento.',
                  'Associacao tipo 8 e candidata a sucessao; nao certificada por vencedor/poligonal. Nao avaliavel nao e CFEM zero.',
                  'Mais de um sucessor por origem agregado uma vez; vinculos ambiguos excluidos da comparacao pareada. Outros desmembramentos nao rastreados.',
                  'Repeticoes integrais no CSV tratadas apenas como sensibilidade; sem identificador de transacao nao ha deduplicacao certificada.',
                  'Dados observados 2002-junho/2026 nao representam toda a vida de processos antigos; fontes extraidas em setembro/2026.']}
(O/'cfem_todas_arrematadas_jun2026.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
def fmt(v):return f'{v:,.2f}'.replace(',','X').replace('.',',').replace('X','.') if v is not None else 'Não disponível'
s=summary_all;pre=s['antes_todos'];post=s['depois_com_vinculo_avaliavel']
lines=['# CFEM dos processos arrematados até junho de 2026','',f"Universo: {s['arrematacoes_area_rodada']} arrematações em {s['processos_distintos_arrematados']} processos distintos, abrangendo todas as substâncias e rodadas comerciais da base. Não inclui Conquistada como Arrematada.",'',
       'Historico efetivamente encontrado desde agosto/2002; lacunas globais de meses foram excluidas do denominador. Observacao termina em junho/2026.', '', '## Antes e depois','', '| Indicador | Antes no universo de origens | Depois nos sucessores acompanháveis |','|---|---:|---:|']
for k,label in [('processos_avaliaveis','Origens avaliáveis'),('com_recolhimento_positivo','Origens com CFEM positiva'),('sem_registro','Origens sem registro encontrado'),('cfem_dos_recolhedores_reais','CFEM dos recolhedores acumulada (R$)'),('media_mensal_so_recolhedores_ponderada','Média mensal ponderada somente dos recolhedores (R$/processo-mês)'),('media_simples_das_medias_mensais_so_recolhedores','Média simples das médias mensais dos recolhedores (R$)'),('media_anual_equivalente_so_recolhedores','Média anual equivalente dos recolhedores (R$)')]:lines.append(f'| {label} | {fmt(pre[k])} | {fmt(post[k])} |')
lines+=['',f"A coluna depois tem {s['depois_nao_avaliaveis']} origens não avaliáveis. Não comparar os dois denominadores como se fossem a mesma amostra. Na mesma coorte pareada, antes: {s['antes_mesma_coorte_pareada']}.",'','## O que aconteceu com as mesmas origens','']
for k,v in transitions.items():lines.append(f'- {k}: {v}.')
lines+=['',f"Recolhedores anteriores sem seguimento avaliável: {s['antes_recolhedores_sem_seguimento']}. Sucessores distintos na coorte: {s['sucessores_distintos_na_coorte']}.",'',
        '## Interpretação','', 'A média solicitada é calculada somente entre processos com recolhimentos positivos. Para cada um, todos os meses do período observado entram no denominador, incluindo meses sem pagamento. A média ponderada divide o total recolhido pelos meses-processo dos recolhedores; a média simples dá o mesmo peso a cada recolhedor. A média dos meses com pagamento é apenas um diagnóstico, não a medida principal.', '',
        'As transições usam as mesmas origens com sucessão candidata acompanhável. Ausência de registro não comprova recolhimento zero ou ausência de atividade. O aumento ou redução após homologação não identifica efeito causal do leilão.', '', '## Recorte por rodada','']
for rd,v in by_round.items():lines.append(f"- Rodada {rd}: antes, {v['antes']['com_recolhimento_positivo']} recolhedores e R$ {fmt(v['antes']['cfem_dos_recolhedores_reais'])}; depois, {v['depois']['com_recolhimento_positivo']} origens com recolhimentos nos sucessores e R$ {fmt(v['depois']['cfem_dos_recolhedores_reais'])}.")
lines+=['','## Fontes e limitações','']+['- '+s for s in report['limits']]
for rd,u in sources.items():lines.append(f'- Homologação da rodada {rd}: {dates[rd]} — {u}')
lines+=['- Retificação área 1609, rodada 8: '+override_source,'- Microdados CFEM: https://dadosabertos.anm.gov.br/CFEM/','- Cadastro Mineiro: https://dadosabertos.anm.gov.br/SCM/microdados/','- SOPLE: https://dadosabertos.anm.gov.br/SOPLE/']
(O/'cfem_todas_arrematadas_jun2026.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(summary_all,ensure_ascii=True))
