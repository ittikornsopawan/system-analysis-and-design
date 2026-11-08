---
name: E-commerce Order Lifecycle Explanation
description: คำอธิบายภาพ order-lifecycle พร้อมสถานะคำสั่งซื้อ transitions guards actors และผลต่อ stock/budget ใช้อ่านประกอบการทบทวน business lifecycle และ failure cases
---

# Order lifecycle — สถานะธุรกิจของคำสั่งซื้อ

เอกสารนี้อธิบาย [order-lifecycle.drawio.png](order-lifecycle.drawio.png) ซึ่งเลือกแสดง **วงจรชีวิตของคำสั่งซื้อ ตั้งแต่สร้าง จ่ายเงิน จัดส่ง จบงาน จนถึงยกเลิกหรือคืนเงิน** เพื่อให้เห็น event, guard และผลของแต่ละทางเดินอย่างเป็นระบบ โครงสร้าง runtime อ่านจาก [Architecture Design](architecture-design.md) และตำแหน่งโค้ดจาก [Repository Architecture](../reference/repository/repository-architecture.md)

## 1. เหตุผลที่เลือก State Machine / Lifecycle phase map

คำสั่งซื้อหนึ่งรายการมีสถานะปัจจุบันและเปลี่ยนได้เฉพาะเมื่อเงื่อนไขผ่าน การวาดเป็นกล่องความสามารถทั่วไปจะบอกไม่ได้ว่า “จ่ายแล้วแต่ยังไม่ส่ง” คืนเงินได้หรือไม่ หรือ “จ่ายล้มเหลว” ต้องสร้าง order ใหม่หรือไม่ ภาพนี้จึงใช้ state machine มี 6 persisted order states, จุดเริ่มต้นหนึ่งจุด และ 8 transitions

เส้นทางหลักวางซ้ายไปขวาเป็น `WAIT_PAYMENT → PAYMENT_CONFIRMED → PROCESSING → COMPLETED` ด้านบนแยก retry/guarded recovery ด้านล่างแยก `CANCELLED` และ `REFUNDED` การวางแยกช่วยให้อ่าน happy path ก่อนแล้วค่อยพิจารณาเหตุการณ์ผิดปกติ พื้นที่ล่างด้านขวาแยกคำแนะนำการอ่านภาพ publication/runtime ออกจาก business states

นี่เป็นภาพของพฤติกรรมตาม specifications ที่ตรวจใน workspace ไม่ใช่หลักฐานว่ามี order/payment/shipping handlers ทำงานครบใน backend ปัจจุบัน สถานะอนุมัติของข้อเสนอแต่ละเรื่องยังยึดเอกสารต้นทาง

## 2. ต้องแยกสถานะของสามสิ่งออกจากกัน

| สิ่งที่มีสถานะ | ตัวอย่าง | ความหมาย |
| --- | --- | --- |
| Order: `sales.t_order` | `WAIT_PAYMENT`, `PAYMENT_CONFIRMED`, `PROCESSING`, `COMPLETED`, `CANCELLED`, `REFUNDED` | ภาพนี้แสดงสถานะของสิ่งนี้เป็นหลัก |
| Payment | `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`, `CANCELLED`, `REFUNDED` | การเคลื่อนของเงิน/PaymentIntent แต่ละรายการ ไม่ใช่ order state |
| Shipping/parcel | `PENDING`, `SHIPPED`, `DELIVERED`, `CANCELLED`, `RETURNED` | พัสดุแต่ละชิ้น; order หนึ่งมีหลาย parcels ได้ |

คำว่า `PROCESSING` ของ payment หมายถึงเงินอยู่ระหว่างดำเนินการ ต่างจาก `PROCESSING` ของ order ที่เริ่ม fulfillment แล้ว และ payment `COMPLETED` ทำให้ order `PAYMENT_CONFIRMED` ไม่ได้ทำให้ order `COMPLETED` ทันที

เหตุผลที่แยก entities เหล่านี้คือจำนวนและเวลาไม่ตรงกัน order อาจมีหลาย payment attempts และหลาย parcels ถ้าใช้สถานะเดียวรวมทั้งหมด จะตีความการลองชำระใหม่ การส่งบางส่วน และการคืนเงินผิดได้

## 3. รายละเอียดหกสถานะ

### 3.1 `WAIT_PAYMENT` — รอชำระเงิน

เข้าสถานะนี้จาก [sales/02-create-order](../../doc/api/sales/02-create-order/spec.md) โดยลูกค้าที่ authenticated เลือก cart/address ของตนเอง ระบบตรวจ live availability/price/stock และสร้างหนึ่ง order ต่อร้าน ถ้า request มีหลายร้าน จะสร้างหลาย orders ใน PostgreSQL transaction เดียว สำเร็จทั้งหมดหรือ rollback ทั้งหมด

Order เก็บ snapshot ราคาตาม lot และที่อยู่ ณ ตอนสั่งซื้อ จอง stock และ campaign budget พร้อม soft-delete cart rows ที่ซื้อใน transaction เดียว ค่าเริ่มต้น payment window ตาม spec คือ 30 นาที ยึดเวลาธุรกิจตาม specification

เหตุผลของ price/address snapshot คือการแก้ราคาหรือที่อยู่ในภายหลังต้องไม่เปลี่ยนประวัติ order ส่วนการจอง stock/budget ตอนสร้าง order ลดการแข่งขันที่ลูกค้าหลายคนซื้อทรัพยากรเดียวกัน การจองทำให้ต้องมี cancellation/expiry คืนทรัพยากรอย่างถูกต้อง

การสร้าง order ยังไม่ใช่การชำระเงิน และการสั่งซื้อไม่เชื่อ price/quantity จาก cache เป็น authority

### 3.2 `PAYMENT_CONFIRMED` — ได้รับการยืนยันการชำระ

เกิดจาก signed success event ตาม [payment/02-stripe-webhook](../../doc/api/payment/02-stripe-webhook/spec.md) เมื่อ payment/state guard ยอมรับและ order ยัง `WAIT_PAYMENT` ระบบทำ payment เป็น `COMPLETED` และเปลี่ยน order เป็น `PAYMENT_CONFIRMED`

แม้เลย `expires_at` แล้ว ยังยอมรับ success ได้ถ้า order ยัง `WAIT_PAYMENT` และ stock ยังถูกถืออยู่ตาม spec ต้องแยก “ครบเวลาที่ควร expire” จาก “ถูกยกเลิกและคืน stock ไปแล้ว” การตัดสินจากเวลาอย่างเดียวอาจคืนเงินทั้งที่ทรัพยากรยังจองอยู่ หรือขายทรัพยากรซ้ำโดยไม่ตั้งใจ

สถานะนี้ยังไม่เริ่มจัดส่ง จึงเป็นจุดที่ API อนุญาต full refund ภายใต้สิทธิ์ที่กำหนด browser success page ไม่ใช่หลักฐานยืนยันการชำระ

### 3.3 `PROCESSING` — เริ่ม fulfillment

ตาม [shipping/01-create-shipping](../../doc/api/shipping/01-create-shipping/spec.md) สมาชิกของร้านที่มีสิทธิ์หรือ platform administrator สร้าง parcel แรกเป็น `PENDING` แล้วเปลี่ยน order จาก `PAYMENT_CONFIRMED` เป็น `PROCESSING` ใน transaction เดียว ไม่ต้องรอ parcel เป็น `SHIPPED`

Order แบ่งส่งได้หลาย parcels แต่ assigned quantity รวมจาก `PENDING`, `SHIPPED`, `DELIVERED` ต้องไม่เกินจำนวนของ order item; `CANCELLED`/`RETURNED` parcels คืน assigned capacity ให้สร้าง parcel ใหม่ การ lock order row ก่อนตรวจยอดช่วยป้องกันคำขอพร้อมกันจัดจำนวนซ้ำ

การสร้าง parcel ไม่ใช่การหัก stock ใหม่ เพราะ stock ถูกจองจาก lot ตอนสร้าง order แล้ว เหตุผลที่แยก allocation กับ stock คือไม่ให้การแบ่งส่งหลายกล่องกลายเป็นการขายสินค้าชุดเดิมหลายครั้ง

### 3.4 `COMPLETED` — รับสินค้าครบ

ตาม [shipping/06-confirm-delivery](../../doc/api/shipping/06-confirm-delivery/spec.md) ผู้เป็นเจ้าของ order ยืนยัน parcel ที่ `SHIPPED` ให้เป็น `DELIVERED` หรือ system job ยืนยันเมื่อผ่านเงื่อนไขครบ 7 วัน เมื่อทุก active order item มี delivered quantity ครบ และ order ยัง `PROCESSING` จึงเปลี่ยนเป็น `COMPLETED`

ร้านหรือ administrator ไม่ยืนยันแทน receiver ผ่าน confirm API การส่งพัสดุไปแล้วไม่ทำให้จบทันที: ต้องได้รับการยืนยันจาก owner หรือผ่านเกณฑ์ system job ที่กำหนด สถานะ completed ยังถูกใช้ประกอบ purchased-product review ตามข้อกำหนด

ก่อนเปิด PR ได้ตรวจเทียบ `origin/main` และปรับตาม WP3b ที่ merge แล้ว: job เลือก order `PROCESSING` ที่ไม่ DELETED, ไม่มี parcel `PENDING`, มีอย่างน้อยหนึ่ง `SHIPPED`, ทุก item ถูกจัดสรรครบใน `SHIPPED`/`DELIVERED` และ `SHIPPED` ที่ใหม่ที่สุดมีอายุอย่างน้อย `completion_days` (7 วัน) โดยไม่นับอายุของ `DELIVERED` parcels ค้างส่ง/ส่งบางส่วนไม่เข้าเกณฑ์

Candidate scan ต้องกรองครบทุกเงื่อนไขเพื่อไม่ให้ order ที่ไม่มีวันผ่านกิน batch จนรายการถัดไปไม่ได้ทำงาน จากนั้นหนึ่ง transaction ต่อ order: lock order ก่อน ตรวจเงื่อนไขซ้ำ เปลี่ยน `SHIPPED` เป็น `DELIVERED` ด้วย `updated_by=system` และ `delivered_at` เวลา job แล้วใช้สูตร delivered quantity เดิมเพื่อ complete ไม่คืน campaign budget งานหนึ่ง order ล้มเหลวไม่หยุด order อื่น และรันซ้ำไม่ทำสิ่งที่เสร็จแล้วซ้ำ Hosting/batch size/schedule ยังเป็นค่าที่ต้องกำหนดตาม specification

ถ้า job ชนะการแข่งขันกับ owner confirm หรือร้านที่ขอ `RETURNED`, คำขอที่มาทีหลังตรวจ state ใหม่และอาจได้ `409` เพราะ `DELIVERED` เป็น final การอัปเดตภาพนี้สะท้อน specification ที่ merge แล้ว ไม่ใช่เพิ่ม job implementation

### 3.5 `CANCELLED` — ยกเลิกก่อนรับชำระ

ตาม [sales/05-cancel-order](../../doc/api/sales/05-cancel-order/spec.md) owner, ACTIVE shop member หรือ platform admin ตามสิทธิ์เรียก cancel ได้ และ system ใช้กฎเดียวกันสำหรับ expiry เฉพาะ order `WAIT_PAYMENT`

ถ้ามี payment `PROCESSING` ต้องปฏิเสธ/เลื่อน expiry เพราะเงินอาจกำลังมา หาก payment `PENDING` ให้จัดการยกเลิก PaymentIntent ตาม spec แล้วคืนจำนวนแต่ละ item ไป original `lot_id` แม้ lot ไม่ on sale แล้ว คืน campaign reservation และเพิ่ม `RELEASE` ledger โดยคง order/items เป็นประวัติ

เหตุผลที่คืน original lot คือ stock history และต้นทุนต้องตรงแหล่งเดิม ไม่ย้ายไป lot ที่กำลังขายอยู่โดยอัตโนมัติ Cancel ซ้ำตอบ `409` ตาม spec แต่ผลลัพธ์ทางธุรกิจคงเดิมและไม่คืน stock/budget ซ้ำ ความหมายนี้ต่างจากการรับประกันว่า retry ทุกครั้งต้องตอบ HTTP success

### 3.6 `REFUNDED` — คืนเงินก่อนเริ่ม fulfillment

ตาม [payment/05-refund-payment](../../doc/api/payment/05-refund-payment/spec.md) payment ต้อง `COMPLETED`, order ต้อง `PAYMENT_CONFIRMED` และผู้เรียกเป็น ACTIVE shop member หรือ platform admin ลูกค้าไม่ได้เรียก refund นี้เอง เป็น full refund รวม shipping fee ไม่ใช่ partial refund/return workflow

เมื่อสำเร็จ payment/order เป็น `REFUNDED`, stock กลับ original lots และคืน campaign budget ครั้งเดียว หรือ signed refund webhook อาจทำผลตาม guard เดียวกัน การที่ order เคย `PROCESSING` ไม่ได้เปิด refund ตรง ๆ ต้องเข้า recovery condition ที่อธิบายด้านล่างก่อน

เหตุผลคือเมื่อเริ่ม fulfillment แล้ว ระบบต้องรู้ว่าของที่ส่งไปอยู่ที่ใดก่อนคืน stock การอนุญาต refund โดยไม่พิจารณา parcels อาจทำให้เงินคืนและ stock ถูกเพิ่มทั้งที่สินค้ายังเดินทางอยู่

## 4. แปด transitions พร้อม actors, guards และเหตุผล

| เส้นในภาพ | ผู้กระตุ้น/เหตุการณ์ | Guard และผลสำคัญ | เหตุผล |
| --- | --- | --- | --- |
| จุดเริ่ม → `WAIT_PAYMENT`: `CREATE` | Logged-in customer checkout | Cart/address/visibility/stock/budget ถูกต้อง; snapshot/reserve ใน SQL transaction | ไม่สร้าง order ที่ไม่มีสิทธิ์หรือทรัพยากรไม่พอ |
| `WAIT_PAYMENT` → `PAYMENT_CONFIRMED`: `WEBHOOK OK` | Verified Stripe success | Guard order/payment; stock ยัง held | ใช้ provider event และ SQL เป็นตัวตัดสินเงิน |
| `PAYMENT_CONFIRMED` → `PROCESSING`: `FIRST PARCEL` | Shop member/admin สร้าง parcel แรก | สิทธิ์และ assigned quantities ผ่าน; parcel `PENDING` | ระบุจุดเริ่ม fulfillment ชัดเจน |
| `PROCESSING` → `COMPLETED`: `ALL DELIVERED` | Owner ยืนยันรับ parcel หรือ eligible system job | Parcel จาก `SHIPPED`; delivered quantity ครบทุก item; job ตรวจเงื่อนไข 7 วันทั้งหมด | ไม่จบ order เพราะส่งเพียงบางส่วน |
| `WAIT_PAYMENT` → `CANCELLED`: `EXPIRE/CANCEL` | Owner/shop/admin หรือ system expiry | Payment ต้องไม่ `PROCESSING`; คืน lot/budget ครั้งเดียว | ปล่อยทรัพยากรที่จองเมื่อเลิกซื้อ |
| `PAYMENT_CONFIRMED` → `REFUNDED`: `FULL REFUND` | Authorized refund หรือ valid refund event | Completed payment และ order guard ตาม spec | คืนเงินและทรัพยากรสัมพันธ์กัน |
| `PROCESSING` → `PAYMENT_CONFIRMED`: `NO LIVE PARCEL` | Cancel/return parcels | หลัง update ไม่มี parcel `PENDING`, `SHIPPED` หรือ `DELIVERED` เลย; ทำใน transaction เดียว | เปิดทางส่งใหม่หรือคืนเงินเมื่อไม่มี parcel ที่ถือ allocation อยู่ |
| `WAIT_PAYMENT` → ตัวเอง: `PAYMENT RETRY` | ลองชำระอีกครั้งตาม payment contract | Payment failure/cancellation ไม่เปลี่ยน order; ยังต้องผ่าน expiry/live-payment guards | ไม่สร้าง order state เพิ่มเพียงเพราะ payment attempt ล้มเหลว |

เส้น retry เป็นการสรุป payment attempts ไม่ได้แปลว่าทุกคำขอสร้าง PaymentIntent ใหม่ [payment/01-start-payment](../../doc/api/payment/01-start-payment/spec.md) อาจ reuse `PENDING` intent ที่ method ตรงกัน, เปลี่ยนวิธีแล้ว cancel/create ใหม่ หรือปฏิเสธเมื่อกำลัง `PROCESSING`

Recovery `NO LIVE PARCEL` ต้องไม่มี `DELIVERED` parcel ด้วย ถ้าส่งถึงผู้รับบางส่วนแล้วจะย้อนกลับไป paid phase เพียงเพราะ parcel ที่เหลือ return ไม่ได้ กฎนี้ตรวจจาก [shipping/02-update-shipping-status](../../doc/api/shipping/02-update-shipping-status/spec.md)

## 5. ขอบเขต transaction และ invariants

Invariant คือเงื่อนไขที่ต้องคงจริงแม้ requests/events มาพร้อมกัน ภาพสรุปไว้ แต่ SQL และรายละเอียดทุก failure branch ยังต้องอ่านจาก specs

| Invariant | วิธีตามแบบปัจจุบัน | เหตุผล |
| --- | --- | --- |
| Stock ไม่ถูกขาย/คืนซ้ำ | Conditional stock updates, order/status guards และ original lot references | การอ่าน stock ก่อนแล้วค่อยเขียนโดยไม่ guard แข่งกันได้ |
| Budget ไม่ติดลบและไม่ release ซ้ำ | Reserve พร้อม stock, ledger `RESERVE`/`RELEASE` และเงื่อนไขคืน | ส่วนลดมีทรัพยากรจำกัดเหมือน stock |
| จำนวน assigned ไม่เกิน item | Lock order ก่อนตรวจยอด parcels | ป้องกันสอง requests ใช้ remaining quantity เดียวกัน |
| Event ซ้ำไม่ย้อน final state | Guard payment/order state และ provider idempotency | Provider delivery อาจซ้ำ/สลับลำดับ |
| ประวัติซื้อไม่เปลี่ยนตาม master | Price/address snapshots | ต้องอธิบายธุรกรรมเดิมจากข้อมูลเดิมได้ |

เส้นทางที่แก้ order เดิมใช้ lock order row ก่อน แล้วเมื่อเกี่ยวข้องค่อย lots ตาม `id` และ budgets ตาม `id` สำหรับ checkout ที่ยังสร้าง order ใหม่ spec ระบุ lots ตาม `id` แล้ว budgets ตาม `id` ไม่ได้มี existing order row ให้ lock แบบ cancel/refund การเรียง lock ลดวงจรรอกัน แต่ไม่ใช่คำรับประกันว่า implementation จะไม่มี deadlock ทุกชนิด

คำว่า “transaction เดียว” ใน specs หมายถึงขอบเขตการเขียน PostgreSQL ตามนั้น ไม่ทำให้ Stripe API call เป็น PostgreSQL participant จึงยังต้องใช้ provider idempotency และรับมือผลตอบกลับไม่ชัดเจน

## 6. เหตุการณ์ผิดปกติที่ต้องตีความให้ถูก

### Payment ล้มเหลวหรือผู้ใช้ปิดหน้าจอ

Payment attempt อาจ `FAILED`/`CANCELLED` แต่ order คง `WAIT_PAYMENT` จน payment success หรือ cancel/expiry มีผล การปิด browser ไม่ใช่คำสั่งคืน stock อัตโนมัติ ลูกค้ายังลองชำระตาม guards ของ start-payment ได้

### เงินมาหลัง cancel/expiry

ถ้า order ถูก cancel และคืน stock/budget ไปแล้ว success event ที่มาทีหลังต้องเข้าสาย late-payment refund ตาม webhook contract ไม่คืน stock/budget อีกและไม่เปิด order เดิมกลับเป็น paid เหตุผลคือทรัพยากรนั้นอาจถูกขายให้คนอื่นแล้ว

### Refund event มาหลังเริ่มส่ง

Webhook อาจอัปเดต payment เป็น refunded แต่ถ้า order ไม่อยู่ `PAYMENT_CONFIRMED` จะไม่คืน stock/เปลี่ยน order เป็น refunded โดยอัตโนมัติ และต้องมีคนติดตามตาม contract ภาพจึงไม่วาดเส้นทั่วไปจาก `PROCESSING`/`COMPLETED` ไป `REFUNDED`

### ส่งไม่ครบหรือมี parcel กลับ

Order อยู่ `PROCESSING` จน delivered quantity ครบ หรือกลับ paid phase เมื่อเข้าเงื่อนไขไม่มี live parcel ทั้งหมด การมี parcel หนึ่งถูก return ไม่ใช่เหตุผลพอให้คืนเงินทั้ง order เสมอไป

## 7. แยก business lifecycle จาก publication lifecycle

ภาพนี้เปลี่ยนชื่อจาก `system-design` เป็น `order-lifecycle` ตาม handoff และรับผิดชอบเฉพาะ Order states, actors, guards และ business effects รายละเอียด cache/admission/config ย้ายไปอ่าน [Architecture](architecture-design.md), [Redis design](../design/redis-design.md) และ [MongoDB design](../design/mongodb-design.md) โดยไม่คงรายละเอียดเหล่านั้นเป็นกล่องในภาพนี้

Publication states เช่น `READY`, `CLAIMED`, `DELIVERED` ไม่ใช่สถานะ Order อ่าน [Event outbox lifecycle](event-outbox-design.md) และ [Outbox delivery sequence](outbox-delivery-sequence.md) สำหรับ proposed publication controls การส่ง event ซ้ำไม่ใช่ checkout ซ้ำหรือ stock/budget reservation รอบใหม่

## 8. ตัวอย่างตามรอยเหตุการณ์

**ซื้อสำเร็จ:** checkout จอง stock/budget และสร้าง `WAIT_PAYMENT` → start payment → verified success ทำ `PAYMENT_CONFIRMED` → ร้านสร้าง parcel แรกเป็น `PROCESSING` → ส่งหลาย parcels → owner ยืนยันครบ หรือ system job ผ่านเกณฑ์ 7 วันเป็น `COMPLETED`

**ยกเลิกแล้วเงินมาช้า:** cancel ที่ guard ผ่านทำ `CANCELLED` พร้อมคืน original lots/budget → success event มาทีหลัง → late-payment refund โดยไม่คืนทรัพยากรซ้ำ

**parcel ทั้งหมดกลับ:** order `PROCESSING` → หลัง cancel/return ไม่เหลือ `PENDING`/`SHIPPED`/`DELIVERED` → กลับ `PAYMENT_CONFIRMED` → เลือกส่งใหม่หรือ authorized full refund หากยังผ่าน guards การกลับ paid phase ไม่ได้จอง stock ใหม่

## 9. แหล่งอ้างอิงและขอบเขตที่ยังเปิดอยู่

หลักฐาน business transitions คือ [sales/02](../../doc/api/sales/02-create-order/spec.md), [sales/05](../../doc/api/sales/05-cancel-order/spec.md), [payment/01](../../doc/api/payment/01-start-payment/spec.md), [payment/02](../../doc/api/payment/02-stripe-webhook/spec.md), [payment/05](../../doc/api/payment/05-refund-payment/spec.md), [shipping/01](../../doc/api/shipping/01-create-shipping/spec.md), [shipping/02](../../doc/api/shipping/02-update-shipping-status/spec.md) และ [shipping/06](../../doc/api/shipping/06-confirm-delivery/spec.md) โดย campaign effects อ่านร่วมกับ [campaign design](../../../docs/superpowers/specs/2026-11-06-campaign-design.md)

การจัดภาพและ semantic model อยู่ใน [diagram-semantics.md](../design/diagram-semantics.md)/[layered_lifecycle_content.py](../scripts/layered_lifecycle_content.py) ส่วน proposed delivery controls อยู่ในเอกสารแยกตามหัวข้อ 7 ยังไม่ใช่ implementation ที่ทดสอบแล้ว ภาพไม่ได้ครอบคลุม partial refund, product-return workflow เต็มรูปแบบ, carrier integration หรือรายละเอียดการติดตั้ง automatic completion worker งานอธิบายนี้ไม่เปลี่ยน API/schema/code และไม่ได้รัน provider/load/concurrency tests

## รูปแบบภาพที่ปรับตามความหมาย

กล่องใหญ่หกกล่องคือ persisted order states ตาม SQL ส่วนกล่องเล็ก `ENTRY / ACTOR`, `EVENT / GUARD`, `SQL EFFECT`, `FULFILMENT EFFECT` และ `EFFECT / IDEMPOTENCY` เป็น **compartments อธิบายเงื่อนไข/ผล** ภายใน state ไม่ใช่ nested persisted states ใหม่ ภาพนี้ไม่มีกล่อง data-service controls เพื่อแยก business states ออกจาก infrastructure/publication concerns

ลูกศรหลักย่อเป็น `PAID` (signed success และ guard ผ่าน), `SHIP` (สร้าง parcel แรก), `DONE` (ส่งครบภายใต้ receiver/system gate) เพื่อไม่ให้ label ชนขอบ state ส่วน `EXPIRE/CANCEL`, `REFUND`, `RETRY`, `NO LIVE PARCEL` คง event/guard ของทางเลือก การวางเส้นเหนือ/ใต้รางหลักแยก retry/recovery/terminal outcome ตามความหมาย ไม่ใช่การแบ่ง software layer

Native draw.io ใช้ state parent และ guard/effect child จริง รวมหก state parent containers กับสิบสอง guard/effect child compartments ตรวจทั้งโครงสร้างและรูปที่ render ก่อนส่ง รูปแบบ/เหตุผลร่วมอยู่ใน [diagram-semantics.md](../design/diagram-semantics.md)

[กลับสารบัญ diagram](../README.md)
