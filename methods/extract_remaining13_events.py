import json,csv,io,zipfile,collections
from pathlib import Path
A=json.loads(Path('work/audit_remaining13.json').read_text(encoding='utf-8'));keys=set()
for v in A:
 keys.add(v['row']['origem'])
 for c in v['children']:
  keys.add(c['p'])
  if c['other_award']:keys.update(c['other_award']['sucessores_candidatos'])
out=collections.defaultdict(list)
with zipfile.ZipFile('work/scm.zip') as z:
 for r in csv.DictReader(io.TextIOWrapper(z.open('microdados-scm/ProcessoEvento.txt'),encoding='cp1252'),delimiter=';'):
  if r['DSProcesso'] in keys and r['DTEvento']<='2026-06-30':out[r['DSProcesso']].append(r)
Path('work/remaining13_events_full.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8');print('processes',len(out))
