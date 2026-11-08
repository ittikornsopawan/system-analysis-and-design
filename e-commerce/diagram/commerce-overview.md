---
name: E-commerce Capability Ownership Map
description: อธิบายขอบเขตเจ้าของความสามารถทางธุรกิจและกล่องย่อยใน commerce-overview ใช้อ่านก่อนทบทวนภาพรวมหรือเชื่อมความรับผิดชอบกับ API specs
status: in-review
approved_by: null
approved_at: null
---

# แผนที่ความสามารถและขอบเขตความรับผิดชอบ

ภาพนี้ตอบว่า **ความสามารถใดอยู่ภายในขอบเขตธุรกิจใด** ใช้ notation แบบ nested ownership โดยมี parent/child ที่แก้ไขแยกกันได้ใน draw.io ไม่ใช้ลูกศรเรียงเป็น customer journey การวาง Access ทางซ้ายจึงไม่ได้บังคับให้ลูกค้าต้อง login ก่อน browse และแต่ละขอบเขตไม่ได้หมายถึง microservice หรือ deployment แยกตัว

## โครงสร้างที่เห็นในภาพ

กรอบนอก `E-commerce responsibility map` ครอบขอบเขตห้าชุด โดยมี capability เป็นกล่องลูกจริง:

| ขอบเขต | กล่องความสามารถภายใน | เจ้าของข้อเท็จจริง |
| --- | --- | --- |
| Access | Identity & sessions; Live permission | PostgreSQL session และ permission; Authen มี code subset ห้า use cases |
| Merchandise | Catalog & listings; Inventory; Public metadata | SQL เป็นเจ้าของ visibility, ราคา และ stock; cache ข้อมูลสาธารณะเป็นข้อเสนอ |
| Platform operations | Platform governance; Operating controls | Master data/roles/campaigns ตาม spec; config, outbox และ operational controls ยังอยู่ระหว่างทบทวน |
| Ordering & fulfilment | Cart selection; Checkout & campaigns; Shipping & completion; Purchase history & review | SQL transaction, lots, campaign budget, parcels และสิทธิ์ review ตาม API spec ของแต่ละส่วน |
| Payments | Payment & signed events; Refund & reconciliation | Provider effect ต้องตรวจเทียบกับ SQL guards; MongoDB copy ไม่ตัดสินเงิน |

Checkout เป็นจุดเน้นเพราะการสร้าง order ของทุก selected shop, reservation และข้อมูล snapshot ต้องสำเร็จหรือ rollback ร่วมกัน รายละเอียด SQL อยู่ใน API spec ไม่ย้ายมาแทนด้วยกล่องสรุปในภาพ

## เหตุผลและข้อแลกเปลี่ยน

การใช้กล่องครอบสื่อ ownership ได้ตรงกว่าลูกศร Browse → Pay → Review ซึ่งอาจถูกอ่านเป็นลำดับบังคับ การแยก Public metadata ออกจาก Catalog ทำให้เห็นว่า cache มีสิทธิ์เก็บเพียง public text และยังต้องตรวจ eligibility ที่ SQL การรวม governance ไว้ในขอบเขต operations แสดงความสามารถข้าม domain โดยไม่ทำให้ feature flag กลายเป็นสิทธิ์อนุญาต

ภาพนี้ไม่แสดง call order, state transitions หรือ transaction boundary ทุกกรณี ต้องอ่าน [checkout sequence](checkout-sequence.md), [payment webhook sequence](payment-webhook-sequence.md) และ [system lifecycle](system-design.md) เมื่อคำถามเป็นเรื่องพฤติกรรมตามเวลา

## ความล้มเหลวที่ต้องไม่ตีความผิด

- Cache หมดอายุหรือ MongoDB copy ล่าช้าไม่เปลี่ยน stock, permission หรือสถานะเงินที่ SQL เป็นเจ้าของ
- Projection สำหรับ operational search ไม่ใช่ประวัติครบถ้วน และไม่ให้สิทธิ์ customer/shop อ่านข้อมูลเพิ่มเติม
- Stripe timeout อาจมีผลเงินจริงแล้ว จึงต้อง reconciliation; ไม่ตีความว่า rollback SQL ย้อน provider effect ได้
- งาน shipping ใช้ข้อมูล carrier/tracking ที่ shop กรอก ภาพไม่ได้สร้าง carrier API หรือ broker ขึ้นใหม่

## แหล่งข้อมูลและสถานะ

- [Project structure](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/project-structure.md) และ [runtime architecture](architecture-design.md) สำหรับ implemented subset และ backend เดียว
- [Create order](../doc/api/sales/02-create-order/spec.md), [start payment](../doc/api/payment/01-start-payment/spec.md), [signed webhook](../doc/api/payment/02-stripe-webhook/spec.md)
- [Create shipping](../doc/api/shipping/01-create-shipping/spec.md), [confirm delivery](../doc/api/shipping/06-confirm-delivery/spec.md)
- [MongoDB design](mongodb-design.md), [Redis design](redis-design.md), [supporting operations research](supporting-data-operations-research.md)

เอกสารและภาพเป็นงานออกแบบที่ `in-review` ไม่อนุมัติ schema, endpoint, worker หรือ runtime implementation เพิ่มเติม การตรวจรอบนี้ครอบคลุม ownership และ traceability; ไม่ใช่ runtime/load/security proof
