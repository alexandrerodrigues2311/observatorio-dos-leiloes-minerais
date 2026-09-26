import csv,json,zipfile,io,collections,decimal
from pathlib import Path
social=list(csv.DictReader(Path('work/ResultadoAvaliacaoSocial.csv').open(encoding='utf-8-sig'),delimiter=';'));social=[r for r in social if r['Rodada']=='6'];fmt=lambda s:s.replace('.','').split('/')[0].zfill(6)[:3]+'.'+s.replace('.','').split('/')[0].zfill(6)[3:]+'/'+s.split('/')[1];origins={fmt(r['ProcessoMinerario']):r for r in social if r['Situacao']=='Requerido'};links=collections.defaultdict(list);phases={}
with zipfile.ZipFile('work/scm.zip') as z:
 def rows(n):return csv.DictReader(io.TextIOWrapper(z.open('microdados-scm/'+n+'.txt'),encoding='cp1252'),delimiter=';')
 for r in rows('ProcessoAssociacao'):
  if r['IDTipoAssociacao']=='8' and r['DSProcesso'] in origins and '2022-09-01'<=r['DTAssociacao']<='2026-06-30':links[r['DSProcesso']].append({'process':r['DSProcessoAssociado'],'date':r['DTAssociacao']})
 children={v['process']for vs in links.values()for v in vs};names={r['IDFaseProcesso']:r['DSFaseProcesso'] for r in rows('FaseProcesso')}
 for r in rows('Processo'):
  if r['DSProcesso'] in children:phases[r['DSProcesso']]=names.get(r['IDFaseProcesso'])
monthly=collections.defaultdict(collections.Counter);profiles=collections.defaultdict(list)
with Path('work/CFEM_Arrecadacao_2022_2026.csv').open(encoding='cp1252',newline='') as f:
 for r in csv.DictReader(f):
  p=fmt(r['Processo']+'/'+r['AnoDoProcesso']);m=f"{int(r['Ano']):04}-{int(r['Mês']):02}"
  if p in children and m<='2026-06':
   value=int(decimal.Decimal(r['ValorRecolhido'].replace('.','').replace(',','.'))*100);monthly[p][m]+=value
   profiles[p].append({'month':m,'type':r['Tipo_PF_PJ'],'payer':('PF · final '+r['CPF_CNPJ'][-4:]) if r['Tipo_PF_PJ'].strip()=='PF' else r['CPF_CNPJ'],'substance':r['Substância'],'uf':r['UF'],'city':r['Município'],'quantity':r['QuantidadeComercializada'],'unit':r['UnidadeDeMedida'],'cents':value})
records=[]
for p,r in origins.items():
 ls=links[p];records.append({'origin':p,'area':r['NumeroArea'],'links':ls,'cfem_cents':sum(c for l in ls for m,c in monthly[l['process']].items() if m>l['date'][:7]),'phases':[phases.get(l['process'])for l in ls],'state':r['UnidadeFederacao'],'city':r['Municipio'],'winner':r['NomeVencedor'].upper(),'profiles':[{**x,'process':l['process']}for l in ls for x in profiles[l['process']] if x['month']>l['date'][:7]]})
out={'requested':len(origins),'with_links':sum(bool(r['links'])for r in records),'children':len(children),'phases':dict(collections.Counter(phases.values())),'cfem_origins':sum(r['cfem_cents']>0 for r in records),'cfem_cents':sum(r['cfem_cents']for r in records),'records':records,'inventory':[{'area':r['NumeroArea'],'origin':fmt(r['ProcessoMinerario']),'status':r['Situacao'],'state':r['UnidadeFederacao'],'city':r['Municipio'],'winner':r['NomeVencedor'].upper()}for r in social],'note':'Preliminary direct links after Sep2022; monthly CFEM after association. Requires award/date/polygon validation and checking shared successors before attributing to areas.'};Path('work/social_round6_preliminary.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8');print({k:v for k,v in out.items()if k!='records'})
