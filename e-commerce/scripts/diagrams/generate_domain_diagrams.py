#!/usr/bin/env python3
"""Reproduce four conceptual domain views and verify their SQL traceability."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, re, subprocess, sys
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'e-commerce/diagram/domain'

import generate_layered_diagrams as layered
import generate_diagrams as g
from generate_supporting_diagrams import add_cell
from domain_model_content import CONCEPTS, views
from domain_model_notes import NOTES

SNAPSHOT=OUT/'domain-source-inventory.json'

def evidence():
 spec=importlib.util.spec_from_file_location('domain_schema_audit',ROOT/'e-commerce/db/tests/audit_all.py')
 audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
 tables=audit.parse_migrations();indexes=audit.indexes_of(tables)
 audit.audit_docs(tables,indexes);audit.audit_readme(tables)
 assert not audit.FINDINGS,audit.FINDINGS
 assert set(tables)==set(CONCEPTS),'Every existing SQL table must map to exactly one concept'
 fk_count=sum(bool(c['ref'])for t in tables.values()for c in t['cols'])
 assert (len(tables),len({t['schema']for t in tables.values()}),fk_count)==(53,11,75)
 files=list((ROOT/'e-commerce/db/migrations/up').glob('*.sql'))+list((ROOT/'e-commerce/doc/schema').glob('*/*.md'))+[ROOT/'e-commerce/doc/schema/README.md']
 paths={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(files)if p.name!='template.md'}
 result=dict(table_count=53,schema_count=11,fk_count=75,source_files=paths,tables={k:dict(v,concept=CONCEPTS[k][0],indexes=indexes.get(k,[]))for k,v in tables.items()})
 return result

def sync_inventory(fresh,refresh=False):
 if SNAPSHOT.exists()and not refresh:
  stored=json.loads(SNAPSHOT.read_text());original=dict(stored);original.pop('source_commit')
  # JSON serializes parser reference tuples as lists.
  assert original==json.loads(json.dumps(fresh)),'DB evidence drift: review the model, then use --refresh-inventory'
  return stored
 fresh['source_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 SNAPSHOT.write_text(json.dumps(fresh,ensure_ascii=False,indent=2)+'\n');return fresh

def common_parent(a,b,d):
 items={n['id']:n for n in d['containers']+d['nodes']}
 aa=layered.ancestors(a,items);bb=layered.ancestors(b,items)
 return next((p for p in aa if p in bb),'1')

def card_boxes(d):
 boxes=[];segments=[(p,q)for e in d['edges']for p,q in zip(e['points'],e['points'][1:])]
 obstacles=[layered.bounds(n)for n in d['nodes']]+[(n['x'],n['y'],n['w'],36)for n in d['containers']]
 for ei,e in enumerate(d['edges']):
  for end,value in [('source',e['parent_card']),('target',e['child_card'])]:
   points=e['points']if end=='source'else list(reversed(e['points']));w=math.ceil((len(value)*4.8+8)/4)*4;h=12;found=None;travel=0
   for a,b in zip(points,points[1:]):
    length=abs(a[0]-b[0])+abs(a[1]-b[1])
    for distance in range(12,int(min(length-4,120-travel))+1,4):
     x=a[0]+(b[0]-a[0])*distance/length;y=a[1]+(b[1]-a[1])*distance/length
     for side in [-1,1]:
      rect=(x-w/2,y+side*(h/2+8)-h/2,w,h)if a[1]==b[1]else(x+side*(w/2+8)-w/2,y-h/2,w,h)
      rx,ry,rw,rh=rect
      if not(24<=rx and ry>=196 and rx+rw<=1560 and ry+rh<=1000):continue
      if any(g.overlap(rect,o)for o in obstacles+[v['rect']for v in boxes]):continue
      if any(g.segment_hits_box(p,q,rect)for p,q in segments):continue
      found=rect;break
     if found:break
    travel+=length
    if found or travel>=120:break
   assert found,(d['slug'],'no readable cardinality position',ei,end)
   boxes.append(dict(id=f'card-{ei}-{end}',value=value,rect=found,parent=common_parent(e['source'],e['target'],d)))
 return boxes

def validate(d,source):
 layered.verify(d)
 expected={k for k,t in source['tables'].items()if t['schema']in d['schemas']}
 if d['schemas']:assert {n['table']for n in d['nodes']}==expected,(d['slug'],'table coverage')
 assert len(d['nodes'])<=24 and len(d['edges'])<=12
 for e in d['edges']:
  fk=e['fk'];column=next(c for c in source['tables'][fk['child']]['cols']if c['name']==fk['column'])
  assert column['ref']and '.'.join(column['ref'])==fk['parent']
  # No FK column is unconditionally unique by itself in this schema.
  assert not re.search(r'\bUNIQUE\s*\(\s*'+re.escape(fk['column'])+r'\s*\)',source['tables'][fk['child']]['sql'])
  e['parent_card']='0..1'if column['nullable']else'1';e['child_card']='0..*'
 labels=card_boxes(d)if d['schemas']else[]
 print(f'PASS {d["slug"]}: {len(expected) if d["schemas"]else 53} source tables; {len(d["edges"])} verified associations; {len(labels)} cardinalities')
 return labels

def render(d,labels):
 html,xml=layered.render(d);mx=ET.fromstring(xml);root=mx.find('./diagram/mxGraphModel/root');items={n['id']:n for n in d['containers']+d['nodes']};extra=[]
 # Entity header/body hairlines distinguish this view from the architecture cards.
 for n in d['nodes']:
  if not n.get('table'):continue
  x,y,w,h=layered.bounds(n);extra.append(f'<line x1="{x+8}" y1="{y+44}" x2="{x+w-8}" y2="{y+44}" stroke="#bfc0c0" stroke-width="0.6"/>')
  add_cell(root,'divider-'+n['id'],'',8,44,w-16,0,'shape=line;strokeColor=#bfc0c0;strokeWidth=0.6;',parent=n['id'])
 for label in labels:
  x,y,w,h=label['rect'];parent=label['parent'];px,py=(items[parent]['x'],items[parent]['y'])if parent!='1'else(0,0)
  extra.append(f'<g data-cardinality="{label["id"]}"><rect x="{x:g}" y="{y:g}" width="{w}" height="{h}" rx="2" fill="{g.PAPER}"/>'+g.text_svg(x+w/2,y+9,label['value'],8,g.MONO,g.MUTED,anchor='middle')+'</g>')
  add_cell(root,label['id'],label['value'],x-px,y-py,w,h,f'text;html=0;align=center;verticalAlign=middle;spacing=0;fontSize=8;fontFamily={g.MONO};fontColor={g.MUTED};fillColor={g.PAPER};strokeColor=none;',parent=parent)
 footer=f'Research, evidence and limitations: <a href="{g.resource_link(d["slug"], "design/research.md")}">research</a> and <a href="{g.resource_link(d["slug"], "README.md")}">diagram guide</a>.'
 html=html.replace(footer, 'Domain source, evidence and limitations: <a href="domain-model.md">domain model</a> and <a href="README.md">domain guide</a>.')
 html=html.replace('</svg>','\n'.join(extra)+'</svg>');ET.indent(mx,space='  ')
 return html,ET.tostring(mx,encoding='unicode',xml_declaration=True)+'\n'

def companion(d,source):
 slug=d['slug'];names=[k for k,t in source['tables'].items()if not d['schemas']or t['schema']in d['schemas']]
 text=f'''---
name: {d['title']} — explanation and SQL traceability
description: อธิบาย domain diagram {slug} พร้อมเหตุผล ตารางต้นทาง ความสัมพันธ์และcardinalityจากSQL ใช้ก่อนreviewหรือแก้ภาพนี้
status: in-review
approved_by: null
approved_at: null
---

# {d['title']}

[ภาพแก้ไขได้]({slug}.drawio.png) · [draw.io source]({slug}.drawio) · [HTML]({slug}.html) · [สารบัญ](README.md)

'''+NOTES[slug]
 text+='\n## ตารางต้นทางและ concept ที่แสดง\n\nกล่อง/ชื่อเป็นconceptual interpretationของschemaที่มีอยู่ ไม่ใช่รายชื่อclassที่implementแล้ว Universal audit fieldsยังคงอยู่ในDDL แม้ไม่แสดงบนภาพ\n\n| SQL table / schema doc | Business concept | รายละเอียดที่เลือกแสดง | Migration |\n| --- | --- | --- | --- |\n'
 for key in names:
  t=source['tables'][key];fields='; '.join(CONCEPTS[key][1]);text+=f"| [{key}](../../doc/schema/{t['schema']}/{t['table']}.md) | {CONCEPTS[key][0]} | `{fields}` | [{t['file']}](../../db/migrations/up/{t['file']}) |\n"
 if d['schemas']:
  text+='\n## Associations ที่เลือกวาด\n\nตัวเลขใกล้parentคือจำนวนparentต่อchild ตัวเลขใกล้childคือจำนวนchildต่อparent เมื่อรวมทุกแถวในประวัติ เส้นไม่มีหัวลูกศรและไม่บอกลำดับเวลา\n\n| Parent → child (อ่านassociation ไม่ใช่call) | FKของchild | Cardinalityที่ปลาย parent / child |\n| --- | --- | --- |\n'
  for e in d['edges']:text+=f"| {CONCEPTS[e['source']][0]} — {CONCEPTS[e['target']][0]} | `{e['fk']['child']}.{e['fk']['column']}` | `{e['parent_card']}` / `{e['child_card']}` |\n"
  text+='\n## FK catalogue — ครบทุกreferenceของตารางในหน้านี้\n\nรายการที่ไม่ลากเส้นยังเป็นความสัมพันธ์จริงในDB ใช้ตารางนี้ต่อข้ามภาพ 1หมายถึงFKบังคับ, 0..1หมายถึงnullable FK; ด้านจำนวนchildrenเป็น0..*ในโมเดลรวมประวัติ การลบตามFKไม่ใช่หลักฐานUMLcompositionหรือDDDaggregate\n\n| Child FK | Parent table | Parentต่อchild | Childต่อparent | ON DELETE | ในภาพ |\n| --- | --- | --- | --- | --- | --- |\n'
  selected={(e['fk']['child'],e['fk']['column'])for e in d['edges']}
  for key in names:
   t=source['tables'][key]
   for c in t['cols']:
    if not c['ref']:continue
    parent='.'.join(c['ref']);match=re.search(r'\b'+re.escape(c['name'])+r'\s+UUID\b[^,]*?REFERENCES\s+\S+\s*\(id\)\s+ON DELETE (RESTRICT|CASCADE|SET NULL)',t['sql']);assert match,(key,c['name'])
    text+=f"| `{key}.{c['name']}` | `{parent}` | {'0..1'if c['nullable']else'1'} | 0..* | {match.group(1)} | {'วาดเส้น'if(key,c['name'])in selected else'field / catalogue'} |\n"
  text+='\n## Partial uniqueness ที่ต้องไม่อ่านเป็น unconditional1:1\n\n| Table | Unique index / predicate |\n| --- | --- |\n'
  for key in names:
   for index in source['tables'][key]['indexes']:
    if index.startswith('CREATE UNIQUE')and' WHERE 'in index:text+=f"| `{key}` | `{index.replace('CREATE UNIQUE INDEX IF NOT EXISTS ','')}` |\n"
 else:
  text+='\n## Cross-schema references ที่เลือกในภาพรวม\n\nเส้นไม่มีหัวลูกศร แต่ละปลายคือกลุ่มหลายconcept จึงไม่ใส่cardinalityระดับentityหรือสื่อการเรียกservice ใช้FKต่อไปนี้เป็นหลักฐานและอ่านตัวเลขในหน้ารายละเอียดแทน\n\n| กลุ่มที่เชื่อม | FK evidence | Parent table |\n| --- | --- | --- |\n'
  by_id={n['id']:n for n in d['nodes']}
  for e in d['edges']:text+=f"| {by_id[e['source']]['title']} — {by_id[e['target']]['title']} | `{e['fk']['child']}.{e['fk']['column']}` | `{e['fk']['parent']}` |\n"
  text+='\n## เปิดภาพรายละเอียด\n\n- [Identity / Access / Consent](domain-identity-model.md):21ตาราง /23FK\n- [Catalog / Shop / Stock](domain-merchandising-model.md):19ตาราง /25FK\n- [Commerce](domain-commerce-model.md):13ตาราง /27FK\n\nทั้งสามหน้าแบ่ง53ตารางแบบไม่ซ้ำกัน มีFKcatalogueรวม75รายการ รวมถึง7nullableFK ไม่บังคับให้วาดเส้นทั้ง75บนภาพเดียว\n'
 text+='''
## การตรวจและการสร้างซ้ำ

```sh
python3 -B e-commerce/scripts/diagrams/generate_domain_diagrams.py --check
```

Generatorเทียบtable/column/nullability/reference/constraint/indexและhashของmigration/schema docsกับ [source inventory](domain-source-inventory.json) ก่อนตรวจmodel, nativeparent/child, text capacity, routesและcardinality positions ถ้าDBหรือmappingเปลี่ยนให้reviewmodelแล้วใช้ `--refresh-inventory` และสร้างภาพใหม่ ไม่แก้DDLเพื่อให้ภาพผ่าน

```sh
python3 -B e-commerce/scripts/diagrams/generate_domain_diagrams.py
# export each .drawio with draw.io Desktop as shown in README
python3 -B e-commerce/scripts/diagrams/generate_domain_diagrams.py --finalize-pngs
```

ใช้styleอ่อน/แต้มส้มเดิมและA3landscape1584×1120 NativePNGใช้fontfallbacksที่READMEเปิดเผย ผลตรวจภาพจริงและeditabilityอยู่ใน [domain-model-verification.md](domain-model-verification.md) ไม่มีbackend/API/schema implementationหรือruntimeDB/provider testsในงานนี้

## แหล่งอ้างอิง

- [Schema index](../../doc/schema/README.md), [migrations](../../db/migrations/up/), [physical ER เดิม](../../db/er-diagram.drawio)
- [Microsoft domain analysis](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis): ใช้ประกอบการแยกconcept/ขอบเขตเชิงธุรกิจ; ไม่ถือว่าSQLschemaเท่ากับboundedcontext
- [PostgreSQL constraints](https://www.postgresql.org/docs/18/ddl-constraints.html) และ [partial indexes](https://www.postgresql.org/docs/18/indexes-partial.html): ใช้ตีความFK, nullabilityและconditionaluniqueness
'''
 text+=f"\nSQL/schema baseline commit: `{source['source_commit']}`; file hashesบันทึกในinventoryเพื่อให้ตรวจdriftได้ แม้ภายหลังbranchมีcommitงานภาพเพิ่ม\n"
 return text

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--refresh-inventory',action='store_true');parser.add_argument('--finalize-pngs',action='store_true');args=parser.parse_args()
 source=sync_inventory(evidence(),args.refresh_inventory);coverage=[];fk_count=0
 for d in views():
  labels=validate(d,source);html,xml=render(d,labels)
  if d['schemas']:
   tables=[k for k,t in source['tables'].items()if t['schema']in d['schemas']];coverage.extend(tables);fk_count+=sum(bool(c['ref'])for k in tables for c in source['tables'][k]['cols'])
  md=companion(d,source)
  if args.finalize_pngs:g.finalise_png(d,output_dir=OUT)
  elif args.check:
   assert(OUT/f'{d["slug"]}.html').read_text()==html and(OUT/f'{d["slug"]}.drawio').read_text()==xml,d['slug']+' renderer drift'
   assert(OUT/f'{d["slug"]}.md').read_text()==md,d['slug']+' companion drift'
  else:
   (OUT/f'{d["slug"]}.html').write_text(html);(OUT/f'{d["slug"]}.drawio').write_text(xml);(OUT/f'{d["slug"]}.md').write_text(md)
 assert len(coverage)==len(set(coverage))==53 and fk_count==75
 print('PASS domain source coverage: 53/53 tables; 75/75 FK columns; schema documentation comparison 0 findings')

if __name__=='__main__':main()
