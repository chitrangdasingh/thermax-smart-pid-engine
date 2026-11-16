import streamlit as st, json, io, joblib
import networkx as nx
from PIL import Image
import numpy as np
from engine import ROOT,load,validate,graph,render,dxf,GLYPHS,glyph
st.set_page_config(page_title='Smart P&ID',layout='wide')
st.title('Smart P&ID | Engineering workspace');st.warning('Draft engineering review only — not for construction or safety decisions.')
p=load('plant'); up=st.sidebar.file_uploader('New plant: normalized register JSON',type='json')
if up:
 try:
  p=json.load(up); validate(p);graph(p)
 except Exception as e: st.error(str(e));st.stop()
page=st.sidebar.radio('Workspace',['Drawing & connectivity','Registers & QA','Glossary','Aspen reference','ML laboratory','Sources'])
if page=='Drawing & connectivity':
 g=graph(p);a=st.selectbox('Asset',list(g));st.write('Downstream (draft paths):',sorted(nx.descendants(g,a)));st.dataframe([r for r in p['Line list'] if a in (r['from'],r['to'])]);st.dataframe([r for r in p['Instrument index'] if r['attached_to']==a]);s=render(p);st.image(s);st.download_button('SVG drawing',s,'review.svg','image/svg+xml');st.download_button('DXF connectivity sketch',dxf(p),'review.dxf')
elif page=='Registers & QA':
 st.write('Validation findings',validate(p) or ['No structural issues detected; engineering approval still pending']);k=st.selectbox('Register',list(p));st.dataframe(p[k]);st.download_button('Export plant JSON',json.dumps(p,indent=2),'plant.json')
elif page=='Glossary':
 g=load('glossary');k=st.selectbox('Category',list(g));st.dataframe(g[k]);st.download_button('Master glossary',json.dumps(g,indent=2),'glossary.json');st.caption('Original draft glyphs, not verified standards symbols.'); cols=st.columns(4)
 for i,k in enumerate(GLYPHS):
  with cols[i%4]:st.image(glyph(k),width=95);st.caption(k)
elif page=='Aspen reference':
 st.dataframe(load('aspen_mapping')); 
 for f in (ROOT/'data').glob('*.png'):st.image(str(f))
elif page=='ML laboratory':
 m=joblib.load(ROOT/'models/classifier.joblib');t=st.text_input('Description','Control valve');st.write('Candidate text class:',m.predict([t])[0]);st.json(load('visual_report'));u=st.file_uploader('Isolated symbol crop',type=['png','jpg','jpeg']);
 if u:
  im=Image.open(u).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);X=np.asarray(bg.convert('L').resize((24,24))).reshape(1,-1);st.write('Candidate synthetic glyph class:',joblib.load(ROOT/'models/visual.joblib').predict(X)[0])
 st.caption('Models are draft classifiers, not PFD object detectors. Synthetic evaluation is not cross-plant validation.')
else:st.dataframe(load('manifest'));st.dataframe(load('aspen_mapping'))
