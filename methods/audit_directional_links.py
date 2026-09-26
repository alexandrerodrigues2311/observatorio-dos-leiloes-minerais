import csv,io,zipfile,json,re,collections
from pathlib import Path
d=json.loads(re.search(r'<script id="data"[^>]*>(.*?)</script>',Path('outputs/Observatorio_Leiloes_Minerais.html').read_text(encoding='utf-8'),re.S)[1]);keys={r['origem'] for r in d['rows']};before=collections.defaultdict(list);after=collections.defaultdict(list)
with zipfile.ZipFile('work/scm.zip') as z:
 for r in csv.DictReader(io.TextIOWrapper(z.open('microdados-scm/ProcessoAssociacao.txt'),encoding='cp1252'),delimiter=';'):
  if r['IDTipoAssociacao']!='8':continue
  a,b=r['DSProcesso'],r['DSProcessoAssociado']
  if b in keys:before[b].append({'process':a,'date':r['DTAssociacao']})
  if a in keys:after[a].append({'process':b,'date':r['DTAssociacao']})
Path('work/directional_links.json').write_text(json.dumps({'predecessors':before,'successors':after},ensure_ascii=False),encoding='utf-8');print('origins with predecessor',len(before),'with successor',len(after))
