"""Reviewed semantic inputs for the supporting design package; all new controls are proposals."""
from diagram_content import box, row, link, MONO


def base(slug,title,kind,nodes,edges,notes=(),zones=(),source='Project specs + supporting research | PROPOSED additions; no backend implementation'):
    return dict(slug=slug,title=title,type=kind,pattern=None,eyebrow='E-COMMERCE / SUPPORTING DESIGN / REVIEW PROPOSAL',subtitle='Current commerce specifications with explicit proposed consistency, deployment and operating controls.',desc=title+'. Proposed controls are separated from specified business behavior.',nodes=nodes,edges=edges,notes=list(notes),zones=list(zones),source=source,legend=[('box','Specified responsibility'),('focal','Design focus'),('optional','Proposed control'),('arrow','Directed relationship'),('text','Detailed policy approval pending')])


def vl(x,y,text):
    import math
    w=math.ceil((len(text)*8*.62+16)/4)*4
    return (x+8+w/2,y,text)


OVERVIEW=base('commerce-overview','Commerce capabilities & ownership','Architecture',[
 box('access',40,224,320,208,'Access & identity','CODE SUBSET / SPEC POLICY',[row('Guest browse or verified principal'),row('Authen: five implemented use cases'),row('SQL session / permission authority'),row('Shop membership and PLATFORM_ADMIN'),row('Config flags never grant permission')]),
 box('catalog',448,224,320,208,'Catalog, shop & inventory','SPEC',[row('Product / category / brand / options'),row('Shop listing / SKU / original lots'),row('Live eligibility, price and stock'),row('PROPOSED: public-text Redis cache'),row('Shop owners manage their inventory')]),
 box('cart',856,224,280,208,'Cart selection','SPEC',[row('Customer-owned cart lines'),row('Current availability is recalculated'),row('Selected items / owned address'),row('Checkout rejects unavailable lines')]),
 box('checkout',1224,224,320,208,'Checkout & campaigns','SPEC + PROPOSED OUTBOX',[row('One order per selected shop'),row('Reserve lots + discount budget'),row('Snapshot price/address in SQL'),row('All selected orders commit together'),row('PROPOSED: publication intent')],'focal'),
 box('payment',1224,672,320,224,'Payment & refund','SPEC / PROVIDER GAPS',[row('Stripe intent / signed events'),row('SQL order/payment state guards'),row('PROPOSED: durable operation identity'),row('Reconcile uncertain provider effects'),row('Full settled refund before restock'),row('Never settle using MongoDB copies')]),
 box('fulfilment',856,672,280,224,'Shipping & completion','SPEC',[row('Several parcels / quantity guards'),row('Shop enters carrier/tracking'),row('Receiver confirms delivered'),row('Guarded 7-day system completion'),row('Partial shipment never auto-closes')]),
 box('review',448,672,320,224,'Purchase & review history','SPEC',[row('Completed purchase enables review'),row('History stays in PostgreSQL'),row('PROPOSED: MongoDB status copies'),row('Operational search is restricted'),row('Derived data can lag its source')]),
 box('operations',40,672,320,224,'Platform operations','SPEC + PROPOSED',[row('Master data / roles / campaigns'),row('MongoDB config revisions + audit'),row('Cache/rate policies via snapshots'),row('Outbox lag / alerts / recovery'),row('Retention and targets need approval')],'optional')
],[
 link('access','catalog',[(360,328),(448,328)],(404,312,'BROWSE')),
 link('catalog','cart',[(768,328),(856,328)],(812,312,'SELECT')),
 link('cart','checkout',[(1136,328),(1224,328)],(1180,312,'CHECKOUT')),
 link('checkout','payment',[(1384,432),(1384,672)],vl(1384,544,'PAY')),
 link('payment','fulfilment',[(1224,784),(1136,784)],(1180,768,'FULFIL')),
 link('fulfilment','review',[(856,784),(768,784)],(812,768,'REVIEW')),
],[(40,176,'Customer journey is a capability map, not a mandatory login gate or a deployment topology.',12,'body'),(40,520,'Cross-cutting authority',14,'heading'),(40,552,'PostgreSQL: business truth. Redis: rebuildable metadata + shared admission. MongoDB: config + derived documents.',12,'body'),(40,584,'Platform operations govern the journey; no broker, carrier API or separate microservice is assumed.',12,'body'),(40,960,'Existing endpoint specs remain authoritative; new provider recovery and data-service controls stay in review.',11,'body')])

OUTBOX=base('event-outbox-design','Publication lifecycle & delivery guarantees','State Machine',[
 box('ready',40,360,280,176,'READY','PROPOSED PUBLICATION STATE',[row('SQL business + intent committed'),row('Stable eventId / immutable payload'),row('sourceEpoch + aggregateVersion'),row('Eligible when availableAt <= now')]),
 box('claimed',440,360,280,176,'CLAIMED','SHORT SQL CLAIM TX',[row('leaseOwner / leaseToken / leaseUntil'),row('Release SQL lock before network I/O'),row('Bound batch and per-tenant work'),row('Destination write can be ambiguous')]),
 box('delivered',840,360,280,176,'DELIVERED','ACK AFTER DESTINATION COMMIT',[row('MongoDB majority transaction'),row('Event marker + projection + audit'),row('SQL ACK guarded by lease token'),row('Duplicate replay has no new effect')],'focal'),
 box('retry',440,744,280,176,'RETRY_WAIT','TRANSIENT / AMBIGUOUS',[row('Bound exponential delay + jitter'),row('Same eventId and payload on retry'),row('No second business mutation'),row('Lease expiry allows safe reclaim')],'optional'),
 box('quarantine',840,744,280,176,'QUARANTINED','SCHEMA / IDENTITY CONFLICT',[row('Unsupported version or poison event'),row('Same ID with another hash is unsafe'),row('Operator review + audited replay'),row('Never silently discard evidence')],'optional')
],[
 link(None,'ready',[(62,248),(180,248),(180,360)],(120,232,'SQL COMMIT')),
 link('ready','claimed',[(320,448),(440,448)],(380,432,'CLAIM')),
 link('claimed','delivered',[(720,360+176*2/3),(840,360+176*2/3)],(780,360+176*2/3-16,'COMMIT + ACK')),
 link('claimed','retry',[(440+280/3,536),(440+280/3,640),(580,640),(580,744)],vl(580,688,'RETRY'),dashed=True),
 link('claimed','quarantine',[(440+560/3,536),(440+560/3,616),(980,616),(980,744)],(804,600,'POISON'),dashed=True),
 link('retry','ready',[(440,832),(340,832),(340,576),(180,576),(180,536)],(260,560,'DUE'),dashed=True),
 link('claimed','claimed',[(580,360),(580,288),(752,288),(752,360+176/3),(720,360+176/3)],(664,272,'LEASE EXPIRED'),dashed=True)
],[(40,176,'This is a delivery-state proposal, not a new order/payment status or a deployed queue.',12,'body'),(1176,376,'Contract envelope',14,'heading'),(1176,408,'eventId / eventType / schemaVersion',9,'mono'),(1176,432,'sourceEpoch / aggregateId / version',9,'mono'),(1176,456,'occurredAt / correlationId',9,'mono'),(1176,480,'payloadHash / allowlisted snapshot',9,'mono'),(1176,520,'At-least-once delivery.',12,'body'),(1176,544,'Idempotent destination effects.',12,'body'),(1176,568,'No cross-store exactly-once claim.',12,'body'),(40,968,'ACK loss or lease races may repeat delivery; MongoDB uniqueness/version guards must absorb replay.',11,'body')]);OUTBOX['start']=(56,248)

MODEL=base('mongodb-document-model','MongoDB document ownership & references','ER',[
 box('current',40,232,448,208,'runtime_config_current','PROPOSED CONFIG AUTHORITY',[row('# environment + scope + key',MONO),row('schemaVersion / revision / effectiveAt',MONO),row('validated typed value / publishedBy',MONO),row('CAS expectedRevision; no secrets'),row('Unique canonical identity; majority writes')],'focal'),
 box('revisions',608,232,448,208,'runtime_config_revisions','IMMUTABLE PUBLISHED HISTORY',[row('# config identity + revision',MONO),row('value / publishedAt / actorId',MONO),row('rollbackFromRevision / payloadHash',MONO),row('Rollback publishes a new revision'),row('Never overwrite prior history')]),
 box('audit',1176,232,368,240,'application_audit_events','RESTRICTED APPEND EVIDENCE',[row('# eventId',MONO),row('configRef or sourceRef / actorId',MONO),row('action / occurredAt / correlationId',MONO),row('Minimized allowlisted payload'),row('Not a certified immutable ledger'),row('Backup + retention explicitly required')]),
 box('events',40,680,448,256,'integration_events','DELIVERY MARKER + ENVELOPE',[row('# eventId; unique',MONO),row('payloadHash / schemaVersion / eventType',MONO),row('sourceEpoch / aggregateId / version',MONO),row('occurredAt / receivedAt / correlationId',MONO),row('Same ID / different hash -> quarantine'),row('Marker + effect commit in MongoDB TX'),row('Out-of-order history is retained')],'optional'),
 box('projection',728,680,816,256,'transaction_status_projections','DERIVED CURRENT SNAPSHOT',[row('# sourceEpoch + aggregateType + aggregateId',MONO),row('sourceVersion / sourceOccurredAt / projectedAt / schemaVersion',MONO),row('status + allowed references; restricted operational/admin read',MONO),row('Atomic newer-version replacement; full snapshot rather than unordered deltas'),row('Epoch changes after SQL restore; old timeline cannot remain authoritative'),row('Audit/event history is not reconstructed completely from a current snapshot'),row('No automatic TTL until collection-specific retention is approved')],'optional')
],[link('current','revisions',[(488,336),(608,336)],(548,320,'REVISIONS')),link('revisions','audit',[(1056,336),(1176,336)],(1116,320,'PUBLISH AUDIT')),link('events','projection',[(488,808),(728,808)],(608,792,'APPLIES'))],[(40,176,'Logical references and cardinality only; MongoDB does not enforce these as PostgreSQL foreign keys.',12,'body'),(40,520,'Two independent local transactions',14,'heading'),(40,552,'Config: current + revision + audit. Delivery: event marker + conditional projection + related audit.',12,'body'),(40,584,'Both need a supported replica set/sharded topology; neither includes PostgreSQL in the transaction.',12,'body'),(40,976,'Candidate indexes and validation are specified in the companion; no collection or index is provisioned here.',11,'body')]);MODEL['cardinality']=[(500,328,'1'),(592,328,'N'),(1068,328,'1'),(1152,328,'0..N'),(500,800,'N'),(700,800,'0..1')]

DEPLOY=base('deployment-security','Candidate deployment & security boundaries','Deployment',[
 box('api',368,208,400,176,'API host pool','APP HOST POOL',[row('PROPOSED x2 stateless instances'),row('JWT / SQL permissions / admission'),row('Trusted ingress; HTTPS 443'),row('Separate service credentials')],'focal'),
 box('worker',368,768,400,176,'Background worker pool','WORKER HOST POOL',[row('PROPOSED x1 scheduling/relay pool'),row('Expiry / 7-day completion / outbox'),row('Durable leases, no shared process lock'),row('Per-role health; bounded concurrency')],'optional'),
 box('pg',40,488,288,208,'PostgreSQL nodes','PRIVATE DB HOSTS',[row('PROPOSED primary + standby'),row('Business state + outbox intent'),row('TLS 5432 / narrow SQL roles'),row('Backup / restore to tested point'),row('Replication is not a backup')],'store'),
 box('mongo',840,488,288,208,'MongoDB replica set','PRIVATE DB HOSTS',[row('PROPOSED three members'),row('Config + events + projections'),row('TLS 27017 / majority + TX'),row('Separate reader/publisher/writer'),row('Not publicly reachable')],'store'),
 box('cache',1200,208,344,176,'Redis cache service','PRIVATE CACHE HOST',[row('PROPOSED x1; cache loss tolerated'),row('allkeys-lfu; independent memory'),row('TLS 6379; cache-only ACL'),row('Failure bypasses to guarded SQL')],'optional'),
 box('rate',1200,768,344,176,'Redis admission service','PRIVATE RATE HOSTS',[row('PROPOSED primary + replica'),row('noeviction; isolated budget'),row('TLS 6379; limiter-only ACL'),row('Failover can lose counter updates')],'optional')
],[
 link('api','pg',[(368,296),(184,296),(184,488)],(276,280,'TLS:5432')),
 link('worker','pg',[(368,856),(184,856),(184,696)],(276,840,'TLS:5432'),dashed=True),
 link('api','mongo',[(568,384),(568,440),(984,440),(984,488)],(776,424,'TLS:27017')),
 link('worker','mongo',[(568,768),(568,728),(984,728),(984,696)],(776,712,'TLS:27017'),dashed=True),
 link('api','cache',[(768,208+176/3),(1200,208+176/3)],(984,208+176/3-16,'TLS:6379')),
 link('api','rate',[(768,208+352/3),(1152,208+352/3),(1152,856),(1200,856)],vl(1152,576,'TLS:6379'))
],[(40,960,'Ingress and provider HTTPS paths use the main runtime diagram; data/admin ports are denied from the public network.',11,'body'),(40,984,'Reference topology only. No provider, cluster, image or network is deployed by this design.',11,'body')],[(24,144,1536,864,'PROPOSED PRIVATE PRODUCTION / SELF-HOSTED REFERENCE PLACEMENT','system'),(344,176,448,800,'APPLICATION WORKLOAD PLACEMENT','application')]);DEPLOY['artifacts']={'api':('Ecommerce.Api','releaseSha'),'worker':('worker responsibilities','releaseSha'),'pg':('PostgreSQL','pinned supported major'),'mongo':('MongoDB','pinned supported major'),'cache':('Redis cache','pinned supported release'),'rate':('Redis rate','pinned supported release')};DEPLOY['replicas']={'api':'x2','worker':'x1','pg':'x2','mongo':'x3','cache':'x1','rate':'x2'}

OBSERVE=base('observability-design','Signals, service objectives & response','Architecture',[
 box('api',40,224,400,176,'API & worker instrumentation','PROPOSED BUSINESS SIGNALS',[row('Request rate / errors / latency'),row('Checkout success / webhook age'),row('TraceId + operationId + eventId'),row('Redact PII, secrets and card data')]),
 box('sql',592,224,400,176,'PostgreSQL & outbox signals','PROPOSED SOURCE HEALTH',[row('Pool wait / lock waits / deadlocks'),row('Oldest READY / RETRY age + count'),row('Claim expiry / duplicate effects'),row('Backup age + restore proof')]),
 box('data',1144,224,400,176,'Redis / MongoDB signals','PROPOSED DERIVED HEALTH',[row('Cache hit / refill / invalidation'),row('Rate deny vs store unavailable'),row('Memory / key count / config age'),row('Projection lag / version / epoch')]),
 box('collect',592,544,400,176,'Telemetry collection','PROPOSED OPEN STANDARD',[row('Metrics + traces + structured logs'),row('Bound labels; sample traces'),row('Separate low-cardinality metrics'),row('No user/event IDs as metric labels')],'focal'),
 box('dashboard',40,840,512,160,'Flow dashboards & SLOs','PROPOSED TARGETS',[row('Availability, latency and correctness'),row('Normal load vs burst vs degraded mode'),row('Dependency health is not business success')]),
 box('respond',1032,840,512,160,'Alert owner & runbook','PROPOSED OPERATIONS',[row('Impact + sustained error/lag thresholds'),row('Named operator / escalation / evidence'),row('Contain, reconcile, recover and review')],'optional')
],[
 link('api','collect',[(240,400),(240,480),(692,480),(692,544)],(466,464,'SIGNALS'),dashed=True),
 link('sql','collect',[(792,400),(792,544)],vl(792,448,'SIGNALS'),dashed=True),
 link('data','collect',[(1344,400),(1344,480),(892,480),(892,544)],(1118,464,'SIGNALS'),dashed=True),
 link('collect','dashboard',[(592+400/3,720),(592+400/3,776),(296,776),(296,840)],(510,760,'SLI')),
 link('collect','respond',[(592+800/3,720),(592+800/3,800),(1288,800),(1288,840)],(1074,784,'ALERTS'))
],[(40,176,'A healthy database is insufficient: measure the customer flow, source truth and delivery correctness together.',12,'body'),(40,648,'Test the proposed targets',14,'heading'),(40,680,'Baseline / spike / cold cache',11,'body'),(40,704,'NAT / memory / failover / replay',11,'body'),(40,728,'Every number requires measured evidence.',11,'body')])

RECOVERY=base('recovery-design','Recovery checkpoints & safe reopening','State Machine',[
 box('incident',40,240,320,192,'INCIDENT DETECTED','PROPOSED RECOVERY CHECKPOINT',[row('Impact + scope + incident owner'),row('Preserve logs / IDs / backup points'),row('Declare recovery under agreed RTO'),row('Do not guess a healthy timeline')]),
 box('contain',448,240,320,192,'WRITES CONTAINED','PROPOSED FENCING',[row('Pause unsafe writes + old relays'),row('Fence old worker credentials/epoch'),row('Keep evidence and payment callbacks'),row('Select coherent restore points')]),
 box('restore',856,240,280,192,'AUTHORITY RESTORED','PROPOSED RESTORE',[row('PostgreSQL business + outbox'),row('MongoDB config + audit backup'),row('Recovery epoch is explicitly new'),row('Restore does not undo Stripe')]),
 box('verify',1224,240,320,192,'INTEGRITY VERIFIED','PROPOSED REOPEN GATE',[row('SQL constraints + source versions'),row('Provider money reconciliation'),row('Config authorization / revision'),row('No unresolved financial mismatch')]),
 box('quarantine',448,704,320,192,'RECOVERY QUARANTINED','PROPOSED MANUAL GATE',[row('Keep uncertain writes disabled'),row('Investigate timeline or money gap'),row('Restore/reconcile again with owner'),row('Record every manual correction')],'optional'),
 box('rebuild',856,704,280,192,'DERIVED REBUILT','PROPOSED REPLAY',[row('New-epoch transaction snapshots'),row('Replay retained events safely'),row('Cold Redis cache; bounded refill'),row('Audit history needs its own backup')]),
 box('resume',1224,704,320,192,'SERVICE RESUMED','PROPOSED APPROVAL GATE',[row('Smoke + load + invariant checks'),row('Known data-loss window accepted'),row('Operator approval + watch period'),row('Capture measured RPO / RTO')],'focal')
],[
 link('incident','contain',[(360,336),(448,336)],(404,320,'CONTAIN')),
 link('contain','restore',[(768,336),(856,336)],(812,320,'RESTORE')),
 link('restore','verify',[(1136,336),(1224,336)],(1180,320,'VERIFY')),
 link('verify','rebuild',[(1224+640/3,432),(1224+640/3,560),(996,560),(996,704)],(1190,544,'PASS')),
 link('verify','quarantine',[(1224+320/3,432),(1224+320/3,512),(608,512),(608,704)],(968,496,'FAIL'),dashed=True),
 link('quarantine','contain',[(448,800),(400,800),(400,464),(608,464),(608,432)],(504,448,'RECONCILE'),dashed=True),
 link('rebuild','resume',[(1136,800),(1224,800)],(1180,784,'REOPEN'))
],[(40,176,'Operational checkpoints, not new persisted order states. All timings are untested targets for review.',12,'body'),(40,968,'After SQL restore, MongoDB may be ahead: fence old writers and rebuild under a new sourceEpoch before trusting copies.',11,'body'),(40,992,'Replication is not backup; projections cannot recreate missing historical audit or reverse provider payments.',11,'body')])

SHEETS=[OVERVIEW,OUTBOX,MODEL,DEPLOY,OBSERVE,RECOVERY]


def msg(src,dst,label,detail,kind='call',reply=None):
    return dict(src=src,dst=dst,label=label,detail=detail,kind=kind,reply=reply)


def seq(slug,title,actors,messages,notes,fragment=None):
    return dict(slug=slug,title=title,type='Sequence',actors=actors,messages=messages,notes=notes,fragment=fragment)


SEQUENCES=[
 seq('checkout-sequence','Checkout: authoritative commit before copies',[
 ('customer','Customer','ORDER OWNER'),('api','API / use case','SPEC + PROPOSED PORTS'),('redis','Redis rate store','PROPOSED ADMISSION'),('sql','PostgreSQL','BUSINESS AUTHORITY'),('relay','Outbox relay','PROPOSED WORKER')],[
 msg('customer','api','CHECKOUT','Owned cart + address; no client price authority'),msg('api','redis','ADMIT','Validated subject + active policy'),msg('redis','api','ALLOW / DENY','429 or protected outage 503 before SQL',kind='return',reply=1),msg('api','sql','BEGIN + GUARD','Check ownership, visibility, lots and budgets'),msg('sql','api','LOCKED INPUTS','Stable lock order; live authoritative values',kind='return',reply=3),msg('api','sql','WRITE + COMMIT','All orders + reservations + proposed outbox intent'),msg('sql','api','COMMITTED','Otherwise rollback all selected shops',kind='return',reply=5),msg('api','customer','WAIT_PAYMENT','Response only after source commit',kind='success',reply=0),msg('relay','sql','CLAIM LATER','Separate delivery; no request fire-and-forget'),msg('sql','relay','EVENT BATCH','Claim/lease commits before destination I/O',kind='return',reply=8)
 ],['SPEC: price/address snapshots, one order per shop, stock/budget reserve and selected-cart deletion share SQL commit.','PROPOSED: public-cache invalidation follows commit; MongoDB delivery is asynchronous and cannot repeat checkout.']),
 seq('start-payment-sequence','Payment start: durable identity & uncertainty',[
 ('customer','Customer','ORDER OWNER'),('api','Payment use case','PROPOSED RECOVERY'),('sql','PostgreSQL','ORDER + OPERATION INTENT'),('stripe','Stripe','EXTERNAL PROVIDER')],[
 msg('customer','api','START PAYMENT','Stable caller command identity; validate ownership'),msg('api','sql','DURABLE INTENT','Guard order, persist recoverable payment operation'),msg('sql','api','STABLE OP ID','Commit operation identity before provider call',kind='return',reply=1),msg('api','stripe','CREATE / REUSE','Same operation ID + parameters as provider key'),msg('stripe','api','KNOWN RESULT','Intent/status returned and checked',kind='return',reply=3),msg('api','sql','LINK RESULT','Guarded link; never mark order paid from browser'),msg('sql','api','LINK COMMITTED','Persist provider identity/result',kind='return',reply=5),msg('api','customer','NEXT ACTION','Secret/action or known outcome; per future contract',kind='success',reply=0),msg('api','sql','RECONCILE','Timeout/lost reply/link failure -> durable uncertainty'),msg('api','customer','UNCONFIRMED','Safe retry identity; do not assume provider failure',kind='return',reply=0)
 ],['PROPOSED recovery extension: the current spec can lose a new payment ID when its SQL transaction rolls back.','A provider side effect survives SQL rollback. Resume/retrieve with the same identity; API/schema changes need approval.'],dict(start=4,split=8,end=10,guards=['known provider result + SQL link succeeds','timeout, unknown result or failed SQL link'])),
 seq('payment-webhook-sequence','Webhook: durable receipt before final effects',[
 ('stripe','Stripe','SIGNED EVENT'),('api','Webhook ingress','SPEC + PROPOSED RECEIPT'),('sql','PostgreSQL','RECEIPT / BUSINESS TX'),('relay','Outbox relay','PROPOSED DELIVERY')],[
 msg('stripe','api','SIGNED EVENT','Raw body + signature; body/concurrency limits'),msg('api','sql','STORE RECEIPT','PROPOSED stable event receipt + payload fingerprint'),msg('sql','api','DURABLE','Unknown provider links remain recoverable',kind='return',reply=1),msg('api','stripe','ACK RECEIPT','PROPOSED acknowledgement after durable responsibility',kind='return',reply=0),msg('api','sql','APPLY GUARDED','Known supported event; order lock + current state'),msg('sql','api','COMMIT EFFECT','Business state + outbox intent atomically',kind='return',reply=4),msg('api','sql','HOLD / DEDUPE','Unknown identity, unsettled/partial refund or duplicate'),msg('sql','api','DISPOSITION','Reconcile or retain no-op; no invented restock',kind='return',reply=6),msg('relay','sql','CLAIM LATER','Publish only committed business events'),msg('sql','relay','EVENT BATCH','Destination delivery follows separate protocol',kind='return',reply=8)
 ],['SPEC: validate signature/raw body and guard SQL state. PROPOSED: durable receipt closes the orphan-acknowledgement gap.','Current refund-event contract is broader than safe provider semantics; partial/unsettled outcomes need explicit reconciliation.'],dict(start=4,split=6,end=8,guards=['known supported event + valid state','unknown / duplicate / partial or unsettled refund'])),
 seq('refund-sequence','Refund: confirmed money before inventory release',[
 ('operator','Shop / admin','LIVE SQL PERMISSION'),('api','Refund use case','PROPOSED RECOVERY'),('sql','PostgreSQL','ORDER + DURABLE INTENT'),('stripe','Stripe','EXTERNAL PROVIDER')],[
 msg('operator','api','REQUEST REFUND','Order PAYMENT_CONFIRMED; payment COMPLETED'),msg('api','sql','GUARD + INTENT','Order lock; persist stable refund operation'),msg('sql','api','STABLE OP ID','Recoverable intent commit before provider I/O',kind='return',reply=1),msg('api','stripe','FULL REFUND','Stable key; whole payment including shipping'),msg('stripe','api','REFUND STATUS','Check actual amount and terminal success',kind='return',reply=3),msg('api','sql','FINALIZE ONCE','Full settled success: refund + original lots + budget'),msg('sql','api','COMMITTED','State guards + release evidence + outbox',kind='return',reply=5),msg('api','operator','CONFIRMED','Only after authoritative finalization',kind='success',reply=0),msg('api','sql','WAIT / REVIEW','Pending/failed/partial/ambiguous -> retain operation'),msg('api','operator','NOT FINAL','No premature restock; future response contract needed',kind='return',reply=0)
 ],['PROPOSED: a refund request accepted by Stripe is not always a completed full refund. Current specifications need reconciliation.','Concurrent provider callbacks use the same durable identity and SQL guards; no double stock/budget release.'],dict(start=5,split=8,end=10,guards=['full amount + successful terminal provider status','pending / failed / partial / unknown or SQL failure'])),
 seq('outbox-delivery-sequence','Outbox delivery: one effect across replays',[
 ('relay','Outbox relay','PROPOSED BOUNDED WORKER'),('sql','PostgreSQL','OUTBOX / LEASE OWNER'),('mongo','MongoDB','MAJORITY LOCAL TX')],[
 msg('relay','sql','CLAIM BATCH','Short claim TX; availableAt + durable lease token'),msg('sql','relay','LEASE COMMIT','No SQL row lock held over network call',kind='return',reply=0),msg('relay','mongo','APPLY EVENT','Stable event ID + hash + source epoch/version'),msg('mongo','relay','TX COMMITTED','Marker + conditional projection + audit together',kind='return',reply=2),msg('relay','sql','ACK LEASE','Guard owner/token; destination already committed'),msg('sql','relay','DELIVERED','ACK loss may cause replay, not new business work',kind='success',reply=4),msg('relay','sql','RETRY LATER','Timeout is ambiguous; preserve event ID and payload'),msg('sql','relay','RECLAIMABLE','Lease expiry/backoff; poison to quarantine',kind='return',reply=6)
 ],['PROPOSED at-least-once delivery. Event marker alone must never commit before its projection effect.','Duplicate same-ID/same-hash is harmless; different hash, schema or epoch mismatch is quarantined and investigated.'],dict(start=3,split=6,end=8,guards=['majority destination commit confirmed','destination/ACK uncertain or retryable error'])),
 seq('config-publication-sequence','Config publication: validate, version & activate',[
 ('admin','Platform admin','LIVE AUTHORIZATION'),('api','Config publisher','PROPOSED VALIDATION'),('sql','PostgreSQL','PERMISSION AUTHORITY'),('mongo','MongoDB','CONFIG LOCAL TX'),('instances','API instances','VALIDATED SNAPSHOTS')],[
 msg('admin','api','PUBLISH','Typed config + expectedRevision; no secrets/scripts'),msg('api','sql','AUTHORIZE','Current PLATFORM_ADMIN permission'),msg('sql','api','PERMITTED','Config cannot grant itself authorization',kind='return',reply=1),msg('api','mongo','CAS + PUBLISH','Current + revision + audit in MongoDB transaction'),msg('mongo','api','REVISION','Majority outcome; reload on ambiguity',kind='return',reply=3),msg('api','admin','PUBLISHED','Return confirmed published revision',kind='success',reply=0),msg('mongo','instances','REFRESH HINT','Change stream is a hint; resume can expire',kind='async'),msg('instances','mongo','RECONCILE','Poll revision; full validated reload if needed'),msg('mongo','instances','SNAPSHOT','Immutable LKG + age; controlled fleet activation',kind='return',reply=7)
 ],['PROPOSED: rollback publishes a new revision. Ordinary config revision never resets Redis bucket epoch.','30s reconciliation and 5min last-known-good are candidates; stale/missing protected policy follows unavailable behavior.'])
]
ALL_SLUGS=[d['slug'] for d in SHEETS+SEQUENCES]
