import json,re,collections,copy,csv,io,zipfile
from pathlib import Path
p=Path('.');d=json.loads(re.search(r'<script id="data"[^>]*>(.*?)</script>',(p/'outputs/Observatorio_Leiloes_Minerais.html').read_text(encoding='utf-8'),re.S)[1]);rows={r['origem']:r for r in d['rows']};E=d['enrichment'];result={};cycle_rows={}
def mi(s):return int(s[:4])*12+int(s[5:7])-1
def metric(v,months):
 amounts=collections.Counter();n=0
 for x in v:amounts[x[0]]+=x[6];n+=x[7]
 total=sum(amounts.values())/100
 return {'reais':total,'registros':n,'meses_observados':len(months),'meses_com_positivo':sum(v>0 for v in amounts.values()),'positivo':any(v>0 for v in amounts.values()),'media_mensal':total/len(months) if months else None,'reais_sem_linhas_identicas_sensibilidade':None}
for origin,a in d['reviewedCases'].items():
 if a['kind']=='missing_link':continue
 r=copy.deepcopy(rows[origin]);awards=sorted(r['arrematacoes'],key=lambda x:x['homologacao_referencia']);windows=[]
 for link in r['vinculos']:
  candidates=[v for v in awards if v['homologacao_referencia']<=link['associacao']]
  # Same-month date conflict is reconciled for MONTHLY comparison only, never dates.
  if not candidates:
   candidates=[v for v in awards if v['homologacao_referencia'][:7]==link['associacao'][:7]]
   assert candidates and any(e[0]==link['associacao'] and e[2]=='2293' for e in r['eventos'])
  award=candidates[-1];child=link['processo'];start=max(award['homologacao_referencia'][:7],link['associacao'][:7]);next_dates=[x['homologacao_referencia'][:7] for x in awards if x['homologacao_referencia']>award['homologacao_referencia']]
  if child in rows:next_dates += [x['homologacao_referencia'][:7] for x in rows[child]['arrematacoes'] if x['homologacao_referencia']>award['homologacao_referencia']]
  end=min(next_dates) if next_dates else '2026-07';w={'process':child,'round':award['rodada'],'award':award['homologacao_referencia'],'association':link['associacao'],'startExcluded':start,'endExcluded':end};windows.append(w)
 vals=[];seen=set();months=set()
 for w in windows:
  months.update(m for m in d['coverage'] if mi(w['startExcluded'])<m<mi(w['endExcluded']))
  for i,x in enumerate(E['profiles'].get(w['process'],[])):
   if w['startExcluded']<x[0]<w['endExcluded'] and (w['process'],i)not in seen:vals.append(x);seen.add((w['process'],i))
 r['cycleWindows']=windows;r['problemas_vinculo']=[];r['depois']=metric(vals,months);r['transicao']={(False,False):'sem_positivo_antes_e_depois',(False,True):'passou_a_recolher',(True,False):'sem_positivo_depois',(True,True):'recolhia_e_continuou'}[(r['antes']['positivo'],r['depois']['positivo'])];r['primeiro_depois']=min((x[0]for x in vals if x[6]>0),default=None)
 post=collections.Counter()
 for x in vals:post[x[0]]+=x[6]
 monthly={x[0]:list(x) for x in r['mensal']}
 for m,c in post.items():monthly.setdefault(m,[m,0,0,0])[2]=c
 r['mensal']=sorted(monthly.values());annual={}
 for m,pre,after,old in r['mensal']:
  arow=annual.setdefault(m[:4],[0,0,0]);arow[0]+=pre;arow[1]+=after;arow[2]+=old
 r['anual']=annual;cycle_rows[origin]=r
# Complete directed lineage, with loop protection, for every award origin.
links=collections.defaultdict(list)
with zipfile.ZipFile('work/scm.zip') as z:
 for v in csv.DictReader(io.TextIOWrapper(z.open('microdados-scm/ProcessoAssociacao.txt'),encoding='cp1252'),delimiter=';'):
  if v['IDTipoAssociacao']=='8':links[v['DSProcesso']].append({'process':v['DSProcessoAssociado'],'date':v['DTAssociacao']})
graph={} 
for origin in rows:
 seen=set();todo=[origin];edges=[]
 while todo:
  src=todo.pop()
  if src in seen:continue
  seen.add(src)
  for l in links.get(src,[]):
   if l['date']>'2026-06-30':continue
   edges.append({'from':src,'to':l['process'],'date':l['date']});todo.append(l['process'])
 graph[origin]=edges
result={'rows':cycle_rows,'graph':graph,'method':'Monthly attribution: direct successor after both association month and award month, ending before the month of the next award of the origin or successor. Boundary months excluded; each profile group counted once. Whole chain displayed but descendant cycle revenue not added twice. Same-month date conflict reconciled only at monthly level with opening event; source dates preserved.'}
(p/'work/cycle_resolution.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8');print('Resolved',len(cycle_rows),'CFEM added',sum(r['depois']['reais']for r in cycle_rows.values()));print('322',rows['300.322/2018']['sucessores_candidatos'],d['businessOutcomes']['origins']['300.322/2018']['state'])
