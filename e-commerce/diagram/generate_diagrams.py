#!/usr/bin/env python3
"""Build detailed HTML/draw.io views; use --finalize-pngs after native export."""

from __future__ import annotations

import argparse
import html
import math
from pathlib import Path
import struct
import textwrap
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zlib

from diagram_content import DIAGRAMS


OUT = Path(__file__).resolve().parent
PROJECT = OUT.parent
W, H = 1584, 1120
PAPER, INK, MUTED = "#f5f5f5", "#2d3142", "#4f5d75"
SOFT, ACCENT, LINK = "#5a6580", "#bf4520", "#2e5aa8"
SANS, MONO, SERIF = "Geist,Arial,sans-serif", "Geist Mono,Courier New,monospace", "Instrument Serif,Georgia,serif"
FONTS = "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap"
COLORS = {"muted": MUTED, "accent": ACCENT, "link": LINK}


def esc(value):
    return html.escape(str(value), quote=True)


def treatment(kind):
    return {
        "backend": ("#ffffff", INK), "focal": ("#f1e7e4", ACCENT),
        "store": ("#ebebec", MUTED), "input": ("#e4e6e8", SOFT),
        "folder": ("#efeff0", SOFT), "state": ("#ffffff", INK),
        "terminal": ("#ebebec", MUTED), "optional": ("#efeff0", SOFT),
    }[kind]


def row_layout(n):
    """Conservative readable wrapping; all rows retain full source content."""
    laid_out=[]
    for value, role in n["rows"]:
        size = 9 if role=="mono" else 11
        capacity=math.floor((n["w"]-32)/(size*(.62 if role=="mono" else .60)))
        for line in textwrap.wrap(value,width=capacity,break_long_words=False,break_on_hyphens=False):
            laid_out.append((line,role))
    return laid_out


def rounded_path(points):
    commands=[f'M {points[0][0]:g} {points[0][1]:g}']
    for a,b,c in zip(points,points[1:],points[2:]):
        da,dc=math.dist(a,b),math.dist(b,c)
        r=min(8,da/2,dc/2)
        assert r>=6, ('Corner radius below skill minimum',a,b,c)
        p=(b[0]+(a[0]-b[0])*r/da,b[1]+(a[1]-b[1])*r/da)
        q=(b[0]+(c[0]-b[0])*r/dc,b[1]+(c[1]-b[1])*r/dc)
        commands.append(f'L {p[0]:g} {p[1]:g} Q {b[0]:g} {b[1]:g} {q[0]:g} {q[1]:g}')
    commands.append(f'L {points[-1][0]:g} {points[-1][1]:g}')
    return ' '.join(commands)


def label_box(label):
    cx,y,value=label
    width=math.ceil((len(value)*8*.62+16)/4)*4
    return cx-width/2,y-4,width,12


def text_svg(x,y,value,size=11,family=SANS,color=INK,weight=400,anchor="start"):
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" font-family="{esc(family)}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{esc(value)}</text>'


def page_texts(d):
    yield 40,48,d["eyebrow"],8,MONO,SOFT,500
    yield 40,88,d["title"],32,SERIF,INK,400
    yield 40,116,d["subtitle"],12,SANS,MUTED,400
    for x,y,value,size,role in d["notes"]:
        yield x,y,value,size,MONO if role=="mono" else SANS,MUTED,600 if role=="heading" else 400
    yield 40,1036,d["source"],9,MONO,SOFT,400


def legend_items(d):
    step=248 if len(d["legend"])==6 else 296
    for i,(kind,value) in enumerate(d["legend"]):
        yield 40+i*step,kind,value


def svg(d):
    slug=d["slug"]
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="{slug}-title {slug}-desc">',
       f'<title id="{slug}-title">{esc(d["title"])}</title>',f'<desc id="{slug}-desc">{esc(d["desc"])}</desc>','<defs>']
    for name,color in [("arrow",MUTED),("arrow-accent",ACCENT),("arrow-link",LINK)]:
        p.append(f'<marker id="{slug}-{name}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="{color}"/></marker>')
    p.extend(['</defs>',f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>'])
    for x,y,w,h,label,kind in d["zones"]:
        fill="#f1f1f1" if kind in {"system","recovery","outcome"} else PAPER
        dash=' stroke-dasharray="5,4"' if kind in {"system","application"} else ''
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="#bfc0c0" stroke-width="0.8"{dash}/>')
        p.append(text_svg(x+16,y+16,label,8,MONO,SOFT))
    for e in d["edges"]:
        color=COLORS[e["color"]]
        marker="arrow-link" if e["color"]=="link" else "arrow-accent" if e["color"]=="accent" else "arrow"
        dash=' stroke-dasharray="5,4"' if e["dashed"] else ''
        p.append(f'<path data-source="{e["source"] or "initial"}" data-target="{e["target"]}" d="{rounded_path(e["points"])}" fill="none" stroke="{color}" stroke-width="1.2"{dash} marker-end="url(#{slug}-{marker})"/>')
        if e["label"]:
            x,y,w,h=label_box(e["label"])
            p.append(f'<rect data-role="label-mask" x="{x:g}" y="{y:g}" width="{w}" height="{h}" rx="2" fill="{PAPER}"/>')
            p.append(text_svg(e["label"][0],e["label"][1]+5,e["label"][2],8,MONO,SOFT,anchor="middle"))
    if d.get("start"):
        x,y=d["start"]
        p.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{INK}"/>')
    for n in d["nodes"]:
        x,y,w,h=(n[k] for k in ("x","y","w","h"))
        fill,stroke=treatment(n["kind"])
        radius=8 if d["type"]=="State Machine" else 6
        dash=' stroke-dasharray="5,4"' if n["kind"]=="optional" else ''
        p.append(f'<g data-node-id="{n["id"]}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{PAPER}"/>')
        p.append(f'<rect data-role="node-bounds" x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"{dash}/>')
        tagw=math.ceil((len(n["tag"])*8*.62+12)/4)*4
        p.append(f'<rect x="{x+16}" y="{y+12}" width="{tagw}" height="12" rx="2" fill="none" stroke="{stroke}" stroke-width="0.8"/>')
        p.append(text_svg(x+22,y+21,n["tag"],8,MONO,stroke))
        p.append(text_svg(x+16,y+44,n["title"] ,12,SANS,INK,600))
        p.append(f'<line x1="{x+16}" y1="{y+54}" x2="{x+w-16}" y2="{y+54}" stroke="#bfc0c0" stroke-width="0.8"/>')
        for i,(value,role) in enumerate(row_layout(n)):
            p.append(text_svg(x+16,y+68+i*16,value,9 if role=="mono" else 11,MONO if role=="mono" else SANS,MUTED))
        p.append('</g>')
    for args in page_texts(d):
        p.append(text_svg(*args))
    p.append(f'<line x1="40" y1="1052" x2="1544" y2="1052" stroke="#bfc0c0" stroke-width="0.8"/>')
    for x,kind,value in legend_items(d):
        if kind in {"arrow","dashed","link"}:
            color=LINK if kind=="link" else MUTED
            dash=' stroke-dasharray="5,4"' if kind in {"dashed","link"} else ''
            marker="arrow-link" if kind=="link" else "arrow"
            p.append(f'<path d="M {x} 1072 H {x+24}" fill="none" stroke="{color}"{dash} marker-end="url(#{slug}-{marker})"/>')
        elif kind!="text":
            fill,stroke=treatment({"box":"backend"}.get(kind,kind))
            dash=' stroke-dasharray="5,4"' if kind=="optional" else ''
            p.append(f'<rect x="{x}" y="1066" width="16" height="12" rx="2" fill="{fill}" stroke="{stroke}"{dash}/>')
        p.append(text_svg(x+(0 if kind=="text" else 32),1076,value,10,SANS,MUTED))
    p.append('</svg>')
    return '\n'.join(p)


def make_html(d):
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{esc(d['title'])}</title><link href="{esc(FONTS)}" rel="stylesheet">
<style>
* {{box-sizing:border-box;}} body {{margin:0;padding:24px;background:{PAPER};color:{INK};font-family:'Geist',Arial,sans-serif;}}
main {{width:100%;max-width:{W}px;min-width:0;margin:0 auto;}} h1 {{font-family:'Instrument Serif',Georgia,serif;font-size:32px;font-weight:400;}}
.diagram-container {{width:100%;overflow-x:auto;}} svg {{display:block;width:100%;min-width:{W}px;}}
.source-note {{font-size:12px;line-height:1.6;color:{MUTED};}} @media print {{body {{padding:0;}} .diagram-container {{overflow-x:visible;}} svg {{min-width:0;}}}}
</style></head><body><main><h1>{esc(d['title'])}</h1><div class="diagram-container">{svg(d)}</div>
<p class="source-note">View: {esc(d['type'])}{' / '+esc(d['pattern']) if d['pattern'] else ''}. A3 landscape, 1584 × 1120. Default light style.
The matching PNG contains editable draw.io data. Supplied font fallbacks: Georgia, Arial and Courier New. Research, evidence and limitations: research.md and README.md.</p>
</main></body></html>
'''


def make_drawio(d):
    mx=ET.Element("mxfile",host="app.diagrams.net",agent="Jinny",version="32.6.10",type="device")
    diagram=ET.SubElement(mx,"diagram",id=d["slug"],name=d["title"])
    model=ET.SubElement(diagram,"mxGraphModel",dx=str(W),dy=str(H),grid="1",gridSize="4",guides="1",connect="1",arrows="1",page="1",pageScale="1",pageWidth=str(W),pageHeight=str(H),background=PAPER,math="0",shadow="0")
    root=ET.SubElement(model,"root")
    ET.SubElement(root,"mxCell",id="0");ET.SubElement(root,"mxCell",id="1",parent="0")
    counter=0

    def cell(value,x,y,w,h,style,key=None):
        nonlocal counter
        counter+=1
        c=ET.SubElement(root,"mxCell",id=key or f"decor-{counter}",value=value,style=style,vertex="1",parent="1")
        ET.SubElement(c,"mxGeometry",x=f'{x:g}',y=f'{y:g}',width=f'{w:g}',height=f'{h:g}',attrib={"as":"geometry"})
        return c

    def plain(value,x,y,size=11,family=SANS,color=INK,weight=400,width=None):
        style=f'text;html=0;align=left;verticalAlign=middle;spacing=0;whiteSpace=wrap;overflow=hidden;strokeColor=none;fillColor=none;fontColor={color};fontFamily={family};fontSize={size};fontStyle={1 if weight>=600 else 0};'
        cell(value,x,y-size-3,width or W-40-x,size+8,style)

    cell("",0,0,W,H,f'shape=rect;fillColor={PAPER};strokeColor=none;connectable=0;')
    for x,y,w,h,title,kind in d["zones"]:
        fill="#f1f1f1" if kind in {"system","recovery","outcome"} else PAPER
        cell("",x,y,w,h,f'rounded=1;absoluteArcSize=1;arcSize=16;fillColor={fill};strokeColor=#bfc0c0;strokeWidth=0.8;'+('dashed=1;dashPattern=5 4;' if kind in {"system","application"} else ''))
        plain(title,x+16,y+16,8,MONO,SOFT)
    by_id={n["id"]:n for n in d["nodes"]}
    for i,e in enumerate(d["edges"]):
        a=by_id.get(e["source"]);b=by_id[e["target"]]
        p,q=e["points"][0],e["points"][-1]
        style=f'edgeStyle=none;rounded=1;curved=0;arcSize=16;html=0;endArrow=block;endFill=1;endSize=6;strokeWidth=1.2;strokeColor={COLORS[e["color"]]};'
        if a:
            style+=f'exitX={(p[0]-a["x"])/a["w"]};exitY={(p[1]-a["y"])/a["h"]};exitPerimeter=0;'
        style+=f'entryX={(q[0]-b["x"])/b["w"]};entryY={(q[1]-b["y"])/b["h"]};entryPerimeter=0;'
        if e["dashed"]:style+='dashed=1;dashPattern=5 4;'
        attrs=dict(id=f'edge-{i}',value="",style=style,edge="1",parent="1",target=e["target"])
        if a:attrs["source"]=e["source"]
        c=ET.SubElement(root,"mxCell",**attrs);geo=ET.SubElement(c,"mxGeometry",relative="1",attrib={"as":"geometry"})
        if not a:ET.SubElement(geo,"mxPoint",x=str(p[0]),y=str(p[1]),attrib={"as":"sourcePoint"})
        if len(e["points"])>2:
            arr=ET.SubElement(geo,"Array",attrib={"as":"points"})
            for x,y in e["points"][1:-1]:ET.SubElement(arr,"mxPoint",x=f'{x:g}',y=f'{y:g}')
        if e["label"]:
            x,y,w,h=label_box(e["label"])
            cell(e["label"][2],x,y,w,h,f'text;html=0;align=center;verticalAlign=middle;spacing=0;fontSize=8;fontFamily={MONO};fontColor={SOFT};fillColor={PAPER};strokeColor=none;')
    if d.get("start"):
        x,y=d["start"];cell("",x-6,y-6,12,12,f'ellipse;fillColor={INK};strokeColor=none;')
    for n in d["nodes"]:
        fill,stroke=treatment(n["kind"])
        tagw=math.ceil((len(n["tag"])*8*.62+12)/4)*4
        label=(f'<div style="position:relative;box-sizing:border-box;width:{n["w"]}px;height:{n["h"]}px;text-align:left;color:{INK};">'
               f'<div style="position:absolute;left:16px;top:12px;box-sizing:border-box;border:0.8px solid {stroke};border-radius:2px;width:{tagw}px;height:12px;line-height:10px;padding-left:5px;font-size:8px;font-family:{MONO};">{esc(n["tag"])}</div>'
               f'<div style="position:absolute;left:16px;top:32px;font-family:{SANS};font-size:12px;line-height:16px;font-weight:600;white-space:nowrap;">{esc(n["title"])}</div>'
               f'<div style="position:absolute;left:16px;top:54px;width:{n["w"]-32}px;border-top:0.8px solid #bfc0c0;"></div>')
        for j,(value,role) in enumerate(row_layout(n)):
            family,size=(MONO,9) if role=="mono" else (SANS,11)
            label+=f'<div style="position:absolute;left:16px;top:{58+j*16}px;font-family:{family};font-size:{size}px;line-height:16px;white-space:nowrap;color:{MUTED};">{esc(value)}</div>'
        label+='</div>'
        radius=16 if d["type"]=="State Machine" else 12
        style=f'rounded=1;absoluteArcSize=1;arcSize={radius};whiteSpace=wrap;html=1;overflow=hidden;align=left;verticalAlign=top;spacing=0;fillColor={fill};strokeColor={stroke};strokeWidth=1.2;'
        if n["kind"]=="optional":style+='dashed=1;dashPattern=5 4;'
        cell(label,n["x"],n["y"],n["w"],n["h"],style,n["id"])
    for x,y,value,size,family,color,weight in page_texts(d):plain(value,x,y,size,family,color,weight)
    cell("",40,1052,1504,1,"shape=line;strokeColor=#bfc0c0;strokeWidth=0.8;")
    for i,(x,kind,value) in enumerate(legend_items(d)):
        if kind in {"arrow","dashed","link"}:
            color=LINK if kind=="link" else MUTED
            c=ET.SubElement(root,"mxCell",id=f'legend-edge-{i}',value="",style=f'endArrow=block;endSize=6;endFill=1;strokeColor={color};'+('dashed=1;dashPattern=5 4;' if kind in {"dashed","link"} else ''),edge="1",parent="1")
            geo=ET.SubElement(c,"mxGeometry",relative="1",attrib={"as":"geometry"})
            ET.SubElement(geo,"mxPoint",x=str(x),y="1072",attrib={"as":"sourcePoint"});ET.SubElement(geo,"mxPoint",x=str(x+24),y="1072",attrib={"as":"targetPoint"})
        elif kind!="text":
            fill,stroke=treatment({"box":"backend"}.get(kind,kind))
            cell("",x,1066,16,12,f'rounded=1;absoluteArcSize=1;arcSize=4;fillColor={fill};strokeColor={stroke};'+('dashed=1;dashPattern=5 4;' if kind=="optional" else ''))
        plain(value,x+(0 if kind=="text" else 32),1076,10,SANS,MUTED,width=250)
    ET.indent(mx,space="  ")
    return ET.tostring(mx,encoding="unicode",xml_declaration=True)+'\n'


def overlap(a,b):
    return a[0]<b[0]+b[2] and b[0]<a[0]+a[2] and a[1]<b[1]+b[3] and b[1]<a[1]+a[3]


def segment_hits_box(p,q,box):
    x,y,w,h=box
    if p[1]==q[1]:return y<p[1]<y+h and max(min(p[0],q[0]),x)<min(max(p[0],q[0]),x+w)
    return x<p[0]<x+w and max(min(p[1],q[1]),y)<min(max(p[1],q[1]),y+h)


def verify(d):
    assert len(d["nodes"])+bool(d.get("start"))<=9 and len(d["edges"])<=12
    assert sum(n["kind"]=="focal" for n in d["nodes"])<=2
    rects={n["id"]:tuple(n[k] for k in ("x","y","w","h")) for n in d["nodes"]}
    for n in d["nodes"]:
        assert all(n[k]%4==0 for k in ("x","y","w","h"))
        assert n["x"]>=40 and n["y"]>=40 and n["x"]+n["w"]<=W-40 and n["y"]+n["h"]<=1016
        assert 68+(len(row_layout(n))-1)*16+4<=n["h"]-8,(d["slug"],n["id"],"text height",len(row_layout(n)))
        for other in d["nodes"]:
            if n is not other:assert not overlap(rects[n["id"]],rects[other["id"]]),(d["slug"],"node overlap")
    segments=[];ports=set();masks=[]
    for e in d["edges"]:
        rounded_path(e["points"])
        if e["label"]:
            assert len(e["label"][2])<=14 and e["label"][2].upper()==e["label"][2]
            box=label_box(e["label"]);masks.append(box)
            assert not any(overlap(box,b) for b in rects.values()),(d["slug"],"mask overlaps node",e["label"])
            x,y,w,h=box;gaps=[]
            for a,b in zip(e["points"],e["points"][1:]):
                if a[1]==b[1] and max(x,min(a[0],b[0]))<min(x+w,max(a[0],b[0])):gaps.append(max(y-a[1],a[1]-y-h,0))
                if a[0]==b[0] and max(y,min(a[1],b[1]))<min(y+h,max(a[1],b[1])):gaps.append(max(x-a[0],a[0]-x-w,0))
            assert gaps and 6<=min(gaps)<=10,(d["slug"],"label gap",e["label"],gaps)
        for key,p,q in [(e["source"],e["points"][0],e["points"][1]),(e["target"],e["points"][-1],e["points"][-2])]:
            if key is None:continue
            assert (key,p) not in ports,(d["slug"],"shared port",key,p)
            ports.add((key,p));x,y,w,h=rects[key]
            assert (p[0] in (x,x+w) and y+8<=p[1]<=y+h-8 and p[1]==q[1]) or (p[1] in (y,y+h) and x+8<=p[0]<=x+w-8 and p[0]==q[0]),(d["slug"],"invalid perimeter port",key,p)
        for p,q in zip(e["points"],e["points"][1:]):
            assert (p[0]==q[0])!=(p[1]==q[1]),(d["slug"],"diagonal",p,q)
            for key,box in rects.items():
                if key not in (e["source"],e["target"]):assert not segment_hits_box(p,q,box),(d["slug"],"transit",key,p,q)
            for a,b in segments:
                if p[1]==q[1] and a[1]==b[1] and p[1]==a[1]:assert max(min(p[0],q[0]),min(a[0],b[0]))>=min(max(p[0],q[0]),max(a[0],b[0])),(d["slug"],"stacked horizontal")
                if p[0]==q[0] and a[0]==b[0] and p[0]==a[0]:assert max(min(p[1],q[1]),min(a[1],b[1]))>=min(max(p[1],q[1]),max(a[1],b[1])),(d["slug"],"stacked vertical")
                crossing=False
                if p[1]==q[1] and a[0]==b[0]:crossing=min(p[0],q[0])<a[0]<max(p[0],q[0]) and min(a[1],b[1])<p[1]<max(a[1],b[1])
                if p[0]==q[0] and a[1]==b[1]:crossing=min(p[1],q[1])<a[1]<max(p[1],q[1]) and min(a[0],b[0])<p[0]<max(a[0],b[0])
                assert not crossing,(d["slug"],"crossing",p,q,a,b)
            segments.append((p,q))
    for box in masks:
        assert not any(segment_hits_box(p,q,box) for p,q in segments),(d["slug"],"connector through label mask",box)
    for x,y,value,size,role in d["notes"]:
        box=(x,y-size,len(value)*size*.60,size+2)
        assert not any(segment_hits_box(p,q,box) for p,q in segments),(d["slug"],"connector through annotation",value)
    print(f'PASS {d["slug"]}: {d["type"]}, {len(d["nodes"])} detail nodes / {len(d["edges"])} connectors; routes, text capacity, masks and grid')


def verify_evidence():
    actual={}
    for p in (PROJECT/'repository/src').glob('*/*.csproj'):
        key=p.stem.removeprefix('Ecommerce.').lower()
        actual[key]={r.attrib['Include'].replace('\\','/').split('/')[-1].removesuffix('.csproj').removeprefix('Ecommerce.').lower() for r in ET.parse(p).getroot().iter('ProjectReference')}
    drawn={n['id']:set(n['refs']) for n in DIAGRAMS[1]['nodes'] if n['refs'] is not None}
    assert actual==drawn,(actual,drawn)
    tests={}
    for p in (PROJECT/'repository/tests').glob('*/*.csproj'):
        tests[p.stem]={r.attrib['Include'].replace('\\','/').split('/')[-1].removesuffix('.csproj').removeprefix('Ecommerce.') for r in ET.parse(p).getroot().iter('ProjectReference')}
    assert tests=={'Ecommerce.Domain.Tests':{'Domain','Shared'},'Ecommerce.Application.Tests':{'Application','Domain','Shared'}}
    for relative in ['repository/Directory.Build.props','repository/src/Ecommerce.Api/Program.cs','repository/src/Ecommerce.Shared/Cqrs/Dispatcher.cs','doc/api/sales/02-create-order/spec.md','doc/api/sales/05-cancel-order/spec.md','doc/api/payment/02-stripe-webhook/spec.md','doc/api/payment/05-refund-payment/spec.md','doc/api/shipping/01-create-shipping/spec.md','doc/api/shipping/02-update-shipping-status/spec.md','doc/api/shipping/06-confirm-delivery/spec.md']:
        assert (PROJECT/relative).is_file(),relative
    sales=(PROJECT/'db/migrations/up/06-sales.schema.up.sql').read_text()
    assert all(status in sales for status in ['WAIT_PAYMENT','PAYMENT_CONFIRMED','PROCESSING','COMPLETED','CANCELLED','REFUNDED'])
    shipping=(PROJECT/'doc/api/shipping/06-confirm-delivery/spec.md').read_text()
    assert '### Automatic Completion Rules' in shipping and '`completion_days` (7)' in shipping,'Shipping baseline lacks merged seven-day completion rules'
    print('PASS evidence: all 9 production / 5 test project references and 6 displayed order statuses match current source files')
    print('PASS shipping baseline: merged seven-day automatic completion rules present')


def png_chunks(raw):
    assert raw[:8]==b'\x89PNG\r\n\x1a\n','Not a PNG'
    cursor=8;chunks=[]
    while cursor<len(raw):
        size=struct.unpack('>I',raw[cursor:cursor+4])[0];kind=raw[cursor+4:cursor+8];payload=raw[cursor+8:cursor+8+size]
        crc=struct.unpack('>I',raw[cursor+8+size:cursor+12+size])[0]
        assert len(payload)==size and zlib.crc32(kind+payload)&0xffffffff==crc,'Invalid PNG CRC'
        chunks.append((kind,payload));cursor+=size+12
    assert chunks[-1][0]==b'IEND' and cursor==len(raw)
    return chunks


def xml_signature(e):
    return e.tag,tuple(sorted(e.attrib.items())),(e.text or '').strip(),tuple(xml_signature(c) for c in e)


def finalise_png(d):
    path=OUT/f'{d["slug"]}.drawio.png';chunks=png_chunks(path.read_bytes());native=None
    for kind,payload in chunks:
        if kind==b'zTXt' and payload.startswith(b'mxGraphModel\0\0'):native=zlib.decompress(payload[len(b'mxGraphModel\0\0'):])
    assert native is not None,f'{path.name}: native editable model missing'
    source=ET.parse(OUT/f'{d["slug"]}.drawio').getroot()
    assert xml_signature(ET.fromstring(unquote(native.decode('ascii'))))==xml_signature(source),f'{path.name}: embedded model differs'
    before=b''.join(v for k,v in chunks if k==b'IDAT');result=bytearray(b'\x89PNG\r\n\x1a\n')
    for kind,payload in chunks:
        if kind in {b'tEXt',b'zTXt',b'iTXt'} and payload.split(b'\0',1)[0]==b'mxfile':continue
        if kind==b'IEND':
            extra=b'mxfile\0\0'+zlib.compress(native,9)
            result+=struct.pack('>I',len(extra))+b'zTXt'+extra+struct.pack('>I',zlib.crc32(b'zTXt'+extra)&0xffffffff)
        result+=struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
    after=png_chunks(bytes(result));assert before==b''.join(v for k,v in after if k==b'IDAT')
    path.write_bytes(result);width,height=struct.unpack('>II',after[0][1][:8])
    print(f'PASS {path.name}: {width} x {height}; exact editable source, compatible metadata, pixel bytes preserved')


def main():
    # Keep previous entrypoints safe: the owner-requested hierarchy renderer is authoritative.
    from generate_layered_diagrams import main as layered_main
    return layered_main()
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--finalize-pngs',action='store_true');args=parser.parse_args()
    verify_evidence()
    for d in DIAGRAMS:
        verify(d)
        if args.finalize_pngs:finalise_png(d)
        else:
            (OUT/f'{d["slug"]}.html').write_text(make_html(d),encoding='utf-8')
            (OUT/f'{d["slug"]}.drawio').write_text(make_drawio(d),encoding='utf-8')
    if not args.finalize_pngs:print('Generated three distinct, detailed HTML and editable draw.io sources')


if __name__=='__main__':
    main()
