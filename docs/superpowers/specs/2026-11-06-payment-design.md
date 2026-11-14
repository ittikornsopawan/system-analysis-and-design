---
name: "Payment Design WP2"
description: "ออกแบบการชำระเงินผ่าน Stripe (WP2): บัตรเครดิตและ PromptPay รับผลทาง webhook คืนเงินเต็มจำนวน ค่าส่งและลำดับล็อกออเดอร์ กติกา R51-R72 อ่านก่อนแก้ API payment"
status: in-review
approved_by: null
approved_at: null
---

# ชำระเงิน (payment) — WP2

วันที่: 2026-11-06 · สถานะ: ทำตามคำสั่งของเจ้าของงาน ("เริ่มทำ payment ได้เลย", ต่อ Stripe) การตัดสินใจระหว่างทางรอตรวจ (หัวข้อสุดท้าย)

ต่อจาก [สั่งซื้อ](2026-11-06-order-design.md) (WP1) ออเดอร์เกิดที่สถานะ `WAIT_PAYMENT` และถือสต็อกจนถึง `expires_at` payment คือขั้นที่เปลี่ยนออเดอร์เป็น `PAYMENT_CONFIRMED` หรือคืนเงินกลับ

## เป้าหมาย

- ลูกค้าเริ่มชำระเงินของออเดอร์ที่รอจ่ายผ่าน Stripe (บัตรเครดิต และ PromptPay)
- ระบบรับผลจาก Stripe ทาง webhook แล้วเปลี่ยนสถานะ payment และออเดอร์ ผลจากฝั่งหน้าเว็บไม่ถูกเชื่อ
- ลูกค้าและร้านดูรายการชำระเงิน ร้านคืนเงินเต็มจำนวนของออเดอร์ที่ยังไม่เริ่มจัดส่ง

## ไม่ใช่เป้าหมาย

- PayPal โอนเงินธนาคาร เก็บเงินปลายทาง (ค่าเหล่านี้อยู่ใน enum ของ schema แต่ spec ปฏิเสธด้วย 400 จนกว่าจะมีงานรองรับ)
- คืนเงินบางส่วน คืนเงินหลังเริ่มจัดส่งหรือหลังรับของ (ต้องมีกระบวนการคืนสินค้า ซึ่งอยู่นอก WP2 และ WP3)
- ค่าธรรมเนียม Stripe การโอนเงินให้ร้าน (payout) การกระทบยอดบัญชี
- การเก็บหรือรับข้อมูลบัตร ข้อมูลบัตรไม่ผ่านระบบเรา (Stripe.js ส่งตรงไป Stripe)
- งานตัวตั้งเวลา (job) ที่ยกเลิกออเดอร์หมดเวลา spec เขียนแค่กติกา

## ผลงาน

- Schema: `payment.t_payment` เพิ่มคอลัมน์ผู้ให้บริการ ความล้มเหลว การคืนเงิน, `order_id` เป็น `RESTRICT`, constraint และ partial unique index (migration `07`, schema doc, README, ER diagram หน้า 6 และ 8, แบบทดสอบ `db/tests/07-payment.test.sql`)
- Spec ใน `e-commerce/doc/api/payment/`: `01-start-payment`, `02-stripe-webhook`, `03-inquiry-payment`, `04-inquiry-shop-payment`, `05-refund-payment`
- แก้ `sales/05-cancel-order` ให้ยกเลิก payment ที่ค้างอยู่ด้วย (R59) และข้อความค่าส่งใน `sales/01`, `sales/02` (R67)
- ตัวตรวจ `check_docs.py payment-spec` และ `payment-schema`

## ข้อเท็จจริงของ Stripe ที่ใช้ และสถานะการตรวจสอบ

โฟลเดอร์ `e-commerce/doc/external-api/stripe` ว่าง spec นี้จึงอ้างเอกสาร Stripe ตรงๆ

| ข้อเท็จจริง | สถานะ |
|---|---|
| ใช้ PaymentIntent หนึ่งตัวต่อหนึ่งความพยายามจ่าย ได้ `client_secret` ให้ Stripe.js ฝั่งหน้าเว็บ | ความรู้ทั่วไปของ API ยังไม่ได้เปิดตรวจกับหน้า doc |
| จำนวนเงินส่งเป็นหน่วยย่อยของสกุลเงิน THB คือสตางค์ (บาท × 100) | ความรู้ทั่วไปของ API |
| ขั้นต่ำต่อรายการ THB 10.00 | พบในหน้า Supported currencies แต่เป็นสำเนาเก่า ต้องตรวจกับหน้าสดหรือลองใน test mode |
| PromptPay สูงสุด 2,000,000 บาทต่อรายการ | พบใน FAQ ของ Stripe |
| ลายเซ็น webhook อยู่ใน header `Stripe-Signature` ต้องใช้ raw body ความคลาดเคลื่อนเวลา 5 นาที (ค่าเริ่มต้นของไลบรารี) | ยืนยันจากหน้า Webhooks |
| ชื่อ event `payment_intent.succeeded`, `payment_intent.payment_failed`, `payment_intent.canceled`, `charge.refunded` | ยังไม่ยืนยัน ต้องเทียบกับ Event types reference ก่อน implement |
| header `Idempotency-Key` กันการสร้างซ้ำ | ความรู้ทั่วไปของ API |

## การตัดสินใจระหว่างทาง (รอเจ้าของงานตรวจ)

- R51 ใช้ Stripe ผู้ให้บริการเดียวผ่าน PaymentIntent (เจ้าของงานบอกว่าอยากต่อ Stripe) รองรับ `CREDIT_CARD` (card) และ `THAI_QR` (PromptPay) เท่านั้น ค่าอื่นใน enum ตอบ 400 คอลัมน์ `provider` มีค่าเดียว `STRIPE` เพื่อเพิ่มผู้ให้บริการทีหลังได้โดยไม่ย้ายข้อมูล ถ้าผิด: เพิ่มค่าใน CHECK ของ `provider` และ endpoint webhook ของผู้ให้บริการนั้น
- R52 หนึ่งแถว `t_payment` คือหนึ่ง PaymentIntent ชำระใหม่หลังล้มเหลวคือสร้างแถวใหม่ (ประวัติความพยายามอยู่ครบ) ออเดอร์หนึ่งมีแถวที่ยังมีผล (`PENDING`, `PROCESSING`, `COMPLETED`) ได้ไม่เกินหนึ่ง บังคับด้วย partial unique index ถ้าผิด: ต้องเลิก index แล้วคุมในแอป
- R53 การแปลงสถานะ Stripe เป็นของเรา: `requires_payment_method` ก่อนเคยลอง, `requires_confirmation`, `requires_action` → `PENDING`; `processing` → `PROCESSING`; `succeeded` → `COMPLETED`; `payment_failed` → `FAILED`; `canceled` → `CANCELLED`; คืนเงินเต็มจำนวน → `REFUNDED` สถานะที่จบแล้ว (`COMPLETED` ไม่นับ เพราะยังคืนเงินได้) คือ `FAILED`, `CANCELLED`, `REFUNDED` และห้ามย้อน
- R54 เริ่มชำระ: เจ้าของออเดอร์เท่านั้น ออเดอร์ต้อง `WAIT_PAYMENT` และยังไม่ถึง `expires_at` จำนวนเงินคำนวณฝั่งเซิร์ฟเวอร์เสมอจากรายการของออเดอร์บวกค่าส่ง (R67) ไม่รับจากคำขอ ถ้าออเดอร์มีแถว `PENDING` อยู่แล้ว: วิธีจ่ายเดิม → คืนแถวเดิมพร้อม client secret ใหม่จาก Stripe (200); วิธีจ่ายต่าง → ยกเลิกแถวเดิมที่ Stripe แล้วสร้างแถวใหม่ (201); แถว `PROCESSING` → 409 (E10006) ถ้าผิด: ตัดการสลับวิธีจ่ายออก
- R55 `client_secret` คืนให้ผู้เรียกตอนเริ่มชำระ ไม่เก็บในฐานข้อมูล (ดึงใหม่จาก Stripe ได้) ถ้าผิด: ไม่มีผลต่อ schema
- R56 webhook คือแหล่งความจริงของผลชำระ หน้าเว็บที่ redirect กลับมาไม่ถูกเชื่อ endpoint เป็น public ไม่มี `authorization` ป้องกันด้วยลายเซ็น `Stripe-Signature` (raw body, ความคลาดเคลื่อน 5 นาที) ลายเซ็นผิด → 400 (E10001) event ที่ไม่รู้จักหรือไม่ใช่ของเรา → 200 ไม่ทำอะไร (ไม่ให้ Stripe ส่งซ้ำ) ประมวลผลซ้ำได้โดยผลเท่าเดิม (idempotent ตามสถานะ) ไม่มีตารางเก็บ event ถ้าผิด (อยากเก็บ event ดิบเพื่อตรวจสอบ): เพิ่มตาราง `t_payment_event` unique ที่ `event id`
- R57 เงินเข้าหลังออเดอร์ไม่ใช่ `WAIT_PAYMENT` แล้ว (เช่นหมดเวลาและถูกยกเลิกไปก่อน) หรือ payment นั้นเป็น `FAILED`/`CANCELLED` ไปแล้ว: ระบบสั่งคืนเงินเต็มจำนวนทันทีและตั้ง payment เป็น `REFUNDED` โดยตรง (ไม่ผ่าน `COMPLETED` เพราะ index ที่คุมหนึ่ง payment ที่มีผลต่อออเดอร์จะชนกับ payment ใหม่ที่ลูกค้าเริ่มไว้) ออเดอร์คงเดิมและไม่คืนสต็อกซ้ำ เงินลูกค้าถูกตัดจริงชั่วคราวจึงต้องรายงานให้เจ้าของงานรู้ ถ้าผิด: ต้องมีสถานะ "รอตรวจสอบ" ให้คนตัดสิน
- R58 คืนเงิน: เต็มจำนวนเท่านั้น ผู้สั่งคือสมาชิก ACTIVE ของร้านหรือ `PLATFORM_ADMIN` (ลูกค้าสั่งเองไม่ได้ ต้องขอร้าน) ทำได้เมื่อ payment `COMPLETED` และออเดอร์ `PAYMENT_CONFIRMED` เท่านั้น ผลคือ payment `REFUNDED`, ออเดอร์ `REFUNDED` และจำนวนของทุกรายการกลับเข้า lot เดิม (เหมือนยกเลิก) ข้อตกลงกับ WP3: การสร้างการจัดส่งแรกต้องเปลี่ยนออเดอร์เป็น `PROCESSING` ในธุรกรรมเดียวกัน จึงคืนเงินหลังเริ่มจัดส่งไม่ได้ (409 E10006) แต่เมื่อร้านยกเลิกหรือพัสดุตีกลับครบทุกพัสดุ shipping จะคืนออเดอร์เป็น `PAYMENT_CONFIRMED` (S9 ของ shipping เจ้าของงานอนุมัติแล้ว) และคืนเงินได้อีกครั้ง ถ้าผิด (อยากให้คืนได้หลังจัดส่ง): ต้องมี WP คืนสินค้า และกติกาเรื่องสต็อก
- R59 ยกเลิกออเดอร์ (API และตัวตั้งเวลา) ต้องยกเลิก payment `PENDING` ที่ค้างอยู่ที่ Stripe ด้วย และ payment เป็น `CANCELLED` ถ้ามี payment `PROCESSING` ยกเลิกออเดอร์ไม่ได้ (409 E10006) และตัวตั้งเวลาข้ามออเดอร์นั้น เพราะเงินอาจกำลังเข้า spec `sales/05-cancel-order` ถูกแก้ตามนี้
- R60 payment `FAILED` ไม่เปลี่ยนออเดอร์ (ยัง `WAIT_PAYMENT` ลูกค้าลองใหม่ได้จนถึง `expires_at`) และยกเลิก PaymentIntent เดิมที่ Stripe แบบพยายามให้ (best effort)
- R61 ข้อมูลที่เก็บเพิ่ม: `provider_payment_id` (id ของ PaymentIntent, unique), `currency` (`THB`), `failure_code`/`failure_message`, `provider_refund_id`, `refunded_at`, `refund_reason` ไม่เก็บข้อมูลบัตรใดๆ `payment_name` เก็บป้ายแสดงผล เช่น `Visa •••• 4242` หรือ `PromptPay` `transaction_code` เก็บ id ของ charge ที่สำเร็จ ถ้าผิด: ลบคอลัมน์ที่เพิ่มได้โดยไม่กระทบอย่างอื่น
- R62 `order_id` เปลี่ยนเป็น `ON DELETE RESTRICT` เพราะเป็นประวัติการเงิน และ unique ของ `transaction_code`, `provider_payment_id`, `provider_refund_id` เป็น unique ธรรมดา (ไม่ใช่ partial) เพราะแถว payment ไม่ถูกลบแบบ soft ไม่มีเส้น API ลบ ถ้าผิด: เปลี่ยนเป็น partial unique
- R63 ส่ง `Idempotency-Key` ไป Stripe: ตอนสร้าง PaymentIntent ใช้ id ของแถว payment ตอนคืนเงินใช้ `refund-<id ของแถว payment>` เพื่อกันการเรียกซ้ำจาก retry หรือกดซ้ำ
- R64 ผู้ใช้เห็นอะไร: ลูกค้าเห็นรายการของตัวเอง รวม `failureMessage`; ร้านเห็นรายการของออเดอร์ร้านตัวเอง (สมาชิก ACTIVE หรือ `PLATFORM_ADMIN`, ไม่ใช่ → 403 E10009); `providerPaymentId` และ `providerRefundId` เห็นเฉพาะ `PLATFORM_ADMIN` (คืน null ให้คนอื่น คงคีย์ไว้) ตามแนวซ่อนฟิลด์ของโปรเจกต์
- R65 ขั้นต่ำและสูงสุด: จำนวนเงินต่ำกว่า 10.00 บาท หรือ PromptPay เกิน 2,000,000 บาท → 409 (E10006) พร้อมข้อความ ค่านี้เป็น config ไม่ฝังใน schema (ดูตารางข้อเท็จจริงด้านบนว่ายังต้องตรวจ)
- R66 bizCode: ใช้ชุดเดิม ไม่สร้างรหัสใหม่ E10001 ลายเซ็น/คำขอผิด, E10003 ไม่ใช้, E10004 ไม่พบออเดอร์หรือ payment, E10006 สถานะชน/มี payment ค้าง/นอกช่วงจำนวนเงิน, E10009 สิทธิ์
- R67 วิธีส่งและค่าส่งถูกกำหนดตอนเริ่มชำระ (เจ้าของงานตอบ SA ฝั่ง shipping ว่า "ได้มาจาก payment ของ josh" และยืนยันกับ Josh ในแชตแล้ว 2026-11-06) คำขอเริ่มชำระส่ง `shippingMethod` (`STANDARD`, `EXPRESS`, `SAME_DAY`) ระบบคิดค่าส่งฝั่งเซิร์ฟเวอร์แล้วเก็บ `shipping_method` และ `shipping_fee` ที่แถว `t_payment` และตั้ง `sales.t_order.total_shipping` กับ `total_amount` ในธุรกรรมเดียวกัน (สูตร `ck_t_order_total_amount_sum` ยังเป็นจริง) ยอดที่ส่งให้ Stripe คือ `total_amount` ใหม่ WP3 อ่านค่าจากแถว payment ที่ `COMPLETED` ถ้าผิด (ลูกค้าเลือกตอน checkout หรือร้านเลือกตอนส่ง): ย้ายฟิลด์ไป spec ของ sales หรือ shipping และลบสองคอลัมน์
- R68 กติกาคิดค่าส่ง เจ้าของงานยังไม่ให้ ผมตั้งเป็นค่า config อัตราคงที่ต่อออเดอร์ต่อวิธีส่ง (ไม่ฝังใน schema) ตัวเลข `STANDARD` 40.00, `EXPRESS` 80.00, `SAME_DAY` 150.00 บาท Josh เสนอเอง เจ้าของงานยืนยันให้ใช้ตัวเลขนี้แล้วในแชต 2026-11-06 และยังไม่มีส่งฟรีเมื่อยอดถึงเกณฑ์ ถ้าผิด: เปลี่ยนค่า config ไม่กระทบ schema
- R69 เริ่มชำระซ้ำ (เปลี่ยนวิธีจ่ายหรือวิธีส่ง) คำนวณค่าส่งและตั้งยอดออเดอร์ใหม่ทุกครั้ง ยอดออเดอร์ที่ `WAIT_PAYMENT` จึงเปลี่ยนได้จนกว่าจะจ่าย สถานะ payment `FAILED` หรือ `CANCELLED` ไม่คืน `total_shipping` เป็น 0 (ค่าล่าสุดค้างอยู่จนเริ่มชำระใหม่) ถ้าผิด: ต้องคืนยอดเมื่อ payment ไม่สำเร็จ
- R70 `CASH_ON_DELIVERY` ไม่รองรับใน WP2 ตอบ 400 ตอนเริ่มชำระ สัญญากับ WP3 จึงไม่มีข้อยกเว้น: การจัดส่งสร้างได้เมื่อออเดอร์ `PAYMENT_CONFIRMED` หรือ `PROCESSING` เท่านั้น ถ้าผิด (ต้องการ COD): ต้องออกแบบสถานะออเดอร์ก่อนจ่ายเงิน
- R71 คืนเงินคืนค่าส่งด้วย (เต็มจำนวนคือ `amount` ที่เก็บไว้ รวมค่าส่ง) ถ้าผิด: ต้องแยกคืนเฉพาะสินค้า
- R72 ลำดับการล็อกคือแถวออเดอร์ก่อนเสมอ (`SELECT ... FOR UPDATE` บน `sales.t_order`) แล้วค่อยแก้ payment ด้วย UPDATE ที่เช็กสถานะ ใช้ทั้งเริ่มชำระ, webhook, คืนเงิน และ WP3 (ตกลงกับ Tommy แล้วว่า shipping ล็อกแถวออเดอร์ตอนสร้างและยกเลิก) เพื่อไม่ให้ deadlock ถ้าผิด: ไม่มีผลต่อ schema
