#!/usr/bin/env python3
"""Generate/verify supporting HTML and native draw.io; finalize PNGs after native export."""
from __future__ import annotations
import argparse,copy,math,re
from pathlib import Path
import xml.etree.ElementTree as ET
import generate_diagrams as g
from supporting_content import SHEETS,SEQUENCES

from diagram_paths import DIAGRAM_ROOT
OUT=DIAGRAM_ROOT


def add_cell(root,key,value,x,y,w,h,style,parent='1',edge=False,points=None):
    c=ET.SubElement(root,'mxCell',id=key,value=value,style=style,parent=parent,**({'edge':'1'} if edge else {'vertex':'1'}))
    geo=ET.SubElement(c,'mxGeometry',attrib={'as':'geometry'})
    if edge:
        geo.set('relative','1');p=points
        ET.SubElement(geo,'mxPoint',x=f'{p[0][0]:g}',y=f'{p[0][1]:g}',attrib={'as':'sourcePoint'})
        ET.SubElement(geo,'mxPoint',x=f'{p[-1][0]:g}',y=f'{p[-1][1]:g}',attrib={'as':'targetPoint'})
        if len(p)>2:
            a=ET.SubElement(geo,'Array',attrib={'as':'points'})
            for px,py in p[1:-1]:ET.SubElement(a,'mxPoint',x=f'{px:g}',y=f'{py:g}')
    else:
        for k,v in dict(x=x,y=y,width=w,height=h).items():geo.set(k,f'{v:g}')
    return c


def sheet_sources(d):
    svg=g.svg(d);mx=ET.fromstring(g.make_drawio(d));root=mx.find('./diagram/mxGraphModel/root')
    if d['type']=='ER':
        svg=re.sub(r' marker-end="[^"]+"','',svg)
        for c in root.findall('mxCell'):
            if c.get('edge')=='1':c.set('style',re.sub(r'endArrow=[^;]+','endArrow=none',c.get('style','')))
    for i,(x,y,value) in enumerate(d.get('cardinality',[])):
        svg=svg.replace('</svg>',g.text_svg(x,y,value,8,g.MONO,g.MUTED)+'</svg>')
        add_cell(root,f'cardinality-{i}',value,x-12,y-10,24,12,f'text;html=0;align=center;spacing=0;fontSize=8;fontFamily={g.MONO};fontColor={g.MUTED};')
    for n in d['nodes']:
        if n['id'] not in d.get('artifacts',{}):continue
        name,version=d['artifacts'][n['id']];x,y,w,h=(n[k] for k in ('x','y','w','h'))
        artifact=f'{name} | {version}'
        assert len(artifact)*5.4<=w-40,(d['slug'],n['id'],'artifact length')
        extra=(f'<rect data-role="artifact" x="{x+16}" y="{y+h-40}" width="{w-32}" height="24" rx="4" fill="#e4e6e8" stroke="#bfc0c0"/>'
               +g.text_svg(x+24,y+h-24,artifact,9,g.MONO,g.MUTED)
               +f'<rect x="{x+w-56}" y="{y+12}" width="40" height="16" rx="2" fill="{g.PAPER}" stroke="#bfc0c0"/>'
               +g.text_svg(x+w-36,y+24,d['replicas'][n['id']],8,g.MONO,g.SOFT,anchor='middle'))
        pat=rf'(<g data-node-id="{re.escape(n["id"])}">.*?)(</g>)'
        svg,count=re.subn(pat,lambda m:m[1]+extra+m[2],svg,flags=re.S);assert count==1
        add_cell(root,f'artifact-{n["id"]}',artifact,16,h-40,w-32,24,f'rounded=1;arcSize=8;html=0;spacing=8;align=left;fontSize=9;fontFamily={g.MONO};fillColor=#e4e6e8;strokeColor=#bfc0c0;fontColor={g.MUTED};',parent=n['id'])
        add_cell(root,f'replicas-{n["id"]}',d['replicas'][n['id']],w-56,12,40,16,f'rounded=1;arcSize=4;html=0;spacing=0;align=center;fontSize=8;fontFamily={g.MONO};fillColor={g.PAPER};strokeColor=#bfc0c0;fontColor={g.SOFT};',parent=n['id'])
    html=g.make_html(d).replace(g.svg(d),svg)
    ET.indent(mx,space='  ')
    return html,ET.tostring(mx,encoding='unicode',xml_declaration=True)+'\n'


class Canvas:
    def __init__(self,d):self.d=d;self.ops=[]
    def rect(self,x,y,w,h,fill=g.PAPER,stroke='#bfc0c0',rx=6,dash=False,group=None):self.ops.append(dict(k='rect',x=x,y=y,w=w,h=h,fill=fill,stroke=stroke,rx=rx,dash=dash,group=group))
    def text(self,x,y,value,size=11,font=g.SANS,color=g.MUTED,weight=400,anchor='start'):self.ops.append(dict(k='text',x=x,y=y,value=value,size=size,font=font,color=color,weight=weight,anchor=anchor))
    def path(self,points,color=g.MUTED,dash=False,marker='arrow',width=1.2):self.ops.append(dict(k='path',points=points,color=color,dash=dash,marker=marker,width=width))
    def render(self):
        d=self.d;slug=d['slug'];mx=ET.Element('mxfile',host='app.diagrams.net',agent='Jinny',version='32.6.10',type='device');diagram=ET.SubElement(mx,'diagram',id=slug,name=d['title']);model=ET.SubElement(diagram,'mxGraphModel',dx='1584',dy='1120',grid='1',gridSize='4',page='1',pageScale='1',pageWidth='1584',pageHeight='1120',background=g.PAPER);root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
        svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1584 1120" role="img" aria-labelledby="{slug}-title {slug}-desc">',f'<title id="{slug}-title">{g.esc(d["title"])}</title>',f'<desc id="{slug}-desc">{g.esc(d["title"])}. Time ordered coordination with explicit proposal and transaction boundaries.</desc>','<defs>']
        for name,col in [('arrow',g.MUTED),('accent',g.ACCENT),('open',g.MUTED)]:
            shape=f'<polyline points="0 0,8 3,0 6" fill="none" stroke="{col}"/>' if name=='open' else f'<polygon points="0 0,8 3,0 6" fill="{col}"/>'
            svg.append(f'<marker id="{slug}-{name}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">{shape}</marker>')
        svg.extend(['</defs>',f'<rect width="1584" height="1120" fill="{g.PAPER}"/>'])
        for i,o in enumerate(self.ops):
            key=f'op-{i}';k=o['k']
            if k=='rect':
                group=o['group'];start=f'<g data-node-id="{group}">' if group else ''
                svg.append(start+f'<rect'+(' data-role="node-bounds"' if group else '')+f' x="{o["x"]:g}" y="{o["y"]:g}" width="{o["w"]:g}" height="{o["h"]:g}" rx="{o["rx"]}" fill="{o["fill"]}" stroke="{o["stroke"]}"'+(' stroke-dasharray="4,4"' if o['dash'] else '')+'/>'+('</g>' if group else ''))
                add_cell(root,key,'',o['x'],o['y'],o['w'],o['h'],f'rounded=1;absoluteArcSize=1;arcSize={o["rx"]*2};html=0;fillColor={o["fill"]};strokeColor={o["stroke"]};strokeWidth=0.8;'+('dashed=1;dashPattern=4 4;' if o['dash'] else ''))
            elif k=='text':
                svg.append(g.text_svg(o['x'],o['y'],o['value'],o['size'],o['font'],o['color'],o['weight'],o['anchor']))
                w=max(24,len(o['value'])*o['size']*.66+8);x=o['x']-(w/2 if o['anchor']=='middle' else w if o['anchor']=='end' else 0)
                add_cell(root,key,o['value'],x,o['y']-o['size']-1,w,o['size']+6,f'text;html=0;spacing=0;align={"center" if o["anchor"]=="middle" else "right" if o["anchor"]=="end" else "left"};verticalAlign=middle;fontSize={o["size"]};fontFamily={o["font"]};fontColor={o["color"]};'+('fontStyle=1;' if o['weight']>=600 else ''))
            else:
                marker=f' marker-end="url(#{slug}-{o["marker"]})"' if o['marker'] else ''
                svg.append(f'<path d="{g.rounded_path(o["points"])}" fill="none" stroke="{o["color"]}" stroke-width="{o["width"]}"'+(' stroke-dasharray="4,4"' if o['dash'] else '')+marker+'/>')
                arrow='none' if not o['marker'] else 'open' if o['marker']=='open' else 'block'
                add_cell(root,key,'',0,0,0,0,f'rounded=1;arcSize=8;html=0;endArrow={arrow};endFill={0 if arrow=="open" else 1};strokeColor={o["color"]};strokeWidth={o["width"]};'+('dashed=1;dashPattern=4 4;' if o['dash'] else ''),edge=True,points=o['points'])
        svg.append('</svg>');svg='\n'.join(svg);template=dict(slug=slug,title=d['title'],type='Sequence',pattern=None,eyebrow='',subtitle='',desc=d['title'],nodes=[],edges=[],zones=[],notes=[],source='',legend=[])
        html=g.make_html(template).replace(g.svg(template),svg)
        ET.indent(mx,space='  ')
        return html,ET.tostring(mx,encoding='unicode',xml_declaration=True)+'\n'


def sequence_sources(d):
    c=Canvas(d);actors=d['actors'];n=len(actors);positions={3:[160,792,1424],4:[160,580,1004,1424],5:[160,476,792,1108,1424]}[n];xs={a[0]:x for a,x in zip(actors,positions)};frag=d['fragment'];ys=[];current=320;frame={}
    for i,m in enumerate(d['messages']):
        if frag and i==frag['start']:frame['top']=current-28;frame['guard1']=current+4;current+=40
        if frag and i==frag['split']:frame['divider']=current-16;frame['guard2']=current+8;current+=48
        if frag and i==frag['end']:frame['bottom']=current-24;current+=16
        ys.append(current);current+=56
    if frag and 'bottom' not in frame:frame['bottom']=current-24
    assert len(actors)<=5 and len(d['messages'])<=12 and max(ys)<=936,(d['slug'],ys)
    assert all(len(m['label'])<=14 and m['src']!=m['dst'] and m['src'] in xs and m['dst'] in xs for m in d['messages'])
    c.text(40,48,'E-COMMERCE / COORDINATION SEQUENCE / PROPOSED CONTROLS',8,g.MONO,g.SOFT,500);c.text(40,88,d['title'],32,g.SERIF,g.INK);c.text(40,116,'Time flows down. Existing business rules are retained; new operation/receipt/outbox protocols remain in review.',12)
    if frag:
        subset={k for m in d['messages'][frag['start']:frag['end']] for k in [m['src'],m['dst']]};left=min(xs[k] for k in subset)-24;right=max(xs[k] for k in subset)+24
        c.rect(left,frame['top'],right-left,frame['bottom']-frame['top'],fill='#f1f1f1',rx=4)
        c.rect(left,frame['top'],40,16,rx=2);c.text(left+20,frame['top']+12,'ALT',8,g.MONO,g.SOFT,anchor='middle')
        c.text(left+12,frame['guard1'],'['+frag['guards'][0]+']',8,g.MONO,g.SOFT)
        c.path([(left+8,frame['divider']),(right-8,frame['divider'])],color='#bfc0c0',dash=True,marker=None,width=.8)
        c.text(left+12,frame['guard2'],'['+frag['guards'][1]+']',8,g.MONO,g.SOFT)
        assert frame['divider']-ys[frag['split']-1]>=16 and ys[frag['split']]-frame['divider']>=16
    for key,name,tag in actors:
        x=xs[key];focal=key=='api' or ('api' not in xs and key=='relay')
        c.path([(x,272),(x,944)],color='#bfc0c0',dash=True,marker=None,width=.8)
        c.rect(x-120,160,240,112,fill='#f1e7e4' if focal else '#ffffff',stroke=g.ACCENT if focal else g.INK,group=key)
        c.text(x,184,tag,8,g.MONO,g.SOFT,anchor='middle');c.text(x,212,name,12,g.SANS,g.INK,600,'middle');c.text(x,244,key+' / coordination role',9,g.MONO,g.SOFT,anchor='middle')
    activations=[]
    for i,m in enumerate(d['messages']):
        if m['kind'] not in ['return','success'] or m['reply'] is None:continue
        call=m['reply'];actor=d['messages'][call]['dst'];activations.append((actor,ys[call],ys[i]+8))
    # Alternative responses share one enclosing activation, not stacked bars.
    byactor={}
    for actor,start,end in activations:
        if (actor,start) in byactor:byactor[(actor,start)]=max(end,byactor[(actor,start)])
        else:byactor[(actor,start)]=end
    if d['slug']=='checkout-sequence':byactor[('sql',ys[3])]=ys[6]+8;byactor.pop(('sql',ys[5]),None)
    for (actor,start),end in byactor.items():c.rect(xs[actor]-4,start,8,end-start,fill='#e4e6e8',stroke=g.MUTED,rx=0)
    for i,(m,y) in enumerate(zip(d['messages'],ys)):
        a,b=xs[m['src']],xs[m['dst']];direction=1 if b>a else -1
        marker='open' if m['kind']=='async' else 'accent' if m['kind']=='success' else 'arrow';color=g.ACCENT if m['kind']=='success' else g.MUTED
        c.path([(a+4*direction,y),(b-4*direction,y)],color=color,dash=m['kind'] in ['return','async'],marker=marker)
        # Pick an inter-lifeline gap; labels must never cover an intervening lifeline.
        gaps=[(p+q)/2 for p,q in zip(positions,positions[1:]) if min(a,b)<=p and q<=max(a,b)];cx=min(gaps,key=lambda x:abs(x-(a+b)/2))
        label=(cx,y-16,m['label']);x,ly,w,h=g.label_box(label);assert all(not(x-3<px<x+w+3) for px in positions)
        c.rect(x,ly,w,h,stroke=g.PAPER,rx=2);c.text(cx,y-11,m['label'],8,g.MONO,g.SOFT,anchor='middle');c.text(40,y+3,f'{i+1:02d}',9,g.MONO,g.SOFT)
    for i,note in enumerate(d['notes']):
        assert len(note)*11*.6<1504,(d['slug'],'note too long');c.text(40,976+i*24,note,11)
    c.text(40,1036,'Sources: linked spec.md + sequence.wsd and supporting research | Coordination view; exact SQL stays in API specs.',9,g.MONO,g.SOFT)
    c.path([(40,1052),(1544,1052)],color='#bfc0c0',marker=None,width=.8)
    c.path([(40,1072),(64,1072)]);c.text(80,1076,'Call',10);c.path([(336,1072),(360,1072)],dash=True);c.text(376,1076,'Return',10);c.path([(632,1072),(656,1072)],dash=True,marker='open');c.text(672,1076,'Async hint',10);c.rect(928,1066,16,12,fill='#f1e7e4',stroke=g.ACCENT,rx=2);c.text(960,1076,'Headline success',10);c.text(1224,1076,'ALT = mutually exclusive branches',10)
    print(f'PASS {d["slug"]}: Sequence, {n} lifelines / {len(ys)} messages; ALT bounds, label gaps and time order')
    return c.render()


def main():
    # Keep previous entrypoints safe: the owner-requested hierarchy renderer is authoritative.
    from generate_layered_diagrams import main as layered_main
    return layered_main()
    ap=argparse.ArgumentParser();ap.add_argument('--finalize-pngs',action='store_true');ap.add_argument('--check',action='store_true');args=ap.parse_args()
    for d in SHEETS+SEQUENCES:
        if d in SHEETS:g.verify(d);html,xml=sheet_sources(d)
        else:html,xml=sequence_sources(d)
        if args.finalize_pngs:g.finalise_png(d)
        elif args.check:
            assert (OUT/f'{d["slug"]}.html').read_text()==html,d['slug']+' HTML drift'
            assert (OUT/f'{d["slug"]}.drawio').read_text()==xml,d['slug']+' XML drift'
        else:
            (OUT/f'{d["slug"]}.html').write_text(html);(OUT/f'{d["slug"]}.drawio').write_text(xml)
    print('PASS twelve supporting views: generated/checkable native and HTML sources')

if __name__=='__main__':main()
