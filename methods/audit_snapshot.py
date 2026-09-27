"""Reproduz verificações aritméticas; não certifica documentos nem pagamentos."""
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal
import csv, hashlib, json, random, re

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / 'index.html').read_text(encoding='utf-8')
payload = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)[1]
d = json.loads(payload)
checks = []
def check(name, actual, expected):
    checks.append(dict(name=name, actual=actual, expected=expected, passed=actual == expected))
def cents(value):
    return int((Decimal(str(value))*100).quantize(Decimal('1')))
a = d['areaScenario']['areas']; s = d['areaScenario']['summary']
check('Ofertas arrematadas sem chave repetida', len({x['key'] for x in a}), len(a))
check('Total de arrematações', len(a), s['awarded'])
check('Soma dos lances em centavos', sum(x['cents'] for x in a), s['bid_cents'])
u = [x for x in a if x['unpaid']]
check('Áreas com não pagamento identificado',len(u),s['unpaid'])
check('Montante do não pagamento identificado',sum(x['cents'] for x in u),s['unpaid_cents'])
check('Saldo de áreas sem não pagamento identificado',len(a)-len(u),s['estimated_paid'])
check('CFEM atribuída às áreas comerciais',sum(x['cfem_cents'] for x in a),s['cfem_cents'])
check('Áreas comerciais com CFEM',sum(x['cfem_cents']>0 for x in a),s['cfem_areas'])
social = d['socialRound6']
check('CFEM social somada por área',sum(x['cfem_cents'] for x in social['records']),social['cfem_cents'])
check('Áreas sociais com CFEM',sum(x['cfem_cents']>0 for x in social['records']),social['cfem_origins'])
check('Processos originais únicos',len({x['origem'] for x in d['rows']}),len(d['rows']))
stopped = {'returned_unpaid','free_unpaid','paid_without_request'}
paired = [r for r in d['rows'] if d['businessOutcomes']['origins'].get(r['origem'],{}).get('state') not in stopped and r['antes'] and r['depois']]
matrix=Counter(('antes_e_depois' if r['antes']['positivo'] and r['depois']['positivo'] else 'somente_antes' if r['antes']['positivo'] else 'somente_depois' if r['depois']['positivo'] else 'nenhum') for r in paired)
check('Matriz comercial fecha o conjunto comparável',sum(matrix.values()),len(paired))
check('CFEM posterior da matriz e das áreas',sum(cents(r['depois']['reais']) for r in paired),s['cfem_cents'])
check('Contagem posterior da matriz e das áreas',sum(r['depois']['positivo'] for r in paired),s['cfem_areas'])
check('Rodadas sociais e canceladas sem lance comercial',sum(r['cents'] for r in d['auctionContext']['rounds'] if r['round'] in (6,7)),0)
matches=Counter(x.get('match') for x in u)
report={'scope':'Verificação computacional da versão congelada; não é auditoria independente nem conciliação bancária.',
 'cutoff':d['cutoff'],'snapshot_sha256':hashlib.sha256(payload.encode()).hexdigest(),'checks':checks,
 'matrix':dict(matrix),'comparable':len(paired),'before_cents':sum(cents(r['antes']['reais']) for r in paired),
 'after_cents':s['cfem_cents'],'social_cents':social['cfem_cents'],'total_cfem_cents':s['cfem_cents']+social['cfem_cents'],
 'payment_origin_status':d['paymentEvidence']['counts'],'nonpayment_match_types':dict(matches),
 'pending':['Conciliação financeira do saldo','Revisão documental independente de vínculos e alertas','Uniformização das janelas temporais','Teste com usuários e mensuração de tempo e acerto']}
(ROOT/'docs'/'quality_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
# Seleção reproduzível para revisão. Não é uma amostra probabilística de precisão global.
groups=defaultdict(list)
for r in d['rows']:
    state=d['businessOutcomes']['origins'].get(r['origem'],{}).get('state','unknown')
    groups[(max(x['rodada'] for x in r['arrematacoes']),state if state in stopped else r.get('transicao') or 'unknown')].append(r)
rng=random.Random(20260927)
fields=['origem','rodada','grupo','sucessores','vinculo_correto','classificacao_correta','cfem_atribuida_corretamente','fonte_documental','revisor','data_revisao','observacao']
with (ROOT/'docs'/'amostra_revisao.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for (rd,group),rows in sorted(groups.items()):
        for r in rng.sample(sorted(rows,key=lambda r:r['origem']),min(3,len(rows))):
            w.writerow(dict(origem=r['origem'],rodada=rd,grupo=group,sucessores='; '.join(r['sucessores_candidatos'])))
print(json.dumps(report,ensure_ascii=False,indent=2))
if not all(c['passed'] for c in checks):raise SystemExit('Divergência: revisar antes de publicar.')
