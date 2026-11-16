"""Draft graph renderer: no inferred valve placement or safety decisions."""
import json, html, math, re
from pathlib import Path
import networkx as nx
ROOT=Path(__file__).parent

def load(name): return json.loads((ROOT/'data'/f'{name}.json').read_text())

def validate(p):
 issues=[]; tags=[r['tag'] for r in p['Equipment']]; lines=[r['line_no'] for r in p['Line list']]
 for group,key in [('Equipment','tag'),('Line list','line_no'),('Instrument index','tag'),('Valve list','tag')]:
  ids=[r[key] for r in p.get(group,[])];
  if len(ids)!=len(set(ids)): issues.append('Duplicate IDs in '+group)
  for r in p.get(group,[]):
   if not r.get('source'): issues.append('Missing source: '+r[key])
 for r in p['Line list']:
  if r['from'] not in tags or r['to'] not in tags: issues.append('Unresolved endpoint: '+r['line_no'])
 for group,key in [('Instrument index','attached_to'),('Valve list','line')]:
  for r in p.get(group,[]):
   if r.get(key) not in tags+lines: issues.append('Unresolved association: '+r['tag'])
 return issues

def graph(p):
 g=nx.MultiDiGraph();g.add_nodes_from(r['tag'] for r in p['Equipment']);
 for r in p['Line list']:g.add_edge(r['from'],r['to'],key=r['line_no'])
 return g

# Original schematic glyphs, not certified standard reproductions. Shared by renderer and training.
GLYPHS={'hopper':'<path d="M10 10H90V40L60 80H40L10 40Z"/>','vessel':'<rect x="25" y="5" width="50" height="90" rx="23"/>','screw':'<rect x="5" y="30" width="90" height="40"/><path d="M10 50L25 35 40 65 55 35 70 65 90 50"/>','exchanger':'<circle cx="50" cy="50" r="38"/><path d="M12 50L35 30 65 70 88 50"/>','cyclone':'<path d="M15 10H85V45L55 90H45L15 45Z M0 25H15 M50 0V10"/>','package':'<rect x="5" y="15" width="90" height="70" stroke-dasharray="5 3"/>','instrument':'<circle cx="50" cy="50" r="35"/>','valve':'<path d="M10 25L90 75V25L10 75Z"/>','check':'<path d="M15 25L75 50 15 75Z M75 20V80"/>','ball':'<path d="M10 25L90 75V25L10 75Z"/><circle cx="50" cy="50" r="13"/>','control':'<path d="M10 40L90 90V40L10 90Z M50 65V25 M25 25Q50 -10 75 25Z"/>','pump':'<circle cx="50" cy="50" r="35"/><path d="M40 30L70 50 40 70Z M50 15H95"/>','unknown':'<rect x="10" y="10" width="80" height="80" stroke-dasharray="2 4"/>'}

def glyph(kind):return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><g fill="white" stroke="black" stroke-width="3">'+GLYPHS[kind]+'</g></svg>'
def kind(r):
 t=r.get('type','').lower();return {'hopper':'hopper','screw_heated':'screw','auger_reactor':'screw','heat_exchanger':'exchanger','solids_cooler':'exchanger','gasifier':'vessel','electric_heater_vessel':'vessel','package':'package','solids_separator':'unknown'}.get(t,'unknown')
def render(p):
 g=graph(p); pos={n:(150+(i%4)*420,150+(i//4)*270) for i,n in enumerate(g)}; h=300+math.ceil(len(g)/4)*270; e=lambda s:html.escape(str(s)); out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1800 {h}" font-family="Arial"><rect width="1800" height="{h}" fill="white"/><defs><marker id="a" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z"/></marker></defs><text x="30" y="35" font-size="24">SMART P&amp;ID — DRAFT CONNECTIVITY REVIEW</text><text x="30" y="65">Proposed glyphs; routing not engineered. Valve order, nozzle sizes and control connections unresolved.</text>']
 for i,(u,v,k) in enumerate(g.edges(keys=True)):
  x,y=pos[u];a,b=pos[v]; yy=y+85+(i%5)*12;out.append(f'<g><title>{e(k)}</title><path d="M{x+50} {y+35} V{yy} H{a-65-(i%4)*12} V{b+35} H{a-50}" fill="none" stroke="#657487" marker-end="url(#a)"/><text x="{(x+a)/2}" y="{yy-3}" font-size="11">{e(k)}</text></g>')
 for r in p['Equipment']:
  x,y=pos[r['tag']];out.append(f'<g><title>{e(r.get("source","TBD"))}</title><g transform="translate({x-50},{y-15})" fill="white" stroke="black" stroke-width="2">{GLYPHS[kind(r)]}</g><text x="{x-50}" y="{y-24}" font-weight="bold">{e(r["tag"])}</text><text x="{x-50}" y="{y+105}" font-size="13">{e(r["name"])}</text></g>')
 out.append('</svg>');return ''.join(out)

def dxf(p):
 import ezdxf,io
 doc=ezdxf.new(); m=doc.modelspace();g=graph(p);pos={n:((i%4)*150,-(i//4)*100) for i,n in enumerate(g)}
 for n,(x,y) in pos.items():m.add_lwpolyline([(x-20,y-15),(x+20,y-15),(x+20,y+15),(x-20,y+15)],close=True);m.add_text(n,dxfattribs={'height':3,'insert':(x-15,y)})
 for u,v,k in g.edges(keys=True):m.add_line(pos[u],pos[v]);x,y=pos[u];a,b=pos[v];m.add_text(k,dxfattribs={'height':2,'insert':((x+a)/2,(y+b)/2)})
 m.add_text('DRAFT CONNECTIVITY ONLY - NOT FOR CONSTRUCTION',dxfattribs={'height':5,'insert':(0,35)});f=io.StringIO();doc.write(f);return f.getvalue()
