"""Mass harmonisation at packaging; source files remain unchanged."""
import unicodedata
from collections import Counter

def fold(s):
 return ''.join(c for c in unicodedata.normalize('NFD',str(s).strip().lower()) if unicodedata.category(c)!='Mn')
def factor(sub,unit):
 if fold(sub) not in {'areia','minerio de manganes','manganes'}: return None
 u=fold(unit)
 if u in {'kg','quilograma','quilogramas','quilogramo','quilogramos'}: return .001
 if u in {'t','ton','tonelada','toneladas'}: return 1
 return None

def normalize(d):
 audit=[]
 for process,rows in d['enrichment']['production'].items():
  for i,r in enumerate(rows):
   f=factor(r[1],r[2])
   if f is None: continue
   original={'quantity':r[5],'unit':r[2]}
   r[2]='t';r[5]*=f
   audit.append({'process':process,'month':r[0],'substance':r[1],'source':'production','row':i,**original,'tonnes':r[5]})
 def visit(obj,path=''):
  if isinstance(obj,dict):
   if all(k in obj for k in ['substance','unit','quantity']):
    f=factor(obj['substance'],obj['unit'])
    if f is not None:
     q=obj['quantity'];n=float(q.replace('.','').replace(',','.')) if isinstance(q,str) and ',' in q else float(q)
     obj['original_quantity']=q;obj['original_unit']=obj['unit'];obj['quantity']=n*f;obj['unit']='t'
   for k,v in list(obj.items()):visit(v,path+'/'+k)
  elif isinstance(obj,list):
   for v in obj:visit(v,path)
 visit(d['guideEvidence']);visit(d['socialRound6'])
 d['massNormalization']={'rule':'Areia e minério de manganês: kg ÷ 1.000 = t; toneladas preservadas. m³ não convertido. Valores da CFEM inalterados. Fontes originais preservadas.','records':audit,'counts':dict(Counter('kg_to_t' if factor(a['substance'],a['unit'])==.001 else 't_label' for a in audit))}
 return d
