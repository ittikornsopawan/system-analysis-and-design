#!/usr/bin/env python3
"""Render semantic views with actual native parent/child containment, plus temporal sequences."""
from __future__ import annotations
import argparse,math,re,textwrap
import xml.etree.ElementTree as ET
import generate_diagrams as g
from generate_supporting_diagrams import add_cell
from diagram_paths import artifact_path


def all_views():
 from layered_core_content import CORE
 from layered_operations_content import OPS
 from layered_lifecycle_content import LIFECYCLES
 return CORE+LIFECYCLES+OPS


def bounds(n):return tuple(n[k] for k in ('x','y','w','h'))

def ancestors(key,items):
 result=[];p=items[key].get('parent')
 while p:
  assert p not in result,'containment cycle';result.append(p);p=items[p].get('parent')
 return result


def rows(n):
 size=9 if n.get('mono') else 11
 output=[]
 for value,role in n.get('rows',[]):
  size=9 if role=='mono' else 11
  cap=max(8,math.floor((n['w']-24)/(size*(.60 if role=='mono' else .55))))
  for line in textwrap.wrap(value,width=cap,break_long_words=False,break_on_hyphens=False):output.append((line,role))
 return output


def verify(d):
 containers=d.get('containers',[]);items={n['id']:n for n in containers+d['nodes']};assert len(items)==len(containers)+len(d['nodes'])
 for n in containers+d['nodes']:
  x,y,w,h=bounds(n);assert all(v%4==0 for v in (x,y,w,h)),(d['slug'],n['id'],'grid')
  assert x>=24 and y>=144 and x+w<=1560 and y+h<=1016,(d['slug'],n['id'],'frame')
  if n.get('parent'):
   p=items[n['parent']];assert p in containers
   assert x>=p['x']+12 and y>=p['y']+36 and x+w<=p['x']+p['w']-12 and y+h<=p['y']+p['h']-8,(d['slug'],n['id'],'containment')
  ancestors(n['id'],items)
 for i,n in enumerate(d['nodes']):
  for m in d['nodes'][i+1:]:assert not g.overlap(bounds(n),bounds(m)),(d['slug'],'leaf overlap',n['id'],m['id'])
  if n.get('shape') in ['decision','terminator']:continue
  for value,role in rows(n):assert len(value)*(9*.60 if role=='mono' else 11*.55)<=n['w']-20,(d['slug'],n['id'],'long token',value)
  start=36 if n.get('compact') else 54
  assert start+max(0,len(rows(n))-1)*14+3<=n['h']-2,(d['slug'],n['id'],'text height',len(rows(n)),n['h'])
  assert len(n['title'])*12*.53<=n['w']-24,(d['slug'],n['id'],'long title',n['title'])
 segments=[];ports={};masks=[]
 for e in d['edges']:
  pts=e['points'];g.rounded_path(pts)
  for key,p,q in [(e['source'],pts[0],pts[1]),(e['target'],pts[-1],pts[-2])]:
   if key is None:continue
   n=items[key];x,y,w,h=bounds(n)
   assert ((p[0] in (x,x+w) and y+6<=p[1]<=y+h-6 and p[1]==q[1]) or (p[1] in (y,y+h) and x+6<=p[0]<=x+w-6 and p[0]==q[0])),(d['slug'],key,'port',p)
   assert (key,p) not in ports,(d['slug'],key,'shared port');ports[(key,p)]=True
  if e.get('label'):
   assert len(e['label'][2])<=14 and e['label'][2].upper()==e['label'][2]
   b=g.label_box(e['label']);assert not any(g.overlap(b,bounds(n)) for n in d['nodes']),(d['slug'],'label over leaf',e['label']);masks.append(b)
   x,y,w,h=b;gaps=[]
   for p,q in zip(pts,pts[1:]):
    if p[1]==q[1] and max(x,min(p[0],q[0]))<min(x+w,max(p[0],q[0])):gaps.append(max(y-p[1],p[1]-y-h,0))
    if p[0]==q[0] and max(y,min(p[1],q[1]))<min(y+h,max(p[1],q[1])):gaps.append(max(x-p[0],p[0]-x-w,0))
   assert gaps and 6<=min(gaps)<=10,(d['slug'],'label gap',e['label'],gaps)
  exempt={e['source'],e['target']}
  for n in d['nodes']:
   if any(a in exempt for a in ancestors(n['id'],items)):exempt.add(n['id'])
  for p,q in zip(pts,pts[1:]):
   assert (p[0]==q[0])!=(p[1]==q[1]),(d['slug'],'diagonal')
   for n in d['nodes']:
    assert n['id'] in exempt or not g.segment_hits_box(p,q,bounds(n)),(d['slug'],'transit',n['id'])
   for a,b in segments:
    if p[1]==q[1] and a[1]==b[1] and p[1]==a[1]:assert max(min(p[0],q[0]),min(a[0],b[0]))>=min(max(p[0],q[0]),max(a[0],b[0])),(d['slug'],'stacked horizontal')
    if p[0]==q[0] and a[0]==b[0] and p[0]==a[0]:assert max(min(p[1],q[1]),min(a[1],b[1]))>=min(max(p[1],q[1]),max(a[1],b[1])),(d['slug'],'stacked vertical')
    cross=(p[1]==q[1] and a[0]==b[0] and min(p[0],q[0])<a[0]<max(p[0],q[0]) and min(a[1],b[1])<p[1]<max(a[1],b[1])) or (p[0]==q[0] and a[1]==b[1] and min(p[1],q[1])<a[1]<max(p[1],q[1]) and min(a[0],b[0])<p[0]<max(a[0],b[0]))
    assert not cross,(d['slug'],'crossing',p,q,a,b)
   segments.append((p,q))
 for b in masks:assert not any(g.segment_hits_box(p,q,b) for p,q in segments),(d['slug'],'connector through mask')
 print(f'PASS {d["slug"]}: {d["type"]}; {len(containers)} native containers / {len(d["nodes"])} child responsibilities; containment, text and routes')


def native_plain(root,key,text,x,y,w,h,size=11,font=g.SANS,color=g.MUTED,weight=400,parent='1',align='left'):
 return add_cell(root,key,text,x,y,w,h,f'text;html=0;spacing=0;align={align};verticalAlign=middle;fontSize={size};fontFamily={font};fontColor={color};'+('fontStyle=1;' if weight>=600 else ''),parent=parent)


def render(d):
 slug=d['slug'];containers=d.get('containers',[]);items={n['id']:n for n in containers+d['nodes']}
 mx=ET.Element('mxfile',host='app.diagrams.net',agent='Jinny',version='32.6.10',type='device');diagram=ET.SubElement(mx,'diagram',id=slug,name=d['title']);model=ET.SubElement(diagram,'mxGraphModel',dx='1584',dy='1120',grid='1',gridSize='4',page='1',pageScale='1',pageWidth='1584',pageHeight='1120',background=g.PAPER);root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1584 1120" role="img" aria-labelledby="{slug}-title {slug}-desc">',f'<title id="{slug}-title">{g.esc(d["title"])}</title>',f'<desc id="{slug}-desc">{g.esc(d["desc"])}</desc>','<defs>']
 for name,color in [('arrow',g.MUTED),('accent',g.ACCENT),('link',g.LINK)]:svg.append(f'<marker id="{slug}-{name}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="{color}"/></marker>')
 svg.extend(['</defs>',f'<rect width="1584" height="1120" fill="{g.PAPER}"/>'])
 for n in sorted(containers,key=lambda n:len(ancestors(n['id'],items))):
  x,y,w,h=bounds(n);kind=n.get('kind');focal=kind=='focal';color=g.ACCENT if focal else g.INK if kind in ['state','collection','project'] else g.SOFT;fill='#f1e7e4' if focal else '#f0f0f1' if kind in ['system','lane','policy'] else g.PAPER
  rx=8 if kind in ['state','focal'] else 4
  svg.append(f'<g data-container-id="{n["id"]}" data-parent="{n.get("parent") or "root"}"><rect data-role="container-bounds" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{color}" stroke-width="1"/>')
  svg.append(f'<line x1="{x}" y1="{y+36}" x2="{x+w}" y2="{y+36}" stroke="#bfc0c0" stroke-width="0.8"/>')
  svg.append(g.text_svg(x+12,y+16,n['title'],12,g.SANS,color,600));svg.append(g.text_svg(x+12,y+29,n.get('tag',''),8,g.MONO,g.SOFT));svg.append('</g>')
  parent=n.get('parent') or '1';px,py=(items[parent]['x'],items[parent]['y']) if parent!='1' else (0,0)
  label=f'<div style="text-align:left;font-family:{g.SANS};font-size:12px;font-weight:600;line-height:14px;">{g.esc(n["title"])}</div><div style="text-align:left;font-family:{g.MONO};font-size:8px;font-weight:400;line-height:12px;color:{g.SOFT};">{g.esc(n.get("tag",""))}</div>'
  add_cell(root,n['id'],label,x-px,y-py,w,h,f'swimlane;html=1;startSize=36;horizontal=1;container=1;collapsible=0;recursiveResize=0;rounded=1;absoluteArcSize=1;arcSize={rx*2};align=left;verticalAlign=top;spacingLeft=12;spacingTop=3;fillColor={fill};swimlaneFillColor={fill};strokeColor={color};fontColor={color};',parent=parent)
 for i,e in enumerate(d['edges']):
  color=g.COLORS.get(e.get('color'),g.MUTED);ref=e.get('kind')=='reference';marker='' if ref else f' marker-end="url(#{slug}-{"accent" if e.get("color")=="accent" else "link" if e.get("color")=="link" else "arrow"})"'
  svg.append(f'<path d="{g.rounded_path(e["points"])}" fill="none" stroke="{color}" stroke-width="1.2"'+(' stroke-dasharray="5,4"' if e.get('dashed') else '')+marker+'/>')
  style=f'edgeStyle=none;rounded=1;arcSize=8;html=0;endArrow={"none" if ref else "block"};endFill=1;strokeColor={color};strokeWidth=1.2;'+('dashed=1;dashPattern=5 4;' if e.get('dashed') else '')
  for prefix,key,p in [('exit',e['source'],e['points'][0]),('entry',e['target'],e['points'][-1])]:
   if key:
    n=items[key];style+=f'{prefix}X={(p[0]-n["x"])/n["w"]:g};{prefix}Y={(p[1]-n["y"])/n["h"]:g};{prefix}Dx=0;{prefix}Dy=0;'
  c=add_cell(root,f'edge-{i}','',0,0,0,0,style,edge=True,points=e['points'])
  if e['source']:c.set('source',e['source'])
  c.set('target',e['target'])
  if e.get('label'):
   x,y,w,h=g.label_box(e['label']);svg.append(f'<rect x="{x:g}" y="{y:g}" width="{w}" height="{h}" rx="2" fill="{g.PAPER}"/>');svg.append(g.text_svg(e['label'][0],e['label'][1]+5,e['label'][2],8,g.MONO,g.SOFT,anchor='middle'));native_plain(root,f'edge-label-{i}',e['label'][2],x,y,w,h,8,g.MONO,g.SOFT,align='center')
 if d.get('start'):
  x,y=d['start'];svg.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{g.INK}"/>');add_cell(root,'initial','',x-6,y-6,12,12,f'ellipse;fillColor={g.INK};strokeColor=none;')
 for n in d['nodes']:
  x,y,w,h=bounds(n);kind=n.get('kind','backend');fill,stroke=g.treatment(kind) if kind in ['backend','focal','store','input','folder','state','terminal','optional'] else ('#ffffff',g.INK);shape=n.get('shape');parent=n.get('parent') or '1';px,py=(items[parent]['x'],items[parent]['y']) if parent!='1' else (0,0)
  svg.append(f'<g data-node-id="{n["id"]}" data-parent="{parent}">')
  if shape=='decision':
   svg.append(f'<polygon points="{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}" fill="{fill}" stroke="{stroke}"/>');svg.append(g.text_svg(x+w/2,y+h/2-5,n['title'],11,g.SANS,g.INK,600,'middle'));condition=' / '.join(value for value,role in n.get('rows',[]));svg.append(g.text_svg(x+w/2,y+h/2+13,condition,9,g.SANS,g.MUTED,anchor='middle'));style='rhombus;'
   label=g.esc(n['title'])+'<br><span style="font-size:9px;">'+g.esc(condition)+'</span>'
  elif shape=='terminator':
   svg.append(f'<rect data-role="node-bounds" x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{fill}" stroke="{stroke}"/>');svg.append(g.text_svg(x+w/2,y+h/2+4,n['title'],12,g.SANS,g.INK,600,'middle'));style=f'rounded=1;arcSize=50;';label=g.esc(n['title'])
  else:
   svg.append(f'<rect data-role="node-bounds" x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1"'+(' stroke-dasharray="5,4"' if kind=='optional' else '')+'/>');svg.append(g.text_svg(x+12,y+22,n['title'],12,g.SANS,g.INK,600))
   compact=n.get('compact');start=36 if compact else 54
   label=f'<div style="position:relative;box-sizing:border-box;width:{w}px;height:{h}px;text-align:left;">'+f'<div style="position:absolute;left:12px;top:8px;font-size:12px;font-family:{g.SANS};font-weight:600;line-height:18px;white-space:nowrap;">{g.esc(n["title"])}</div>'
   if not compact:
    svg.append(g.text_svg(x+12,y+38,n.get('tag',''),8,g.MONO,g.SOFT));label+=f'<div style="position:absolute;left:12px;top:29px;font-size:8px;font-family:{g.MONO};line-height:12px;white-space:nowrap;color:{g.SOFT};">{g.esc(n.get("tag",""))}</div>'
   for i,(value,role) in enumerate(rows(n)):
    size,font=(9,g.MONO) if role=='mono' else (11,g.SANS);svg.append(g.text_svg(x+12,y+start+i*14,value,size,font,g.MUTED));label+=f'<div style="position:absolute;left:12px;top:{start+i*14-11}px;font-size:{size}px;font-family:{font};line-height:14px;color:{g.MUTED};white-space:nowrap;">{g.esc(value)}</div>'
   label+='</div>';style='rounded=1;absoluteArcSize=1;arcSize=8;'
  svg.append('</g>');style+=f'html=1;whiteSpace=wrap;align={"center" if shape else "left"};verticalAlign={"middle" if shape else "top"};spacing=0;overflow=hidden;fillColor={fill};strokeColor={stroke};fontSize=12;fontFamily={g.SANS};'+('dashed=1;dashPattern=5 4;' if kind=='optional' else '')
  add_cell(root,n['id'],label,x-px,y-py,w,h,style,parent=parent)
 for i,(x,y,value,size,role) in enumerate(d.get('notes',[])):
  svg.append(g.text_svg(x,y,value,size,g.MONO if role=='mono' else g.SANS,g.MUTED,600 if role=='heading' else 400));native_plain(root,f'note-{i}',value,x,y-size-1,max(40,len(value)*size*.65+8),size+6,size,g.MONO if role=='mono' else g.SANS,g.MUTED,600 if role=='heading' else 400)
 for i,(x,y,value) in enumerate(d.get('cardinality',[])):
  svg.append(g.text_svg(x,y,value,8,g.MONO,g.MUTED));native_plain(root,f'cardinality-{i}',value,x-8,y-10,32,14,8,g.MONO,g.MUTED)
 for key,x,y,text,size,font,color,weight in [('eyebrow',40,48,d['eyebrow'],8,g.MONO,g.SOFT,500),('title',40,88,d['title'],32,g.SERIF,g.INK,400),('subtitle',40,116,d['subtitle'],12,g.SANS,g.MUTED,400),('source',40,1036,d['source'],9,g.MONO,g.SOFT,400)]:
  svg.append(g.text_svg(x,y,text,size,font,color,weight));native_plain(root,'page-'+key,text,x,y-size-2,1504,size+8,size,font,color,weight)
 svg.append('<line x1="40" y1="1052" x2="1544" y2="1052" stroke="#bfc0c0"/>');add_cell(root,'legend-line','',40,1052,1504,1,'shape=line;strokeColor=#bfc0c0;')
 legends=d.get('legend',[]);step=1504/max(1,len(legends))
 for i,(kind,text) in enumerate(legends):
  x=40+i*step;svg.append(g.text_svg(x,1076,text,9,g.SANS,g.MUTED));native_plain(root,f'legend-{i}',text,x,1063,step-8,20,9,g.SANS,g.MUTED)
 svg.append('</svg>');svg='\n'.join(svg);template=dict(d,pattern=None,nodes=[],edges=[],zones=[],notes=[],legend=[]);html=g.make_html(template).replace(g.svg(template),svg)
 ids=[c.get('id') for c in root.findall('mxCell')];assert len(ids)==len(set(ids)),(slug,'duplicate native cell ID')
 ET.indent(mx,space='  ')
 return html,ET.tostring(mx,encoding='unicode',xml_declaration=True)+'\n'


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--finalize-pngs',action='store_true');ap.add_argument('--only',nargs='*');args=ap.parse_args()
 for d in all_views():
  if args.only and d['slug'] not in args.only:continue
  verify(d);html,xml=render(d)
  if args.finalize_pngs:g.finalise_png(d)
  elif args.check:assert artifact_path(d["slug"],".html").read_text()==html and artifact_path(d["slug"],".drawio").read_text()==xml,d['slug']+' source drift'
  else:artifact_path(d["slug"],".html").write_text(html);artifact_path(d["slug"],".drawio").write_text(xml)
 from layered_sequence_content import sequence_sources,SEQUENCES
 for d in SEQUENCES:
  if args.only and d['slug'] not in args.only:continue
  html,xml=sequence_sources(d)
  if args.finalize_pngs:g.finalise_png(d)
  elif args.check:assert artifact_path(d["slug"],".html").read_text()==html and artifact_path(d["slug"],".drawio").read_text()==xml
  else:artifact_path(d["slug"],".html").write_text(html);artifact_path(d["slug"],".drawio").write_text(xml)
 print('PASS semantic hierarchy package: source and native containment checks')

if __name__=='__main__':main()
