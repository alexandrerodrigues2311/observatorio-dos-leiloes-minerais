import json,re,datetime
from pathlib import Path
p=Path('work/guide_evidence.json');d=json.loads(p.read_text(encoding='utf-8'))
for records in d['processes'].values():
 for g in records:
  text=g['text'];m=re.search(r'Validade\s*:\s*(\d{2})/(\d{2})/(\d{4})',text,re.I)
  if m:
   try:g['explicitEnd']=datetime.date(int(m[3]),int(m[2]),int(m[1])).isoformat()
   except ValueError:pass
  g['limits']=[]
  m=re.search(r'Substância\(s\):\s*(.*?)\s*-\s*Volume\(s\):\s*(.*)',text,re.I)
  if m and not re.search(r'[;,/]',m[1]):
   q=re.fullmatch(r'\s*([\d.,]+)\s*(toneladas?|ton|t|m³|m3)\s*(/\s*ano|por\s+ano)?\s*\.?\s*',m[2],re.I)
   if q:
    g['limits']=[{'substance':m[1].strip(),'quantity':float(q[1].replace('.','').replace(',','.')),'unit':'t' if q[2].lower().startswith('t') else 'm3','period':'annual' if q[3] else 'unspecified'}]
p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8');print('Explicit ends',sum('explicitEnd'in g for r in d['processes'].values() for g in r),'parsed limits',sum(bool(g['limits'])for r in d['processes'].values() for g in r))
