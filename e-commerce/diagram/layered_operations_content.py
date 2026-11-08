"""Semantically distinct ownership, document, placement, signal and recovery views.

Coordinates are absolute; parent IDs are genuine native draw.io containment.
All new operational controls remain proposals. No schema is provisioned here.
"""
from diagram_content import box, row, link, MONO


def frame(slug, title, kind, desc, nodes, containers, edges=(), notes=(), legend=()):
    return dict(slug=slug, title=title, type=kind,
                eyebrow='E-COMMERCE / LAYERED SUPPORTING DESIGN / IN REVIEW',
                subtitle='Specified business responsibilities; proposed data and operating controls remain in review.',
                desc=desc, nodes=nodes, edges=list(edges), notes=list(notes),
                containers=containers,
                source='Commerce API specifications + MongoDB/Redis proposals + supporting operations research | No implementation change',
                legend=list(legend))


def group(key, x, y, w, h, title, tag, parent=None, kind='system'):
    d = dict(id=key, x=x, y=y, w=w, h=h, title=title, tag=tag, kind=kind)
    if parent:
        d['parent'] = parent
    return d


def leaf(key, parent, x, y, w, h, title, tag, lines=(), kind='backend', compact=False, shape=None):
    d = box(key, x, y, w, h, title, tag, [v if isinstance(v, tuple) else row(v) for v in lines], kind)
    d.update(parent=parent, compact=compact)
    if shape:
        d['shape'] = shape
    return d


def ref(source, target, points, label):
    d = link(source, target, points, label)
    d['kind'] = 'reference'
    return d


COMMERCE = frame(
    'commerce-overview', 'Commerce capability ownership', 'Nested',
    'Capability children belong to five business ownership boundaries; containment expresses responsibility, not a mandatory customer journey or separate deployed services.',
    [
        leaf('identity', 'access-context', 80, 272, 272, 104, 'Identity & sessions', 'CODE SUBSET / SPEC', ['Authen: five use cases', 'SQL owns session authority']),
        leaf('permission', 'access-context', 80, 408, 272, 104, 'Live permission', 'SPEC', ['Shop membership / admin role', 'Flags never grant access']),
        leaf('catalog', 'merch-context', 432, 272, 448, 104, 'Catalog & listings', 'SPEC', ['Categories / brands / options', 'Shop listing and live visibility']),
        leaf('inventory', 'merch-context', 432, 408, 208, 104, 'Inventory', 'SPEC', ['SKU / original lots', 'Live stock checks']),
        leaf('metadata', 'merch-context', 664, 408, 216, 104, 'Public metadata', 'PROPOSED CACHE', ['Public text only', 'SQL eligibility stays live'], 'optional'),
        leaf('governance', 'ops-context', 960, 272, 528, 104, 'Platform governance', 'SPEC + PROPOSED', ['Master data / roles / campaigns', 'Versioned config + publication audit']),
        leaf('operations', 'ops-context', 960, 408, 528, 104, 'Operating controls', 'PROPOSED', ['Outbox / telemetry / recovery ownership', 'Retention and targets need approval'], 'optional'),
        leaf('cart', 'order-context', 80, 648, 264, 104, 'Cart selection', 'SPEC', ['Customer-owned lines + address', 'Recheck availability at checkout']),
        leaf('checkout', 'order-context', 376, 648, 328, 104, 'Checkout & campaigns', 'SPEC / SQL ATOMIC', ['One order per selected shop', 'Reserve lots + discount budget'], 'focal'),
        leaf('delivery', 'order-context', 80, 800, 352, 104, 'Shipping & completion', 'SPEC', ['Parcels / tracking entered by shop', 'Quantity guards + 7-day completion']),
        leaf('history', 'order-context', 464, 800, 560, 104, 'Purchase history & review', 'SPEC + PROPOSED COPY', ['Completed purchase permits review', 'SQL history; restricted derived status search']),
        leaf('payment', 'money-context', 1120, 648, 368, 104, 'Payment & signed events', 'SPEC / STRIPE', ['Provider intent + verified webhook', 'SQL guards decide financial state']),
        leaf('refund', 'money-context', 1120, 800, 368, 104, 'Refund & reconciliation', 'SPEC + PROPOSED RECOVERY', ['Stable provider operation identity', 'Full settled refund before restock']),
    ],
    [
        group('commerce', 40, 160, 1504, 828, 'E-commerce responsibility map', 'BUSINESS OWNERSHIP; ONE BACKEND'),
        group('access-context', 64, 216, 304, 320, 'Access', 'IDENTITY & AUTHORIZATION', 'commerce'),
        group('merch-context', 416, 216, 480, 320, 'Merchandise', 'SHOP / CATALOG / INVENTORY', 'commerce'),
        group('ops-context', 944, 216, 560, 320, 'Platform operations', 'CROSS-CUTTING GOVERNANCE', 'commerce'),
        group('order-context', 64, 592, 976, 372, 'Ordering & fulfilment', 'CART / ORDER / PARCEL / REVIEW', 'commerce'),
        group('money-context', 1104, 592, 400, 372, 'Payments', 'PROVIDER EFFECTS + SQL GUARDS', 'commerce'),
    ],
    notes=[(40, 1012, 'Capability ownership only: no login-to-review chain, carrier integration, broker or independently deployed service is implied.', 11, 'body')],
    legend=[('box', 'Capability child'), ('text', 'Parent = responsibility boundary'), ('focal', 'Atomic checkout'), ('optional', 'Proposed control')])


MONGO = frame(
    'mongodb-document-model', 'MongoDB collections, fields & references', 'ER',
    'Five proposed collections are decomposed into identity, payload and integrity compartments; logical references and cardinality are separate from causal execution.',
    [
        leaf('current-id', 'current', 80, 256, 368, 72, 'Identity', '', [row('environment / scopeType / scopeId', MONO), row('key', MONO)], compact=True),
        leaf('current-payload', 'current', 80, 344, 368, 72, 'Payload', '', [row('value / effectiveAt / schemaVersion', MONO), row('revision / publishedBy', MONO)], compact=True),
        leaf('current-rule', 'current', 80, 432, 368, 72, 'Integrity', '', ['Unique canonical identity; CAS', 'Validated values; no secrets'], 'focal', compact=True),
        leaf('revision-id', 'revisions', 584, 256, 368, 72, 'Identity', '', [row('config identity + revision', MONO), 'Immutable published revision'], compact=True),
        leaf('revision-payload', 'revisions', 584, 344, 368, 72, 'Payload', '', [row('value / publishedAt / actorId', MONO), row('rollbackFromRevision / payloadHash', MONO)], compact=True),
        leaf('revision-rule', 'revisions', 584, 432, 368, 72, 'Integrity', '', ['Rollback publishes a new revision', 'Never overwrite published history'], compact=True),
        leaf('audit-id', 'audit', 1088, 256, 416, 72, 'Identity & references', '', [row('eventId / configRef or sourceRef', MONO), row('actorId / correlationId', MONO)], compact=True),
        leaf('audit-payload', 'audit', 1088, 344, 416, 72, 'Payload', '', [row('action / occurredAt', MONO), 'Minimized allowlisted evidence'], compact=True),
        leaf('audit-rule', 'audit', 1088, 432, 416, 72, 'Integrity', '', ['Restricted append; stable related ID', 'Backup + approved retention required'], compact=True),
        leaf('event-id', 'events', 80, 688, 552, 72, 'Identity', '', [row('eventId / payloadHash / schemaVersion', MONO), row('sourceEpoch / aggregateId / aggregateVersion', MONO)], compact=True),
        leaf('event-payload', 'events', 80, 776, 552, 72, 'Payload', '', [row('eventType / occurredAt / receivedAt / correlationId', MONO), 'Complete approved status snapshot'], compact=True),
        leaf('event-rule', 'events', 80, 864, 552, 72, 'Integrity', '', ['Same ID / same hash: replay; conflict: quarantine', 'Marker + effect + audit share one local transaction'], 'optional', compact=True),
        leaf('projection-id', 'projection', 816, 688, 688, 72, 'Identity', '', [row('sourceEpoch + aggregateType + aggregateId', MONO), 'Unique current snapshot within active authority epoch'], compact=True),
        leaf('projection-payload', 'projection', 816, 776, 688, 72, 'Payload', '', [row('sourceVersion / schemaVersion / sourceOccurredAt / projectedAt', MONO), 'Status + allowed references; restricted operational read'], compact=True),
        leaf('projection-rule', 'projection', 816, 864, 688, 72, 'Integrity', '', ['Atomic replacement only for newer complete snapshots', 'Derived copy never settles money; no automatic TTL'], 'optional', compact=True),
    ],
    [
        group('config-group', 40, 160, 1504, 392, 'Configuration authority + shared audit evidence', 'PROPOSED COLLECTIONS; AUDIT MAY ALSO REFERENCE BUSINESS EVENTS'),
        group('current', 64, 208, 400, 320, 'runtime_config_current', 'CURRENT VALIDATED VALUE', 'config-group'),
        group('revisions', 568, 208, 400, 320, 'runtime_config_revisions', 'IMMUTABLE PUBLISHED HISTORY', 'config-group'),
        group('audit', 1072, 208, 448, 320, 'application_audit_events', 'APPEND EVIDENCE; NOT FINANCIAL LEDGER', 'config-group'),
        group('derived-group', 40, 592, 1504, 392, 'Delivery evidence & derived transaction status', 'POSTGRESQL REMAINS BUSINESS AUTHORITY'),
        group('events', 64, 640, 584, 320, 'integration_events', 'IMMUTABLE ENVELOPE + DELIVERY MARKER', 'derived-group'),
        group('projection', 800, 640, 720, 320, 'transaction_status_projections', 'CURRENT COPY; NOT COMPLETE HISTORY', 'derived-group'),
    ],
    edges=[
        ref('current', 'revisions', [(464, 384), (568, 384)], (516, 368, 'REVISIONS')),
        ref('revisions', 'audit', [(968, 384), (1072, 384)], (1020, 368, 'AUDIT REF')),
        ref('events', 'projection', [(648, 816), (800, 816)], (724, 800, 'SOURCE REF')),
    ],
    notes=[(40, 576, 'Local TX A: current + revision + audit. Local TX B: event marker + conditional projection + related audit. No PostgreSQL/MongoDB TX.', 11, 'body'),
           (40, 1012, 'Logical references only: MongoDB does not enforce these as SQL foreign keys. Candidate model; no collections or indexes provisioned.', 11, 'body')],
    legend=[('box', 'Collection compartment'), ('text', 'Line = logical reference'), ('optional', 'Derived integrity rule'), ('text', 'All collections proposed')])
MONGO['cardinality'] = [(476, 400, '1'), (548, 400, 'N'), (980, 400, '1'), (1044, 400, '0..N'), (660, 832, 'N'), (772, 832, '0..1')]


DEPLOYMENT = frame(
    'deployment-security', 'Proposed private host & artifact placement', 'Deployment',
    'A self-hosted reference environment contains application, data and Redis security zones, six host pools and the version-pinned artifacts placed inside them.',
    [
        leaf('api-artifact', 'api-host', 104, 412, 376, 88, 'Ecommerce.Api', 'ARTIFACT / releaseSha', ['x2 stateless API replicas', 'JWT + live SQL permissions'], 'focal'),
        leaf('worker-artifact', 'worker-host', 104, 780, 376, 104, 'Background responsibilities', 'ARTIFACT / releaseSha', ['x1 scheduling / relay pool', 'Leases + bounded concurrency']),
        leaf('pg-artifact', 'pg-host', 592, 412, 536, 88, 'PostgreSQL', 'ARTIFACT / PIN SUPPORTED MAJOR', ['x2: primary + standby; business + outbox', 'TLS / least-privilege SQL roles'], 'store'),
        leaf('mongo-artifact', 'mongo-host', 592, 780, 536, 104, 'MongoDB', 'ARTIFACT / PIN SUPPORTED MAJOR', ['x3 data-bearing replica-set members', 'Config reader / publisher / writer roles'], 'store'),
        leaf('cache-artifact', 'cache-host', 1240, 412, 240, 88, 'Redis cache', 'PIN SUPPORTED RELEASE', ['x1; loss tolerated', 'allkeys-lfu; cache ACL'], 'optional'),
        leaf('rate-artifact', 'rate-host', 1240, 780, 240, 104, 'Redis admission', 'PIN SUPPORTED RELEASE', ['x2: primary + replica', 'noeviction; limiter ACL'], 'optional'),
    ],
    [
        group('private-env', 40, 160, 1504, 828, 'Proposed production reference / self-hosted', 'NO VENDOR, REGION OR RUNNING CLUSTER CLAIM'),
        group('app-zone', 64, 216, 456, 744, 'Application subnet', 'TRUSTED INGRESS; HTTPS 443', 'private-env'),
        group('data-zone', 552, 216, 616, 744, 'Private data subnet', 'NO PUBLIC DATA / ADMIN PORTS', 'private-env'),
        group('redis-zone', 1200, 216, 320, 744, 'Isolated Redis zone', 'SEPARATE MEMORY + CREDENTIALS', 'private-env'),
        group('api-host', 88, 352, 408, 168, 'API host pool', 'PROPOSED VM POOL / x2', 'app-zone', 'application'),
        group('worker-host', 88, 712, 408, 208, 'Worker host pool', 'PROPOSED VM POOL / x1', 'app-zone', 'application'),
        group('pg-host', 576, 352, 568, 168, 'PostgreSQL host pool', 'PROPOSED PRIVATE HOSTS / x2', 'data-zone', 'store'),
        group('mongo-host', 576, 712, 568, 208, 'MongoDB host pool', 'PROPOSED PRIVATE HOSTS / x3', 'data-zone', 'store'),
        group('cache-host', 1224, 352, 272, 168, 'Cache host', 'PROPOSED PRIVATE HOST / x1', 'redis-zone', 'optional'),
        group('rate-host', 1224, 712, 272, 208, 'Admission hosts', 'PROPOSED PRIVATE HOSTS / x2', 'redis-zone', 'optional'),
    ],
    edges=[
        link('api-host', 'pg-host', [(496, 400), (576, 400)], (536, 384, 'TLS:5432')),
        link('worker-host', 'pg-host', [(496, 752), (536, 752), (536, 472), (576, 472)], (556, 456, 'TLS:5432'), dashed=True),
        link('worker-host', 'mongo-host', [(496, 824), (576, 824)], (536, 808, 'TLS:27017'), dashed=True),
        link('api-host', 'mongo-host', [(344, 352), (344, 328), (1176, 328), (1176, 860), (1144, 860)], (760, 312, 'TLS:27017')),
        link('api-host', 'cache-host', [(240, 352), (240, 296), (1360, 296), (1360, 352)], (1396, 324, 'TLS:6379')),
        link('api-host', 'rate-host', [(188, 352), (188, 280), (1512, 280), (1512, 752), (1496, 752)], (850, 264, 'TLS:6379')),
    ],
    notes=[(40, 1012, 'Reference placement only. Version pins and replica counts need approval + capacity/failover tests; replication does not replace backup.', 11, 'body')],
    legend=[('box', 'Deployable artifact'), ('text', 'Parent = zone / host pool'), ('arrow', 'Permitted TLS path'), ('optional', 'Proposed isolated service')])


OBSERVABILITY = frame(
    'observability-design', 'Operational signals → pipelines → decisions', 'Data Flow',
    'Application and data-layer instruments feed separate metric, trace and log pipelines; output groups distinguish objective measurement and alerting from diagnostic investigation.',
    [
        leaf('app-signal', 'app-sources', 80, 272, 392, 104, 'API & worker instruments', 'PROPOSED SOURCE SIGNALS', ['Rate / errors / latency / checkout outcome', 'TraceId + operationId; redact PII']),
        leaf('sql-signal', 'data-sources', 80, 584, 392, 104, 'PostgreSQL & outbox', 'PROPOSED SOURCE HEALTH', ['Pool / locks / oldest eligible event age', 'Backlog / retry / quarantine / backup age']),
        leaf('redis-signal', 'data-sources', 80, 712, 392, 104, 'Redis cache & rate', 'PROPOSED DERIVED HEALTH', ['Hit / refill / memory / eviction', 'Quota deny vs store unavailable']),
        leaf('mongo-signal', 'data-sources', 80, 840, 392, 104, 'MongoDB & configuration', 'PROPOSED DOCUMENT HEALTH', ['Lag / sourceVersion / sourceEpoch', 'Config age / replica + storage health']),
        leaf('metrics', 'pipelines', 616, 512, 328, 104, 'Metric pipeline', 'PROPOSED / LOW CARDINALITY', ['Bound labels; no event or user IDs', 'Source → destination → read watermark'], 'focal'),
        leaf('traces', 'pipelines', 616, 272, 328, 104, 'Trace pipeline', 'PROPOSED / SAMPLED', ['Request + worker dependency spans', 'Correlate commit and delivery timing']),
        leaf('logs', 'pipelines', 616, 848, 328, 104, 'Structured log pipeline', 'PROPOSED / REDACTED', ['Stable diagnostic IDs; minimize payload', 'Access + retention explicitly controlled']),
        leaf('slo', 'decision-outputs', 1072, 464, 440, 104, 'Business SLIs & objectives', 'PROPOSED / UNMEASURED', ['Freshness + coverage + correctness', '5s lag candidate; validate denominators']),
        leaf('alert', 'decision-outputs', 1072, 272, 440, 104, 'Alert routing & response', 'PROPOSED / OWNER + RUNBOOK', ['Impact + sustained lag/error conditions', 'Contain / reconcile / recover + evidence']),
        leaf('trace-query', 'investigation', 1072, 760, 440, 88, 'Trace investigation', 'PROPOSED DIAGNOSTICS', ['Find failing dependency or delivery step']),
        leaf('log-query', 'investigation', 1072, 868, 440, 88, 'Evidence search', 'PROPOSED DIAGNOSTICS', ['Correlate IDs; no high-cardinality metrics']),
    ],
    [
        group('sources', 40, 160, 464, 828, 'Signal sources', 'APPLICATION + DATA LAYER'),
        group('app-sources', 64, 216, 424, 232, 'Application layer', 'API HOST + WORKER RESPONSIBILITIES', 'sources'),
        group('data-sources', 64, 528, 424, 440, 'Data layer', 'AUTHORITY / COPIES / RECOVERY EVIDENCE', 'sources'),
        group('pipelines', 592, 216, 376, 768, 'Collection pipelines', 'OPEN TELEMETRY SHAPES; TOOL NOT SELECTED'),
        group('outputs', 1040, 160, 504, 828, 'Operational outputs', 'MEASURE → DIAGNOSE → RESPOND'),
        group('decision-outputs', 1056, 216, 472, 400, 'Objective & response', 'SERVICE OWNER / OPERATIONS', 'outputs'),
        group('investigation', 1056, 704, 472, 268, 'Investigation', 'RESTRICTED DIAGNOSTIC READ', 'outputs'),
    ],
    edges=[
        link('app-signal', 'metrics', [(472, 328), (552, 328), (552, 536), (616, 536)], (512, 312, 'COUNTERS'), dashed=True),
        link('data-sources', 'metrics', [(488, 560), (616, 560)], (552, 544, 'HEALTH'), dashed=True),
        link('app-sources', 'traces', [(488, 280), (616, 280)], (552, 264, 'SPANS'), dashed=True),
        link('app-sources', 'logs', [(64, 424), (52, 424), (52, 1000), (780, 1000), (780, 952)], (416, 984, 'RECORDS'), dashed=True),
        link('metrics', 'slo', [(944, 536), (1072, 536)], (1008, 520, 'SLI')),
        link('metrics', 'alert', [(780, 512), (780, 440), (1280, 440), (1280, 376)], (1030, 424, 'ALERTS')),
        link('traces', 'trace-query', [(944, 304), (976, 304), (976, 192), (1536, 192), (1536, 804), (1512, 804)], (1494, 672, 'TRACE DATA')),
        link('logs', 'log-query', [(944, 916), (1072, 916)], (1004, 900, 'LOG RECORDS')),
    ],
    notes=[(40, 1012, 'Healthy storage is insufficient: reconcile omitted events and stale copies against SQL. Proposed 30s poll / 5min config age are not measured SLOs.', 11, 'body')],
    legend=[('box', 'Instrument / pipeline / output'), ('text', 'Parent = layer or owning function'), ('arrow', 'Telemetry or measurement flow'), ('focal', 'Low-cardinality metric pipeline')])


RECOVERY = frame(
    'recovery-design', 'Recovery activity & owner handoffs', 'Swimlane',
    'A proposed owner-lane activity flow fences workers, restores authority, reconciles provider effects and gates rebuilt projections before reopening; these are actions and decisions, not persisted commerce states.',
    [
        leaf('declare', 'incident-owner', 64, 240, 288, 104, 'Declare incident', 'INCIDENT COMMANDER', ['Scope + evidence + backup points', 'Record impact and recovery owner']),
        leaf('contain', 'data-owner', 432, 240, 304, 104, 'Contain & fence', 'DATA / PLATFORM OPERATOR', ['Pause unsafe writes and old relays', 'Revoke old worker credentials/epoch']),
        leaf('restore', 'data-owner', 432, 432, 304, 104, 'Restore authority', 'DATA / PLATFORM OPERATOR', ['Recorded SQL point + Mongo config', 'Issue external new sourceEpoch']),
        leaf('reconcile', 'payment-owner', 816, 432, 304, 104, 'Reconcile provider money', 'PAYMENT OPERATIONS', ['Compare actual provider effects', 'Restore never reverses Stripe']),
        leaf('money-gate', 'payment-owner', 856, 616, 224, 104, 'MATCH?', '', ['Source + money verified'], shape='decision'),
        leaf('hold', 'incident-owner', 64, 616, 288, 104, 'Hold & investigate', 'INCIDENT COMMANDER', ['Keep uncertain writes disabled', 'Review timeline + record corrections'], 'optional'),
        leaf('rebuild', 'service-owner', 1216, 616, 304, 104, 'Rebuild derived data', 'APPLICATION / SERVICE OWNER', ['New-epoch snapshots; fence old reads', 'Cold cache + bounded refill']),
        leaf('reopen-gate', 'service-owner', 1248, 792, 240, 104, 'READY?', '', ['Checks + operator approval'], 'focal', shape='decision'),
        leaf('resumed', 'service-owner', 1248, 928, 240, 44, 'Reopen & watch', '', [], compact=True, shape='terminator'),
    ],
    [
        group('incident-owner', 40, 160, 336, 828, 'Incident command', 'PROPOSED OWNER LANE'),
        group('data-owner', 408, 160, 352, 828, 'Data / platform operator', 'PROPOSED OWNER LANE'),
        group('payment-owner', 792, 160, 352, 828, 'Payment operations', 'PROPOSED OWNER LANE'),
        group('service-owner', 1192, 160, 352, 828, 'Application service owner', 'PROPOSED OWNER LANE'),
    ],
    edges=[
        link('declare', 'contain', [(352, 272), (432, 272)], (392, 256, 'CONTAIN')),
        link('contain', 'restore', [(584, 344), (584, 432)]),
        link('restore', 'reconcile', [(736, 484), (816, 484)], (776, 468, 'COMPARE')),
        link('reconcile', 'money-gate', [(968, 536), (968, 616)]),
        link('money-gate', 'rebuild', [(1080, 668), (1216, 668)], (1148, 652, 'YES')),
        link('money-gate', 'hold', [(856, 668), (352, 668)], (604, 652, 'NO'), dashed=True),
        link('hold', 'contain', [(208, 616), (208, 384), (400, 384), (400, 320), (432, 320)], (304, 368, 'REVIEW'), dashed=True),
        link('rebuild', 'reopen-gate', [(1368, 720), (1368, 760), (1368, 792)]),
        link('reopen-gate', 'resumed', [(1368, 896), (1368, 928)], (1392, 900, 'YES')),
        link('reopen-gate', 'hold', [(1248, 844), (1176, 844), (1176, 956), (384, 956), (384, 752), (208, 752), (208, 720)], (780, 940, 'NO'), dashed=True),
    ],
    notes=[(40, 1012, 'READY = smoke + invariants + load check; accept recorded data-loss window. Measure RPO/RTO in drills; audit history requires its own backup.', 11, 'body')],
    legend=[('box', 'Owned action'), ('text', 'Diamond = decision gate'), ('arrow', 'Control / owner handoff'), ('optional', 'Hold unsafe reopening')])

OPS = [COMMERCE, MONGO, DEPLOYMENT, OBSERVABILITY, RECOVERY]
