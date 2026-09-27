import json,re,math
from pathlib import Path
from normalize_mass_units import factor
s=Path('outputs/Observatorio_Leiloes_Minerais.html').read_text(encoding='utf-8');d=json.loads(re.search(r'<script id="data"[^>]*>(.*?)</script>',s,re.S).group(1));old=json.loads(Path('work/cfem_enrichment.json').read_text(encoding='utf-8'))
assert d['enrichment']['profiles']==old['profiles']
for p,rs in old['production'].items():
 for a,b in zip(rs,d['enrichment']['production'][p]):
  f=factor(a[1],a[2])
  if f is None:assert a==b
  else:assert b[2]=='t' and math.isclose(b[5],a[5]*f,rel_tol=1e-12)
assert d['areaScenario']['summary']['cfem_cents']==412312839
print(d['massNormalization']['counts']);print('PASS: all rows checked; CFEM unchanged; other units unchanged')
Path('work/mass_conversion_audit.json').write_text(json.dumps(d['massNormalization'],ensure_ascii=False,indent=2),encoding='utf-8')
