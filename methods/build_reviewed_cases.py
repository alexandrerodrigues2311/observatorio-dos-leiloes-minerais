import json,re
from pathlib import Path
A=json.loads(Path('work/audit_remaining13.json').read_text(encoding='utf-8'));events=json.loads(Path('work/remaining13_events_full.json').read_text(encoding='utf-8'));E=json.loads(Path('work/cfem_enrichment.json').read_text(encoding='utf-8'));out={}
for v in A:
 r=v['row'];p=r['origem'];issues=r['problemas_vinculo'];ps=[p];ps += [c['p'] for c in v['children']]
 for c in v['children']:
  if c['other_award']:ps+=c['other_award']['sucessores_candidatos']
 if 'sem_sucessor_tipo8_identificado' in issues:kind='missing_link';title='Sucessor não localizado';why='Não encontramos associação tipo 8 nem eventos posteriores à arrematação na extração consultada. Consultar o resultado individual da área e o processo SEI para localizar eventual novo número.'
 elif 'associacao_anterior_homologacao' in issues:kind='date_conflict';title='Continuidade encontrada; data da rodada a conferir';why='O novo processo foi aberto e associado em 13/09/2022, um dia antes do marco de homologação usado (14/09/2022). Há alvará posterior. O vínculo existe; falta conciliar o marco com o ato individual, sem deslocar a data por suposição.'
 elif 'origem_com_multiplas_arrematacoes' in issues:kind='multiple_cycles';title='Duas arrematações e dois sucessores';why='Há ciclos em 2021 e 2024. A comparação precisa separar as janelas de cada rodada; não se trata de ausência de processo.'
 else:
  stopped=[c for c in v['children'] if any(e[1]in ['2463','2464','2471','2472','2473'] for e in c['events'])]
  kind='returned_chain' if stopped else 'reauction_chain';title='Retorno documentado na cadeia' if stopped else 'Nova arrematação do processo associado';why='O associado participou de nova rodada. A cadeia está identificada; a CFEM de diferentes ciclos não é somada à primeira origem para evitar atribuição duplicada.'
 if p=='864.381/2012':why='Sucessor864.218/2021: renúncia homologada em04/11/2022, nova arrematação em21/10/2024 e retorno por proposta paga sem requerimento em13/12/2024. O requerimento864.396/2024 não foi conhecido e foi arquivado em31/01/2025. Em17/02/2025 foi tornado sem efeito o arquivamento do864.218/2021. A fase cadastral persistida não substitui esses atos; conferir a situação atual no SEI.'
 ev=[]
 for q in dict.fromkeys(ps):
  for e in events.get(q,[]):
   if e['DTEvento']<r['data_referencia']:continue
   code=e['IDEvento'];ev.append({'process':q,'date':e['DTEvento'],'code':code,'name':E['eventNames'].get(code,code),'text':e['DSPublicacaoDOU']})
 out[p]={'kind':kind,'title':title,'explanation':why,'chain':list(dict.fromkeys(ps)),'events':sorted(ev,key=lambda x:(x['date'],x['process']))}
Path('work/reviewed_cases.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8');print({k:sum(v['kind']==k for v in out.values()) for k in set(v['kind'] for v in out.values())})
