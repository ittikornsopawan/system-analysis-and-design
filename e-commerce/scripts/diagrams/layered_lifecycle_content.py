"""Order and publication states with explicit guard/effect compartments, not invented substates."""
from diagram_content import box,row,link
from supporting_content import vl


def container(key,x,y,w,h,title,tag,kind='state',parent=None):
 return dict(id=key,x=x,y=y,w=w,h=h,title=title,tag=tag,kind=kind,parent=parent)


def compartment(key,parent,x,y,w,h,title,rows):
 n=box(key,x,y,w,h,title,'',list(map(row,rows)))
 n.update(parent=parent,compact=True,role='state-compartment');return n

SYSTEM=dict(slug='order-lifecycle',title='Order lifecycle · guards and effects',type='State Machine',eyebrow='E-COMMERCE / BUSINESS STATE VIEW',subtitle='Six order states. Small internal boxes describe guards/effects; they are not additional persisted states.',desc='Order states with actor guards, transactional effects, retry, guarded recovery and alternative terminal outcomes.',containers=[
 container('wait',40,320,336,280,'WAIT_PAYMENT','AWAITING PAYMENT'),container('paid',432,320,336,280,'PAYMENT_CONFIRMED','PAID / NOT YET FULFILLED'),container('processing',824,320,336,280,'PROCESSING','FULFILMENT STARTED'),container('complete',1208,320,336,280,'COMPLETED','DELIVERED / TERMINAL','focal'),container('cancel',40,768,336,240,'CANCELLED','UNPAID / TERMINAL'),container('refund',432,768,336,240,'REFUNDED','PAID / TERMINAL')],nodes=[
 compartment('wait-guard','wait',56,368,304,80,'ENTRY / ACTOR',['Customer-owned cart/address','Live lot/visibility/budget checks']),
 compartment('wait-effect','wait',56,472,304,112,'ATOMIC SQL EFFECT',['Snapshot price and address','Reserve stock + campaign budget','Delete selected cart lines','30-minute default payment window']),
 compartment('paid-guard','paid',448,368,304,80,'EVENT / GUARD',['Signed provider success','Order still WAIT_PAYMENT']),
 compartment('paid-effect','paid',448,472,304,112,'SQL EFFECT / INVARIANT',['Payment COMPLETED; order paid','Reserved stock is still held','Browser is not payment truth','Full refund possible before shipping']),
 compartment('processing-guard','processing',840,368,304,80,'ENTRY / QUANTITY GUARD',['Shop/admin creates first parcel','Assigned qty never exceeds item qty']),
 compartment('processing-effect','processing',840,472,304,112,'FULFILMENT EFFECT',['Several parcels; first is PENDING','Shop records SHIPPED + tracking','Owner confirms delivery','No-live-parcel recovery is guarded']),
 compartment('complete-guard','complete',1224,368,304,80,'RECEIVER / SYSTEM GATE',['All active items fully delivered','Or eligible guarded 7-day job']),
 compartment('complete-effect','complete',1224,472,304,112,'COMPLETION EFFECT',['No PENDING; full quantity allocated','All remaining SHIPPED aged >=7d','Partial shipments never auto-close','Enable review; no budget release']),
 compartment('cancel-guard','cancel',56,816,304,64,'GUARD',['Only WAIT_PAYMENT; no processing money']),
 compartment('cancel-effect','cancel',56,904,304,88,'EFFECT / IDEMPOTENCY',['Cancel pending intent; keep history','Restore original lots and budget once','Repeated cancel -> 409, no release']),
 compartment('refund-guard','refund',448,816,304,64,'GUARD',['Paid before shipping; full refund rules']),
 compartment('refund-effect','refund',448,904,304,88,'EFFECT / IDEMPOTENCY',['Restore original lots and budget once','Late money never releases them twice','Post-shipping refunds need follow-up'])

],edges=[
 link(None,'wait',[(62,208),(107.2,208),(107.2,320)],(84,192,'CREATE')),
 link('wait','paid',[(376,460),(432,460)],(404,444,'PAID')),
 link('paid','processing',[(768,460),(824,460)],(796,444,'SHIP')),
 link('processing','complete',[(1160,460),(1208,460)],(1184,444,'DONE')),
 link('wait','cancel',[(208,600),(208,768)],vl(208,680,'EXPIRE/CANCEL')),
 link('paid','refund',[(600,600),(600,768)],vl(600,680,'REFUND')),
 link('processing','paid',[(992,320),(992,232),(600,232),(600,320)],(796,216,'NO LIVE PARCEL'),dashed=True),
 link('wait','wait',[(241.6,320),(241.6,264),(308.8,264),(308.8,320)],(275.2,248,'RETRY'),dashed=True)
],notes=[(40,176,'Read transitions as event + guard + effect. Payment and parcel statuses are separate entities.',12,'body'),(824,680,'PAID = signed success; SHIP = first parcel; DONE = all delivered under the applicable gate.',10,'body'),(824,816,'Business lifecycle only',12,'heading'),(824,848,'Payment attempts and parcels have separate statuses.',11,'body'),(824,876,'Publication READY / CLAIMED / DELIVERED are not Order states.',11,'body'),(824,904,'Delivery controls: event-outbox-design + outbox-delivery-sequence.',11,'body'),(824,932,'Runtime components and adapters: architecture-design.',11,'body')],source='SPEC: sales/02,05; payment/01,02,05; shipping/01,02,06 | Provider gaps: supporting-payments-research.md',legend=[('state','Persisted order state'),('box','Guard/effect compartment'),('focal','Successful terminal'),('dashed','Retry / recovery'),('text','Provider recovery additions remain proposed')],start=(56,208))

OUTBOX=dict(slug='event-outbox-design',title='Publication lifecycle · delivery control',type='State Machine',eyebrow='E-COMMERCE / PROPOSED DELIVERY STATE VIEW',subtitle='Publication states are separate from order/payment states. Each state exposes its durable data and allowed effects.',desc='Proposed publication lifecycle with claim leases, destination commit, retry, quarantine and immutable event identity.',containers=[
 container('ready',40,328,280,248,'READY','COMMITTED PUBLICATION'),container('claimed',392,328,320,248,'CLAIMED','LEASE OWNED'),container('delivered',784,328,320,248,'DELIVERED','DESTINATION COMMIT + ACK','focal'),container('retry',392,760,320,248,'RETRY_WAIT','TRANSIENT / AMBIGUOUS'),container('quarantine',784,760,320,248,'QUARANTINED','MANUAL REVIEW'),container('envelope',1160,328,384,384,'Event envelope','CONTRACT COMPARTMENTS / NOT A STATE','policy')],nodes=[
 dict(box('checkout-source',40,208,560,96,'Checkout transaction · PostgreSQL','SPEC CHECKOUT + PROPOSED OUTBOX INTENT',[row('Create WAIT_PAYMENT; reserve stock + campaign budget'),row('Persist related records + outbox intent; commit all together')],'input')),
 compartment('ready-data','ready',56,376,248,80,'IMMUTABLE IDENTITY',['eventId / payloadHash','sourceEpoch + aggregateVersion']),compartment('ready-gate','ready',56,480,248,80,'ELIGIBILITY',['SQL source and intent committed','availableAt reached; no business retry']),
 compartment('claimed-data','claimed',408,376,288,80,'DURABLE LEASE',['leaseOwner / token / leaseUntil','Short claim TX; then release SQL lock']),compartment('claimed-work','claimed',408,480,288,80,'DESTINATION WORK',['Bounded worker batch and concurrency','Network deadline is not rollback']),
 compartment('delivered-proof','delivered',800,376,288,80,'DESTINATION ATOMICITY',['Mongo marker + projection + audit','Majority outcome confirmed']),compartment('delivered-ack','delivered',800,480,288,80,'SOURCE ACK',['SQL ACK guarded by current lease','Lost ACK may replay the same event']),
 compartment('retry-policy','retry',408,808,288,80,'RETRY POLICY',['Same event ID and immutable payload','Backoff + jitter; no second charge']),compartment('retry-gate','retry',408,912,288,80,'RECLAIM GATE',['Expired lease may be reclaimed','Old owner cannot ACK the new claim']),
 compartment('quarantine-data','quarantine',800,808,288,80,'WHY HELD',['Unsupported schema / poison event','Same ID with different hash']),compartment('quarantine-action','quarantine',800,912,288,80,'OPERATOR REVIEW REQUIRED',['Review + authorize; audit disposition','Only then controlled replay','Same event ID / hash; no checkout']),
 compartment('identity','envelope',1176,376,352,80,'IDENTITY',['Globally unique eventId','Immutable payload fingerprint']),compartment('envelope-source','envelope',1176,480,352,80,'SOURCE / VERSION',['sourceEpoch + aggregate identity','Per-aggregate version + schemaVersion']),compartment('payload','envelope',1176,584,352,112,'PAYLOAD / OBSERVABILITY',['Allowlisted complete status snapshot','occurredAt / correlationId','No raw secrets, card data or full PII','New recovery snapshots get new IDs'])
],edges=[
 link('checkout-source','ready',[(180,304),(180,328)],vl(180,312,'COMMIT')),
 link('ready','claimed',[(320,452),(392,452)],(356,436,'CLAIM')),
 link('claimed','delivered',[(712,452),(784,452)],(748,436,'ACK')),
 link('claimed','retry',[(498.6667,576),(498.6667,672),(552,672),(552,760)],vl(552,712,'RETRY'),dashed=True),
 link('claimed','quarantine',[(605.3333,576),(605.3333,640),(944,640),(944,760)],(776,624,'POISON'),dashed=True),
 link('retry','ready',[(392,884),(344,884),(344,616),(180,616),(180,576)],(260,600,'DUE'),dashed=True),
 link('claimed','claimed',[(712,410),(744,410),(744,312),(680,312),(680,328)],(712,296,'LEASE EXPIRED'),dashed=True)
],notes=[(40,176,'At-least-once delivery with idempotent effects; no cross-store exactly-once guarantee.',12,'body'),(1160,760,'Quarantine stops automatic retry.',11,'body'),(1160,788,'Operator review before controlled replay.',11,'body'),(1160,836,'Payment success is a later event.',11,'body'),(1160,864,'Replay never reruns checkout,',11,'body'),(1160,888,'stock or budget reservations.',11,'body')],source='PROPOSED: mongodb-design.md; supporting-data-operations-research.md | No collection, outbox table or worker implemented',legend=[('state','Durable publication state'),('box','State data / effect'),('focal','Delivery proof'),('dashed','Retry / exceptional transition'),('text','Guarded destination effects tolerate replay')])
LIFECYCLES=[SYSTEM,OUTBOX]
