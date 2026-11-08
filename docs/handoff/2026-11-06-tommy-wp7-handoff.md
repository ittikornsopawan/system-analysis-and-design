# Hand-off ถึง Tommy: งานถัดไป (WP7 แคมเปญและส่วนลด) และข้อตกลงใหม่

วันที่: 2026-11-06 · ผู้ส่งงาน: Josh (Lead SA) ตามที่เจ้าของงานสั่ง · ผู้รับงาน: Tommy (SA)

## ข้อตกลงใหม่ที่มีผลทันที

อ่าน [`2026-11-06-team-protocol.md`](2026-11-06-team-protocol.md) ทั้งฉบับ สรุปสิ่งที่เปลี่ยนจากที่เราทำมา:

- **ถามและรายงาน Josh เท่านั้น** ไม่รอคำตอบจากเจ้าของงานโดยตรง Josh จะรวมคำถามธุรกิจเป็นชุดไปถามและแจ้งผลกลับ
- `approved_by` ใส่ได้เมื่อ Josh แจ้งว่าเจ้าของงานอนุมัติ (ข้อความอนุมัติที่คุณได้จากเจ้าของงานก่อนหน้านี้ยังใช้ได้ตามที่บันทึกไว้)
- **คุณไม่ commit** Josh แพ็ก commit และ PR ให้เมื่อเจ้าของงานสั่ง
- งานทุกชิ้นผ่านประตู 1 (ออกแบบ) และประตู 2 (ลงมือ) ของ Josh ตามเกณฑ์ในโปรโตคอลหัวข้อ 5
- เลขข้อการตัดสินใจ: WP3 ใช้ `S` ต่อ, WP7 ใช้ `C`

## งานที่ 1: WP3 shipping (ทำต่อ)

ผลตรวจรอบ 2 ที่ผมส่งไปแล้วยังใช้ได้ทุกข้อ ยังค้าง: rebase บน payment เมื่อ payment เข้า `origin/main` (ผมจะแจ้ง) แล้วทำ ER หน้า 6 และ 8, รวม `check_docs.py`, `audit_all.py` 0 ข้อพบ และทดสอบตัวตรวจ shipping ซ้ำ แล้วรายงานประตู 2 อีกครั้ง

## งานที่ 2: WP7 แคมเปญและส่วนลด (เริ่มรอบ 1 ได้เลย ขณะรอ payment)

ตาราง 6 ตัวใน `e-commerce/db/migrations/up/09-campaign.schema.up.sql`: `m_campaign`, `m_campaign_budget`, `m_campaign_budget_ledger`, `t_campaign_product`, `t_campaign_shop`, `t_campaign_discount` ตามแผน: แคมเปญ (พร้อม budget, สินค้า, ร้าน, ส่วนลดซ้อน) upsert และ inquiry, ดู ledger, คำนวณส่วนลด

**ที่ทำงาน:** worktree ใหม่ `.claude/worktrees/campaign` branch `feat/campaign-domain` แยกจาก `origin/main` ER diagram: เซลล์ใหม่ id ขึ้นต้น `t_` (หน้า 7 Campaign และหน้า 8)

**ต้องอ่านก่อน (ไฟล์อยู่ใน checkout หลัก `/Users/ittikorn/Repositories/system-analysis-and-design` ยังไม่ merge):**

- `docs/superpowers/specs/2026-11-06-payment-design.md` (R51–R72) และ spec ใน `e-commerce/doc/api/payment/`
- `docs/superpowers/specs/2026-11-06-order-design.md` (R38–R50) และ `e-commerce/doc/api/sales/01–05`
- `docs/superpowers/plans/2026-11-06-api-roadmap.md` (WP7) และหัวข้อ "คำถามค้าง" ใน `docs/handoff/2026-11-06-shop-domain-summary.md`
- skill: `.agents/skills/data-modeling`, `.agents/skills/api-contract-design`

**รอบ 1 (เอกสารออกแบบ `docs/superpowers/specs/2026-11-0X-campaign-design.md`) ต้องตอบอย่างน้อย:**

1. **ใครสร้างแคมเปญ** แพลตฟอร์ม (`PLATFORM_ADMIN`) หรือสมาชิกร้าน หรือทั้งสอง และแคมเปญของร้านกับของแพลตฟอร์มต่างกันอย่างไร (สิทธิ์ใช้โมเดลเดิม: สมาชิก ACTIVE ของร้านหรือ `PLATFORM_ADMIN`, 403 E10009)
2. **คำนวณส่วนลดที่ไหนและอย่างไร:** เสียบใน checkout preview (`sales/01`) และสร้างออเดอร์ (`sales/02`) ลง `t_order_item.discount` และ `t_order.total_discount` สูตรเมื่อส่วนลดซ้อนหลายรายการ (`PERCENTAGE`, `FIXED_AMOUNT`), การปัดเศษ, เพดาน (ส่วนลดห้ามทำให้ยอดติดลบ และห้ามต่ำกว่าต้นทุนของ lot ถ้าเจ้าของงานยังยึดกฎห้ามขายต่ำกว่าต้นทุนที่ lot) ส่วนลดถูกล็อกในออเดอร์ตอนสร้าง ดังนั้นยอดชำระ (`amount = totalPrice - totalDiscount + totalTax + shippingFee` ของ payment) ไม่เปลี่ยนตามแคมเปญที่แก้ทีหลัง
3. **งบ (budget) และ ledger:** ตัดงบตอนสร้างออเดอร์หรือตอนจ่ายเงิน, คืนงบเมื่อออเดอร์ถูกยกเลิก (รวมหมดเวลา, `sales/05`) และเมื่อคืนเงิน (`payment/05`, webhook `charge.refunded`) รูปแบบต้องกันงบติดลบแบบเดียวกับการตัดสต็อก (`UPDATE ... WHERE remaining >= n` ในคำสั่งเดียว) และใช้ลำดับล็อกของโปรเจกต์ (ล็อกแถวออเดอร์ก่อน; ตอนสร้างออเดอร์ที่แถวยังไม่มี ให้ระบุลำดับล็อกของคุณเองให้ชัด)
4. **ใครรับภาระส่วนลดในกำไร:** `t_order_item.gross_profit`, `shop_profit`, `platform_profit` ตอนนี้คิดจาก margin ของ lot คูณจำนวนโดยไม่มีส่วนลด ส่วนลดมาจากงบแพลตฟอร์มหรือหักจากร้าน เป็นคำถามธุรกิจ (เสนอคำตอบพร้อมผลถ้าผิด)
5. **กติกาลบ:** ลบร้านที่มี `t_campaign_shop` ผูก (ค้างจาก `shop/08–09`), ลบสินค้า/lot ที่มี `t_campaign_product` ผูก, ลบแคมเปญที่มีออเดอร์ใช้ไปแล้ว และสถานะแคมเปญที่ใช้งานได้ (ช่วงเวลา, `row_status`)

**งานเดิมที่ WP7 กระทบ (ส่งมอบแล้ว):** `sales/01`, `sales/02`, `sales/05`, `payment/05`, `shop/08–09` ห้ามแก้เอง ให้เขียนเป็น "ข้อเสนอแก้งานที่ส่งแล้ว" ในเอกสารออกแบบ (แก้อะไร ทำไม กระทบ spec ไหน) แล้วให้ Josh ตัดสิน ถ้าอนุมัติ Josh จะบอกว่าให้คุณแก้เองหรือ Josh แก้

**ลำดับ:** รอบ 1 → ส่ง Josh (ประตู 1) → รอบ 2 หลังอนุมัติ ตามโปรโตคอลหัวข้อ 3

เริ่มจากรายงานสั้นๆ ว่าอ่านครบอะไรแล้ว และงาน WP3 ที่ค้างอยู่ตรงไหน ก่อนเริ่ม WP7
