import json, hashlib, re, pathlib, sys, csv
from openpyxl import load_workbook
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
ROOT=pathlib.Path(__file__).parent

def readbook(p):
 out={}
 for s in load_workbook(p,data_only=True):
  rows=list(s.values)
  if not rows: continue
  out[s.title]=[dict(zip(map(str,rows[0]),r))|{'source':f'{p.name}::{s.title}!{i}', 'status':'source_draft'} for i,r in enumerate(rows[1:],2) if any(x is not None for x in r)]
 return out

def main(folder):
 g=readbook(folder/'PID_core_elements_glossary.xlsx'); d=readbook(folder/'PID_gasifier_mode_lists.xlsx')
 for sheet, rows in g.items():
  for i,r in enumerate(rows): r['symbol_id']=hashlib.sha256((sheet+str(list(r.values())[:2])).encode()).hexdigest()[:16]
 for key,rows in d.items():
  for r in rows:r['status']='candidate_unapproved'
 manifest=[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in folder.iterdir() if p.is_file() and p.suffix in ('.xlsx','.pdf','.html','.md','.csv','.docx','.pptx','.zip')]
 for name,obj in [('glossary',g),('plant',d),('manifest',manifest)]: (ROOT/'data'/f'{name}.json').write_text(json.dumps(obj,default=str,indent=2))
 x=[];y=[]
 for sheet in ['Equipment','Instrument index','Valve list']:
  for r in d[sheet]:
   x.append(' '.join(str(r.get(k,'')) for k in ['name','description','type','function'])); y.append(sheet)
 m=make_pipeline(TfidfVectorizer(analyzer='char',ngram_range=(2,4)),LogisticRegression(max_iter=1000));m.fit(x,y);joblib.dump(m,ROOT/'models/classifier.joblib')
 print({k:len(v) for k,v in g.items()}); print({k:len(v) for k,v in d.items()}); print('training rows',len(x))
if __name__=='__main__':main(pathlib.Path(sys.argv[1]))
