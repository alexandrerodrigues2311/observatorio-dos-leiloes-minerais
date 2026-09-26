import json,zipfile,csv,io,re,collections,datetime
from pathlib import Path
E=json.loads(Path('work/cfem_enrichment.json').read_text(encoding='utf-8'));keys=set(E['phases']);out=collections.defaultdict(list)
with zipfile.ZipFile('work/scm.zip') as z:
 def rows(n):return csv.DictReader(io.TextIOWrapper(z.open('microdados-scm/'+n+'.txt'),encoding='cp1252'),delimiter=';')
 names={r['IDEvento']:r['DSEvento'] for r in rows('Evento')};codes={k:v for k,v in names.items() if 'GUIA' in v and 'UTILIZA' in v}
 for r in rows('ProcessoEvento'):
  p=r['DSProcesso'];c=r['IDEvento'];dt=r['DTEvento'][:10]
  if p not in keys or c not in codes:continue
  name=codes[c];txt=r.get('DSPublicacaoDOU','');auth='AUTORIZADA PUBL' in name;extension='PRORROGA' in name and 'PUBL' in name
  years=re.search(r'0?([123]) ANO',name);years=int(years[1]) if years else None
  if not years:
   m=re.search(r'prazo\s+(?:de\s+)?([123])\s+anos?',txt,re.I);years=int(m[1]) if m else None
  number=re.search(r'Guia\s*n[ºo°.]?\s*([\d./-]+)',txt,re.I)
  end=None
  if auth and years:
   d=datetime.date.fromisoformat(dt);end=d.replace(year=d.year+years).isoformat()
  out[p].append({'date':dt,'code':c,'name':name,'text':txt,'observation':r.get('OBEvento',''),'authorization':auth,'extension':extension,'years':years,'estimatedEnd':end,'number':number[1] if number else None,'interruption':('CANCELADA' in name or 'SUSPENSA' in name)})
result={'source':'microdados-scm/ProcessoEvento.txt + Evento.txt; extração SCM disponível neste projeto','cutoff':'2026-06-30','codes':codes,'processes':{p:sorted(v,key=lambda x:x['date']) for p,v in out.items()}}
Path('work/guide_evidence.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'processes_scanned':len(keys),'processes_with_guide_events':len(out),'events':sum(map(len,out.values())),'authorization_codes':[c for c,n in codes.items() if 'AUTORIZADA PUBL' in n]},ensure_ascii=False))
