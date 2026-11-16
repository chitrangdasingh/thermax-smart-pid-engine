"""Train a synthetic single-symbol classifier; not a detector or real-drawing validation."""
from engine import GLYPHS,glyph,ROOT
from PIL import Image
import cairosvg,io,random,numpy as np,joblib,json
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def generate(seed,n):
 rng=random.Random(seed);X=[];y=[]
 for k in GLYPHS:
  if k=='unknown':continue
  base=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=glyph(k).encode(),output_width=64,output_height=64))).convert('RGBA')
  for _ in range(n):
   im=base.rotate(rng.uniform(-12,12),resample=Image.Resampling.BICUBIC); bg=Image.new('RGBA',(80,80),'white');bg.alpha_composite(im,(rng.randint(0,16),rng.randint(0,16)));X.append(np.asarray(bg.convert('L').resize((24,24))).ravel());y.append(k)
 return X,y
if __name__=='__main__':
 X,y=generate(42,40);a,b=generate(99,12);m=RandomForestClassifier(n_estimators=60,random_state=42,n_jobs=2).fit(X,y);joblib.dump(m,ROOT/'models/visual.joblib');report={'train':len(y),'synthetic_test':len(b),'synthetic_accuracy':accuracy_score(b,m.predict(a)),'limitation':'Same glyph templates in both sets; not real drawing performance.'};(ROOT/'data/visual_report.json').write_text(json.dumps(report));print(report)
