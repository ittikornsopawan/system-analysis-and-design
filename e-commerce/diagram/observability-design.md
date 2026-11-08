---
name: E-commerce Operational Signal Pipeline
description: อธิบาย application/data instruments, metrics/traces/logs pipelines และ SLO/alerting outputs ใช้ก่อนออกแบบ telemetry contracts หรือ operational acceptance
status: in-review
approved_by: null
approved_at: null
---

# สัญญาณที่มาของข้อมูลและการตัดสินใจปฏิบัติการ

ภาพนี้ตอบว่า **วัดอะไร ส่งผ่าน pipeline ใด และข้อมูลนั้นนำไปตัดสินใจอย่างไร** ใช้ dataflow จากซ้ายไปขวา ไม่ใช้ architecture cards ที่เพียงระบุว่าแต่ละระบบมี monitoring และไม่อ้างว่าเลือก telemetry vendor หรือติดตั้ง collector แล้ว

## โครงสร้างที่เห็นในภาพ

มี ownership สามกลุ่มหลักและกลุ่มย่อยจริงใน draw.io:

1. `Signal sources` ครอบ `Application layer` ที่มี API/worker instruments และ `Data layer` ที่แยก PostgreSQL/outbox, Redis cache/rate และ MongoDB/configuration เป็นกล่องลูก
2. `Collection pipelines` ครอบ metric, sampled trace และ structured log pipelines แต่ละ pipeline มีหน้าที่คนละชนิด ไม่ใช้ IDs เป็น metric labels
3. `Operational outputs` ครอบ `Objective & response` ที่มี Business SLIs & objectives กับ Alert routing & response และ `Investigation` ที่มี Trace investigation กับ Evidence search

เส้น COUNTERS และ HEALTH ป้อน metric pipeline; SPANS และ RECORDS แยก trace/log path Metric สร้างทั้ง SLI และ alert decisions ส่วน trace/log ช่วยอธิบายสาเหตุผ่าน restricted diagnostic reads เส้นนี้เป็น telemetry flow ไม่ใช่การเรียก business transaction หรือการ grant permission

## สิ่งที่ต้องวัด

| ชั้น | สัญญาณที่ใช้ได้ตาม proposal | การใช้ |
| --- | --- | --- |
| Application | Rate, errors, latency, checkout outcome, dependency spans | วัด customer flow และแยก failure point |
| PostgreSQL / outbox | Pool/lock wait, oldest eligible age, backlog, retry, quarantine, backup age | วัด source health และ omitted/late delivery |
| Redis | Hit/refill, memory/eviction, quota deny เทียบ store unavailable | แยก policy denial ออกจาก infrastructure failure |
| MongoDB / config | Projection lag/version/epoch, config age, replica/storage health | ตรวจความสด ความถูกต้องและ authority generation |

วัด freshness, coverage และ correctness ร่วมกัน Successful delivery latency อย่างเดียวไม่เห็น event ที่ตกหล่น ต้อง reconcile กับ SQL source และเผย serving watermark/source version จึงจะตรวจ stale reads ได้ TraceId/operationId/eventId อยู่ใน redacted diagnostic records ไม่ใช้เป็น high-cardinality metric labels

## Targets, alerting และความล้มเหลว

เป้าหมาย projection lag ภายใน 5 วินาที, reconciliation poll 30 วินาที และ config last-known-good 5 นาทีเป็น **candidate ที่ยังไม่วัด** ต้องอนุมัติ window, denominator, outage treatment และ alert policy ก่อนถือเป็น SLO ไม่สร้าง availability percentage หรือ throughput ขึ้นใหม่

Alert ต้องผูก customer impact หรือ sustained lag/error พร้อม owner และ runbook ไม่แจ้งเพียงเพราะ dependency ยังตอบ health check ได้ ข้อมูลทุก pipeline ต้องจำกัด payload, redact PII/secrets/card data และกำหนด access/retention Sampling อาจพลาด trace; log ที่หายต้องไม่ถูกตีความว่า business effect ไม่เคยเกิด

การแยก pipeline เพิ่ม operational cost แต่ทำให้ bound labels, sampling และ retention ตาม signal type ได้ การรวม output ในกลุ่มเดียวกันช่วยให้เห็นว่า dashboard ไม่ใช่หลักฐานความถูกต้อง ต้องมี reconciliation และผู้รับผิดชอบลงมือ contain/recover ด้วย

## แหล่งข้อมูลและสถานะ

- [Operations research](supporting-data-operations-research.md), [MongoDB design](mongodb-design.md), [Redis design](redis-design.md)
- [Outbox design](event-outbox-design.md), [delivery sequence](outbox-delivery-sequence.md), [recovery activity](recovery-design.md)
- [Google SRE SLI guidance](https://sre.google/workbook/implementing-slos/), [pipeline reliability](https://sre.google/workbook/data-processing/)

เอกสารยัง `in-review` ไม่มี instrumentation, exporter, dashboard, alert policy หรือ runtime implementation เพิ่มเติม ต้องทดสอบ baseline/spike/cold-cache, failover, memory pressure, replay และ restore ก่อนอ้างผลเชิงปฏิบัติการ

## นิยาม SLI และเกณฑ์ทดสอบที่เสนอ

ตารางนี้เป็น **test/design proposal ที่ยังไม่วัด** เพื่อให้ตรวจรับได้ ไม่ใช่คำรับประกัน production และไม่เปลี่ยน rate policies ของ Redis ที่รออนุมัติอยู่

| Flow | ตัววัดและ denominator | Candidate objective / เหตุผล |
| --- | --- | --- |
| Public read | request ที่มีอินพุตถูกต้องและผ่าน admission; success/latency แยก cache hit/miss | p95 ≤300ms ภายใต้ workload ที่กำหนด; อย่านับ 429 เป็น backend failure โดยไม่แยกเหตุ |
| Checkout | valid admitted attempts, commit success, SQL duration และ invariant failures | p95 ≤700ms สำหรับ SQL/use-case path ที่ไม่รวม provider I/O; correctness ของ stock/budget ต้องไม่มี duplicate effect |
| Payment/webhook | signature-valid receipts, durable receipt latency, business-apply age | p95 durable receipt ≤1s และตรวจ backlog age; รับ ACK ได้ไม่เท่ากับ order ถูก apply แล้ว |
| Availability | สัดส่วน eligible requests ที่จบตามความหมายธุรกิจใน rolling 30 วัน | candidate 99.9%; ต้องตกลง planned outage, provider failure และ degraded modes ก่อนใช้จริง |
| Outbox/projection | eligible source-commit→destination-commit lag, oldest READY/RETRY, quarantine count | normal projection lag ≤5s เป็น target เดิม; alert เมื่อ oldest eligible age >60s ต่อเนื่อง5นาทีเป็น candidate |
| Config freshness | เวลาจาก published revision ถึง validated active snapshot; current revision/age | poll30s/LKG5min เป็น candidate เดิม; แยก stale-config alarm จาก API host health |

Metric labels ใช้ bounded dimensions เช่น route template, operation type, result class และ store role ไม่ใช้ eventId/userId/orderId เป็น labels ที่ทำให้ cardinality โตไม่จำกัด ตัวตนเหล่านั้นอยู่ใน redacted structured logs/traces ที่มี access/retention จำกัด Histogram ต้องเก็บ bucket ที่ใช้ประเมิน p95 ได้และแยก timeout/cancel จาก complete

## Workload และ capacity evidence

เริ่ม synthetic baseline ที่เสนอ100 requests/s เป็นเวลา30นาทีและ spike500 requests/s เป็นเวลา60วินาที กระจาย trusted subjects ตาม policy ไม่ใช้ IP เดียวที่ตั้งใจโดน rate limit จำนวน API replicas เริ่ม2ตาม deployment proposal ไม่ได้อ้างว่ารับ traffic นี้ได้แล้ว วัด instance CPU/memory/GC, DB connections/pool wait, Redis command/latency/memory, Mongo majority latency และ steady-state backlog พร้อมกัน

| Scenario | สิ่งที่ต้องเห็นและเกณฑ์ตัดสิน |
| --- | --- |
| Warm / cold cache | เปรียบเทียบ SQL load และ p95; bounded refill ไม่ทำให้ source ล่มเมื่อ cache ว่าง |
| NAT / rotating subjects | แยก legitimate shared-IP throttling, key cardinality และ sensitive-route503; กำหนด budget จาก bytes/bucketจริง |
| Redis timeout / OOM / failover | 429ต่างจาก store-unavailable; local fallbackไม่อ้างfleet quota; ไม่มี duplicate command retry |
| Mongo outage / duplicate / reorder | sourceยังcommitted; lag/backlogโตอย่างเห็นได้; replayไม่ทำbusiness mutationซ้ำ |
| Config stale / stream history lost | reconciliation/full reloadทำงาน; policyไม่รีเซ็ตcounterหรือเปิดสิทธิ์เอง |
| Long SQL transaction / pool exhaustion | รู้ว่า queueรออยู่ตรงไหน; ไม่เพิ่มconnectionsเพื่อกลบปัญหาโดยไม่มีbudget |

Capacity report ต้องบันทึก dataset/cardinality, query/index plan, replica count, resource limits, configuration revision และระยะเวลาทดสอบ จึงจะนำผลไปปรับ SLO/quotas ได้ Test failures เป็นข้อมูลออกแบบ ไม่ใช่เหตุให้เปลี่ยน denominator จนดูผ่าน

## ผู้รับผิดชอบและ response loop

API/use-case owner รับผิดชอบ business error/latency; data owner ดู SQL/outbox/backups; platform operator ดู store health/credentials/telemetry; incident owner ตัดสิน contain/reopen ทุก alert ต้องมี owner, severity, evidence query, runbook และ escalation policy ตัวอย่าง alert body ใช้ route/result/window/lag พร้อม correlation reference ที่ได้รับสิทธิ์ ไม่แนบ secrets หรือ payloadธุรกรรมทั้งหมด ใน [Recovery](recovery-design.md) มีเจ้าของแต่ละ lane และ gate ที่ต้องผ่านก่อนเปิด writes
