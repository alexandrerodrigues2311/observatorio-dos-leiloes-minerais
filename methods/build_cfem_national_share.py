import csv,json,collections,decimal
from pathlib import Path
monthly=collections.Counter();rows=collections.Counter()
for name in ['CFEM_Arrecadacao_2017_2021.csv','CFEM_Arrecadacao_2022_2026.csv']:
 with (Path('work')/name).open(encoding='cp1252',newline='') as f:
  for r in csv.DictReader(f):
   m=f"{int(r['Ano']):04}-{int(r['Mês']):02}"
   if '2021-01'<=m<='2026-06':monthly[m]+=int(decimal.Decimal(r['ValorRecolhido'].replace('.','').replace(',','.'))*100);rows[m]+=1
assert len(monthly)==66
out={'start':'2021-01','end':'2026-06','monthlyCents':dict(sorted(monthly.items())),'totalCents':sum(monthly.values()),'sources':['CFEM_Arrecadacao_2017_2021.csv','CFEM_Arrecadacao_2022_2026.csv'],'method':'Soma de ValorRecolhido em todos os registros nacionais, incluindo ajustes, sem filtrar processos, substâncias ou UF. Mesma base e tratamento de registros do numerador.'}
Path('work/cfem_national_share.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8');print(out['totalCents']/100)
