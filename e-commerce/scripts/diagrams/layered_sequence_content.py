"""Temporal views with native boundary/participant header decomposition and ALT grouping."""
import copy,math,re
import xml.etree.ElementTree as ET
import generate_diagrams as g
from generate_supporting_diagrams import Canvas
from supporting_content import SEQUENCES


def sequence_sources(d):
 d=copy.deepcopy(d)
 if d['slug']=='checkout-sequence':d['fragment']=dict(operator='OPT',start=3,split=None,end=8,guards=['admitted request; shown SQL guards and commit succeed'])
 c=Canvas(d);actors=d['actors'];positions={3:[160,792,1424],4:[160,580,1004,1424],5:[160,476,792,1108,1424]}[len(actors)];xs={a[0]:x for a,x in zip(actors,positions)};frag=d.get('fragment');ys=[];current=384;frame={};groups={}
 def group(key,x,y,w,h,parent=None,fill='#f0f0f1',stroke=g.SOFT):
  c.rect(x,y,w,h,fill=fill,stroke=stroke,rx=4,group=key);groups[key]=dict(x=x,y=y,w=w,h=h,parent=parent)
 for i,m in enumerate(d['messages']):
  if frag and i==frag['start']:frame.update(top=current-20,guard1=current+4);current+=32
  if frag and i==frag['split']:frame.update(divider=current-12,guard2=current+12);current+=40
  if frag and i==frag['end']:frame['bottom']=current-16;current+=12
  ys.append(current);current+=44
 if frag and 'bottom' not in frame:frame['bottom']=current-16
 assert len(actors)<=5 and len(ys)<=12 and max(ys)<=932
 c.text(40,48,'E-COMMERCE / PROPOSED TEMPORAL INTERACTION / NATIVE BOUNDARY GROUPS',8,g.MONO,g.SOFT,500);c.text(40,88,d['title'],32,g.SERIF,g.INK);c.text(40,116,'Time flows down. Header nesting shows ownership; each lifeline represents the named interaction boundary.',12)
 if d['slug']=='outbox-delivery-sequence':c.text(40,140,'PRECONDITION: checkout committed WAIT_PAYMENT + stock/budget reservations + outbox intent together. Payment success is a later event.',10)
 if frag:
  subset={k for m in d['messages'][frag['start']:frag['end']] for k in [m['src'],m['dst']]};left=min(xs[k] for k in subset)-24;right=max(xs[k] for k in subset)+24
  group('alt',left,frame['top'],right-left,frame['bottom']-frame['top'],fill='#f1f1f1',stroke='#bfc0c0')
  c.rect(left,frame['top'],40,16,rx=2);c.text(left+20,frame['top']+12,frag.get('operator','ALT'),8,g.MONO,g.SOFT,anchor='middle');c.text(left+12,frame['guard1'],'['+frag['guards'][0]+']',8,g.MONO,g.SOFT)
  if 'divider' in frame:
   c.path([(left+8,frame['divider']),(right-8,frame['divider'])],color='#bfc0c0',dash=True,marker=None,width=.8);c.text(left+12,frame['guard2'],'['+frag['guards'][1]+']',8,g.MONO,g.SOFT)
 categories={'api':'BACKEND REQUEST BOUNDARY','sql':'AUTHORITATIVE DATA BOUNDARY','mongo':'DOCUMENT DATA BOUNDARY','redis':'ADMISSION STORE BOUNDARY','relay':'BACKGROUND WORKER BOUNDARY','stripe':'EXTERNAL PROVIDER','instances':'APPLICATION RUNTIME','customer':'CUSTOMER / CALLER','admin':'PLATFORM ADMINISTRATOR','operator':'SHOP / ADMIN CALLER'}
 detail={'sql':['SQL transaction / locks','Receipt / intent / outbox'],'mongo':['Validated config / events','Local TX / majority outcome'],'redis':['Atomic token buckets','Independent memory budget'],'relay':['Lease / retry / ACK','No business-operation replay'],'stripe':['Provider side effects','Independent durable state'],'instances':['Snapshot provider','Immutable local LKG']}
 scenario_sql={
 'checkout-sequence':['Orders / lots / budgets','Source transaction + outbox'],
 'start-payment-sequence':['Order guard / durable operation','Stable provider identity'],
 'payment-webhook-sequence':['Durable receipt / event identity','Guarded order/payment effects'],
 'refund-sequence':['Refund operation / order guard','Once-only stock/budget release'],
 'outbox-delivery-sequence':['Publication state / lease','Fenced claim / ACK'],
 'config-publication-sequence':['Current SQL permission check','No config authorization grant']}
 detail['sql']=scenario_sql[d['slug']]
 if d['slug']=='outbox-delivery-sequence':detail['mongo']=['Event marker + full projection','Related audit / majority TX']
 if d['slug']=='config-publication-sequence':detail['mongo']=['Current + revision + audit','Validated publication TX']
 if d['slug']=='payment-webhook-sequence':categories['api']='BACKEND SERVICE BOUNDARY'
 for key,name,tag in actors:
  x=xs[key];focal=key=='api' or ('api' not in xs and key=='relay');col=g.ACCENT if focal else g.SOFT
  c.path([(x,336),(x,944)],color='#bfc0c0',dash=True,marker=None,width=.8)
  group('boundary-'+key,x-120,160,240,176,fill='#f1e7e4' if focal else '#f0f0f1',stroke=col)
  c.text(x,180,categories[key],8,g.MONO,g.SOFT,anchor='middle');c.text(x,200,name,12,g.SANS,g.INK,600,'middle')
  if key=='api':
   group('application-'+key,x-108,212,216,112,'boundary-'+key,fill=g.PAPER,stroke=g.SOFT)
   c.text(x,228,'Application coordination',9,g.SANS,g.INK,600,'middle')
   for j,label in enumerate(['Command / Query','Validator / policy guard','Handler / transaction ports']):
    group(f'role-{key}-{j}',x-96,236+j*28,192,24,'application-'+key,fill='#ffffff',stroke='#bfc0c0');c.text(x,252+j*28,label,10,g.SANS,g.MUTED,anchor='middle')
  else:
   group('participant-'+key,x-108,212,216,112,'boundary-'+key,fill='#ffffff',stroke='#bfc0c0');c.text(x,232,tag,8,g.MONO,g.SOFT,anchor='middle')
   lines=detail.get(key,['External request / response','No direct data-store access'])
   for j,line in enumerate(lines):c.text(x,260+j*24,line,11,g.SANS,g.MUTED,anchor='middle')
 activation={}
 for i,m in enumerate(d['messages']):
  if m['kind'] not in ['return','success'] or m['reply'] is None:continue
  start=m['reply'];who=d['messages'][start]['dst'];activation[(who,ys[start])]=max(activation.get((who,ys[start]),0),ys[i]+8)
 if d['slug']=='checkout-sequence':activation[('sql',ys[3])]=ys[6]+8;activation.pop(('sql',ys[5]),None)
 for (who,start),end in activation.items():c.rect(xs[who]-4,start,8,end-start,fill='#e4e6e8',stroke=g.MUTED,rx=0)
 for i,(m,y) in enumerate(zip(d['messages'],ys)):
  a,b=xs[m['src']],xs[m['dst']];sign=1 if b>a else -1;marker='open' if m['kind']=='async' else 'accent' if m['kind']=='success' else 'arrow';color=g.ACCENT if m['kind']=='success' else g.MUTED
  c.path([(a+4*sign,y),(b-4*sign,y)],color=color,dash=m['kind'] in ['return','async'],marker=marker)
  gaps=[(p+q)/2 for p,q in zip(positions,positions[1:]) if min(a,b)<=p and q<=max(a,b)];cx=min(gaps,key=lambda x:abs(x-(a+b)/2));label=(cx,y-16,m['label']);x,ly,w,h=g.label_box(label)
  assert len(m['label'])<=14 and all(not(x-3<px<x+w+3) for px in positions)
  c.rect(x,ly,w,h,stroke=g.PAPER,rx=2);c.text(cx,y-11,m['label'],8,g.MONO,g.SOFT,anchor='middle');c.text(40,y+3,f'{i+1:02d}',9,g.MONO,g.SOFT)
  detail=m['detail'];dw=math.ceil((len(detail)*9*.56+12)/4)*4;assert dw<=min(q-p for p,q in zip(positions,positions[1:]))-16
  c.rect(cx-dw/2,y+8,dw,14,stroke=g.PAPER,rx=2);c.text(cx,y+19,detail,9,g.SANS,g.MUTED,anchor='middle')
 c.text(40,964,'Header nesting shows ownership. Each lifeline is one interaction boundary; child boxes are structural context, not extra timings.',10)
 for i,note in enumerate(d['notes']):c.text(40,988+i*20,note,10)
 c.text(40,1036,'Sources: linked spec.md + sequence.wsd, diagram-semantics.md and supporting research | Proposed coordination; exact SQL remains in API sequences.',9,g.MONO,g.SOFT)
 c.path([(40,1052),(1544,1052)],color='#bfc0c0',marker=None,width=.8)
 for x,label in [(40,'Solid = synchronous call'),(336,'Dashed filled = return'),(632,'Dashed open = async hint'),(928,('Time flows downward' if not frag else 'OPT = guarded path' if frag.get('operator')=='OPT' else 'ALT = mutually exclusive')),(1224,'Header boxes = ownership')]:c.text(x,1076,label,9)
 html,xml=c.render();mx=ET.fromstring(xml);root=mx.find('./diagram/mxGraphModel/root');cells={cell.get('id'):cell for cell in root.findall('mxCell')};group_cells={}
 for i,o in enumerate(c.ops):
  if o['k']=='rect' and o.get('group'):
   key=o['group'];cell=cells[f'op-{i}'];group_cells[key]=cell;cell.set('id','group-'+key);cell.set('style',cell.get('style')+'container=1;collapsible=0;recursiveResize=0;')
 for key,cell in group_cells.items():
  info=groups[key];p=info.get('parent')
  if p:
   cell.set('parent','group-'+p);geo=cell.find('mxGeometry');geo.set('x',str(info['x']-groups[p]['x']));geo.set('y',str(info['y']-groups[p]['y']))
 for i,o in enumerate(c.ops):
  if o['k']=='rect' and o.get('group'):continue
  cell=cells[f'op-{i}'];geo=cell.find('mxGeometry')
  if o['k']=='path':
   pts=o['points'];rect=(min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts)-min(x for x,y in pts),max(y for x,y in pts)-min(y for x,y in pts))
  else:rect=(float(geo.get('x')),float(geo.get('y')),float(geo.get('width')),float(geo.get('height')))
  x,y,w,h=rect;eligible=[(key,v) for key,v in groups.items() if x>=v['x'] and y>=v['y'] and x+w<=v['x']+v['w'] and y+h<=v['y']+v['h']]
  if not eligible:continue
  key,v=min(eligible,key=lambda kv:kv[1]['w']*kv[1]['h']);cell.set('parent','group-'+key)
  if o['k']=='path':
   for point in geo.iter('mxPoint'):point.set('x',str(float(point.get('x'))-v['x']));point.set('y',str(float(point.get('y'))-v['y']))
  else:geo.set('x',str(float(geo.get('x'))-v['x']));geo.set('y',str(float(geo.get('y'))-v['y']))
 ET.indent(mx,space='  ')
 print(f'PASS {d["slug"]}: temporal lifelines/fragments + {len(groups)} real native ownership groups; {len(ys)} messages')
 return html,ET.tostring(mx,encoding='unicode',xml_declaration=True)+'\n'
