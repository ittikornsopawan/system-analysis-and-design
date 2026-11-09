---
name: E-commerce Permission and Scope API Matrix
description: รวม permission, Allow Scope ในรูปแบบ scope-name:effect และ API allowlist พร้อมลิงก์ spec; อ่านก่อน review สิทธิ์ API หรือเสนอการเปิดใช้ permission/scope enforcement.
status: in-review
approved_by: null
approved_at: null
---

# Permission และ Allow Scope ของ API

เอกสารนี้ทำตามคำขอของ Ittikorn วันที่ 2026-11-09: เพิ่ม `permission-scope.md`, บอกว่า API ไหนใช้ scope ไหน และลิงก์ไปที่ spec โดยแสดง section `Allow Scope` ในรูปแบบ `<scope-name>:<effect>` เช่น `SHOP:allow` และ `ALL:deny` เจ้าของงานยืนยันว่า **deny ชนะเมื่อ permission เดียวกันครอบคลุมข้อมูลเดียวกัน** ดู [คำตัดสินที่บันทึกแล้ว](../../docs/superpowers/specs/2026-11-07-api-review-design.md)

## สถานะและขอบเขต

- สำรวจ API ที่มีอยู่ครบ **83 API**; ทำเครื่องหมาย **คิว review 40 API** ตามรายการที่ตกลงใน Peter chat รายการอื่นแสดงเพื่อให้เห็นขอบเขตและข้อยกเว้นครบทั้งระบบ
- รูปแบบ `scope-name:effect` และกฎ deny ชนะได้รับการยืนยันแล้ว แต่ **การจับคู่ permission/API และนิยาม scope ที่เสนอเพิ่มยัง in-review** ตารางนี้ไม่ใช่หลักฐานว่า endpoint, JWT หรือฐานข้อมูลรองรับ effect แล้ว
- [seed ปัจจุบัน](../db/seed/author.seed.sql) มี scope `ALL`, `SHOP`, `OWN`, permission 7 ชื่อและ definition 12 คู่ เป็น reference data ที่ไม่สร้าง grant ให้ผู้ใช้ ส่วน JWT ปัจจุบันเป็น permission-specific scope **allow-only** และยังไม่มี field effect; ดู [login](api/authen-and-author/02-login/spec.md) และ [refresh](api/authen-and-author/05-refresh-token/spec.md)
- กฎ role/owner/member ใน spec ยังคงเป็นกฎที่ใช้อ้างอิงระหว่าง review; API ที่ยังตรวจ caller admin จากฐานข้อมูลอยู่ต้องย้ายไปใช้ verified JWT ตาม Q2/Q4/Q10/Q13 แยกทีละ API
- PR นี้เพิ่มเอกสารรวมและแนวทาง section เท่านั้น ไม่เปลี่ยน API `spec.md`/`sequence.wsd`, seed, schema, JWT payload หรือ backend การใส่ section และการบังคับใช้จริงต้อง review spec/sequence คู่กันตามกฎ API ละหนึ่ง PR

## Allow Scope

รูปแบบคือ `<scope-name>:<effect>`; ชื่อ scope ใช้ตัวพิมพ์ใหญ่ตาม catalogue และ effect ใช้ตัวพิมพ์เล็ก การคั่นด้วย `:` เป็นรูปแบบแสดงในเอกสาร ไม่ใช่การเปลี่ยนชื่อ `m_scope.scope` ให้เป็น `SHOP:allow` และไม่ใช่รูปแบบ JWT ที่นำไปใช้ได้แล้ว

| Scope name | ตัวอย่าง                  | ครอบคลุมข้อมูลเมื่อ match                                                                                |
| ---------- | ------------------------- | -------------------------------------------------------------------------------------------------------- |
| `ALL`      | `ALL:allow`, `ALL:deny`   | ข้อมูลในขอบเขต API/permission นั้นทั้งแพลตฟอร์ม; ยังต้องผ่าน role และข้อห้ามทางธุรกิจของ endpoint        |
| `SHOP`     | `SHOP:allow`, `SHOP:deny` | ข้อมูลของร้านเป้าหมายที่ผู้เรียกเป็น ACTIVE member; ถ้า operation ต้อง ADMIN การเป็น STAFF ยังไม่พอ      |
| `OWN`      | `OWN:allow`, `OWN:deny`   | ข้อมูลที่เป็นของผู้เรียกจาก verified JWT sub ตามนิยามของแต่ละ operation ไม่ใช่ userId ที่ client อ้างเอง |

รองรับ effect ในเอกสารนี้เพียง `allow` กับ `deny` ค่า “อื่นๆ” ยังไม่ถูกนิยาม ห้ามตีความ effect ที่ไม่รู้จักเป็น allow; ต้องระบุความหมายและอนุมัติก่อนเปิดใช้ ไม่เพิ่ม scope master ชื่อ PUBLIC, SYSTEM, TOKEN หรือ `NONE` สำหรับเส้นที่ไม่ต้องใช้ scope

### กฎ allow และ deny ที่เจ้าของงานยืนยัน

1. ประเมินภายใน **permission เดียวกัน** โดยผูกกับ permissionId ของ claims ห้ามเอา `ALL:allow` ของ permission หนึ่งไปอนุญาตอีก permission
2. ตรวจว่า scope ครอบคลุม resource ที่กำลังทำงานจริง เช่น SHOP ต้อง match ร้านของ order/shipping ไม่ใช่ร้านใดก็ได้ที่ user เป็นสมาชิก ส่วน OWN ต้อง match เจ้าของข้อมูลของ operation นั้น
3. หากมี **matching deny** ให้ปฏิเสธ แม้มี matching allow หรือ role PLATFORM_ADMIN; ไม่มี admin exemption จาก explicit deny ในกฎใหม่นี้
4. หากไม่มี matching deny จึงพิจารณา matching allow; สำหรับเส้นทางที่เปิดใช้ permission enforcement แล้ว การไม่มี matching allow ไม่สร้างสิทธิ์ขึ้นมาเอง
5. การมี allow ไม่ข้ามการตรวจ token/user ปัจจุบัน, owner/member/ADMIN, สถานะธุรกิจ, การปกปิด fields หรือข้อห้ามผู้ดูแลคนสุดท้าย กฎเหล่านี้ยังต้องผ่านทุกข้อ
6. กฎข้างต้นยังไม่เพิ่ม grant requirement ให้ public, token-only, owner/bootstrap exception, reset/refresh token หรือ Stripe webhook เดิม การย้าย exception เหล่านี้ไปบังคับ grant ต้องเป็นการเปลี่ยน contract ที่อนุมัติแยก

| Permission และ resource                                | Rules ที่ได้รับ (ตัวอย่างออกแบบ)                              | ผลตามกฎใหม่                                                                |
| ------------------------------------------------------ | ------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `shipping.manage`, order ของร้าน A ที่เป็นสมาชิก       | `SHOP:allow`                                                  | ผ่าน scope; ยังต้องผ่าน role/member และ state/quantity checks              |
| `shipping.manage`, order ของร้าน A ที่เป็นสมาชิก       | `SHOP:allow`, `ALL:deny`                                      | deny เพราะ ALL ครอบคลุม order เดียวกัน                                     |
| `shipping.manage`, order ของร้าน A ที่เป็นสมาชิก       | `ALL:allow`, `SHOP:deny`                                      | deny เพราะ SHOP match ร้าน A; รวมผู้ดูแลที่มีทั้งสอง rule                  |
| `shipping.manage`, order ของร้าน B ที่ไม่ได้เป็นสมาชิก | `SHOP:allow`                                                  | ไม่มี matching allow; ห้ามใช้สมาชิกของร้าน A ไปอนุญาตร้าน B                |
| `shipping.manage`, order ของร้าน B ที่ไม่ได้เป็นสมาชิก | `ALL:allow`, `SHOP:deny`                                      | SHOP deny ไม่ match ร้าน B; ALL อาจผ่าน scope แต่ต้องผ่าน gate อื่นของ API |
| `shipping.manage`, order ของร้าน A                     | `shipping.manage` มี `SHOP:allow`; `order.read` มี `ALL:deny` | deny ของ order.read ไม่ลามไป shipping.manage                               |
| `payment.refund`, payment ของลูกค้าเอง                 | `OWN:allow`                                                   | ไม่ใช่ branch ที่ API refund อนุญาต; ลูกค้า refund เองไม่ได้               |

ตัวอย่างเป็นกฎออกแบบ ไม่ใช่ JWT ตัวอย่างที่ระบบรองรับอยู่ ห้ามแปลง allow-only claims เดิมเป็น deny โดยอนุมานจากการขาดสิทธิ์

### รูปแบบ section ที่จะใส่ใน spec แต่ละ API

```markdown
### Allow Scope

- Permission: `shipping.manage`
- Scope rules: `SHOP:allow`, `ALL:allow`
- Effect rule: matching deny ของ permission เดียวกันชนะ allow
- SHOP condition: ACTIVE member ของร้านของ order; operation ที่ต้อง ADMIN ยังต้องตรวจ ADMIN
- ALL condition: PLATFORM_ADMIN ตาม verified JWT; ไม่ข้าม matching deny เมื่อเปิดใช้ policy ใหม่นี้
- Mapping status: in-review; effect ยังไม่มีใน JWT/ฐานข้อมูลเดิม
- Reference: [permission-scope.md](../../../permission-scope.md)
```

ลิงก์ตัวอย่างเป็น relative path จาก `doc/api/<group>/<NN-name>/spec.md` ไปเอกสารนี้ เมื่อเปิดใช้จริงต้องอธิบายทั้ง allow/deny ใน sequence, error และ checker ของ endpoint ด้วย สำหรับเส้นที่ไม่ใช้ scoped grant ให้เขียน `Permission: ไม่บังคับ`, `Scope rules: ไม่ใช้ scoped grant` แล้วระบุกฎ public/token/owner/provider เดิม

## Permission และ API Allowlist

รายการด้านล่างคือ **ข้อเสนอ API allowlist สำหรับ review** ไม่ใช่การมอบสิทธิ์ให้ user/role และการมี scope definition ไม่เท่ากับได้รับ grant ตาราง API ถัดไประบุเงื่อนไขละเอียด รวม operation/field ที่ใช้ได้ใน API เดียวกัน Scope ที่ไม่อยู่ใน allowlist ไม่ถูกอนุญาตโดยอัตโนมัติ; การไม่อยู่ในรายการไม่ใช่การสร้าง explicit deny rule

### author.manage

- Permission status: มีใน seed; การผูก API ยังเป็นข้อเสนอ
- Allow Scope: `ALL:allow`
- API ที่เสนอให้ allow:
  - [author/01-upsert-role](api/author/01-upsert-role/spec.md): `ALL:allow`
  - [author/02-upsert-role-batch](api/author/02-upsert-role-batch/spec.md): `ALL:allow`
  - [author/03-inquiry-role](api/author/03-inquiry-role/spec.md): `ALL:allow`
  - [author/04-upsert-permission](api/author/04-upsert-permission/spec.md): `ALL:allow`
  - [author/05-upsert-permission-batch](api/author/05-upsert-permission-batch/spec.md): `ALL:allow`
  - [author/06-inquiry-permission](api/author/06-inquiry-permission/spec.md): `ALL:allow`
  - [author/07-upsert-scope](api/author/07-upsert-scope/spec.md): `ALL:allow`
  - [author/08-upsert-scope-batch](api/author/08-upsert-scope-batch/spec.md): `ALL:allow`
  - [author/09-inquiry-scope](api/author/09-inquiry-scope/spec.md): `ALL:allow`
  - [author/10-upsert-user-role](api/author/10-upsert-user-role/spec.md): `ALL:allow`
  - [author/11-inquiry-user-role](api/author/11-inquiry-user-role/spec.md): `ALL:allow`

### campaign.manage

- Permission status: **เสนอใหม่ ยังไม่มีใน seed**
- Allow Scope: `ALL:allow`
- Definition ที่เสนอเพิ่ม: `campaign.manage / ALL`; ยังไม่มี grant/effect ใหม่ในฐานข้อมูล
- API ที่เสนอให้ allow:
  - [campaign/01-upsert-campaign](api/campaign/01-upsert-campaign/spec.md): `ALL:allow`
  - [campaign/03-inquiry-campaign-ledger](api/campaign/03-inquiry-campaign-ledger/spec.md): `ALL:allow`

### campaign.read

- Permission status: **เสนอใหม่ ยังไม่มีใน seed**
- Allow Scope: `ALL:allow`, `SHOP:allow`
- Definition ที่เสนอเพิ่ม: `campaign.read / ALL`, `campaign.read / SHOP`; ยังไม่มี grant/effect ใหม่ในฐานข้อมูล
- API ที่เสนอให้ allow:
  - [campaign/02-inquiry-campaign](api/campaign/02-inquiry-campaign/spec.md): `SHOP:allow`, `ALL:allow`

### catalog.manage

- Permission status: มีใน seed; การผูก API ยังเป็นข้อเสนอ
- Allow Scope: `ALL:allow`
- การรวม product write 01/03 ภายใต้ catalog.manage เป็นข้อเสนอขยายการใช้ permission; seed เดิมอธิบาย master catalog เท่านั้น และยังไม่เปลี่ยน role gate
- API ที่เสนอให้ allow:
  - [product/01-upsert-product](api/product/01-upsert-product/spec.md): `ALL:allow`
  - [product/03-upsert-product-batch](api/product/03-upsert-product-batch/spec.md): `ALL:allow`
  - [product/04-upsert-product-category](api/product/04-upsert-product-category/spec.md): `ALL:allow`
  - [product/06-upsert-product-category-batch](api/product/06-upsert-product-category-batch/spec.md): `ALL:allow`
  - [product/07-upsert-product-category-attribute](api/product/07-upsert-product-category-attribute/spec.md): `ALL:allow`
  - [product/09-upsert-product-category-attribute-batch](api/product/09-upsert-product-category-attribute-batch/spec.md): `ALL:allow`
  - [product/10-upsert-product-type](api/product/10-upsert-product-type/spec.md): `ALL:allow`
  - [product/11-upsert-product-type-batch](api/product/11-upsert-product-type-batch/spec.md): `ALL:allow`
  - [product/13-upsert-product-brand](api/product/13-upsert-product-brand/spec.md): `ALL:allow`
  - [product/14-upsert-product-brand-batch](api/product/14-upsert-product-brand-batch/spec.md): `ALL:allow`
  - [shop/05-upsert-shop-type](api/shop/05-upsert-shop-type/spec.md): `ALL:allow`
  - [shop/06-upsert-shop-type-batch](api/shop/06-upsert-shop-type-batch/spec.md): `ALL:allow`

### consent.manage

- Permission status: มีใน seed; การผูก API ยังเป็นข้อเสนอ
- Allow Scope: `ALL:allow`
- API ที่เสนอให้ allow:
  - [consent/02-upsert-consent](api/consent/02-upsert-consent/spec.md): `ALL:allow`
  - [consent/03-inquiry-consent](api/consent/03-inquiry-consent/spec.md): `ALL:allow`
  - [consent/06-upsert-consent-type](api/consent/06-upsert-consent-type/spec.md): `ALL:allow`
  - [consent/07-upsert-consent-type-batch](api/consent/07-upsert-consent-type-batch/spec.md): `ALL:allow`

### order.cancel

- Permission status: **เสนอใหม่ ยังไม่มีใน seed**
- Allow Scope: `ALL:allow`, `OWN:allow`, `SHOP:allow`
- Definition ที่เสนอเพิ่ม: `order.cancel / ALL`, `order.cancel / OWN`, `order.cancel / SHOP`; ยังไม่มี grant/effect ใหม่ในฐานข้อมูล
- API ที่เสนอให้ allow:
  - [sales/05-cancel-order](api/sales/05-cancel-order/spec.md): `OWN:allow`, `SHOP:allow`, `ALL:allow`

### order.read

- Permission status: มีใน seed; การผูก API ยังเป็นข้อเสนอ
- Allow Scope: `ALL:allow`, `OWN:allow`, `SHOP:allow`
- API ที่เสนอให้ allow:
  - [sales/03-inquiry-order](api/sales/03-inquiry-order/spec.md): `OWN:allow`
  - [sales/04-inquiry-shop-order](api/sales/04-inquiry-shop-order/spec.md): `SHOP:allow`, `ALL:allow`

### payment.read

- Permission status: **เสนอใหม่ ยังไม่มีใน seed**
- Allow Scope: `ALL:allow`, `SHOP:allow`
- Definition ที่เสนอเพิ่ม: `payment.read / ALL`, `payment.read / SHOP`; ยังไม่มี grant/effect ใหม่ในฐานข้อมูล
- API ที่เสนอให้ allow:
  - [payment/04-inquiry-shop-payment](api/payment/04-inquiry-shop-payment/spec.md): `SHOP:allow`, `ALL:allow`

### payment.refund

- Permission status: มีใน seed; การผูก API ยังเป็นข้อเสนอ
- Allow Scope: `ALL:allow`, `SHOP:allow`
- API ที่เสนอให้ allow:
  - [payment/05-refund-payment](api/payment/05-refund-payment/spec.md): `SHOP:allow`, `ALL:allow`

### shipping.manage

- Permission status: มีใน seed; การผูก API ยังเป็นข้อเสนอ
- Allow Scope: `ALL:allow`, `SHOP:allow`
- API ที่เสนอให้ allow:
  - [shipping/01-create-shipping](api/shipping/01-create-shipping/spec.md): `SHOP:allow`, `ALL:allow`
  - [shipping/02-update-shipping-status](api/shipping/02-update-shipping-status/spec.md): `SHOP:allow`, `ALL:allow`
  - [shipping/03-upsert-shipping-stop](api/shipping/03-upsert-shipping-stop/spec.md): `SHOP:allow`, `ALL:allow`
  - [shipping/04-inquiry-shop-shipping](api/shipping/04-inquiry-shop-shipping/spec.md): `SHOP:allow`, `ALL:allow`

### shop.manage

- Permission status: มีใน seed; การผูก API ยังเป็นข้อเสนอ
- Allow Scope: `ALL:allow`, `OWN:allow`, `SHOP:allow`
- Definition ที่เสนอเพิ่ม: `shop.manage / OWN`; ยังไม่มี grant/effect ใหม่ในฐานข้อมูล
- OWN ใช้เฉพาะ leave own membership / my shops; ไม่เปิดให้ STAFF จัดการสมาชิกคนอื่น; basic inquiry และ create-shop bootstrap ยังไม่ถูกบังคับ grant ใหม่
- API ที่เสนอให้ allow:
  - [shop/01-upsert-shop-product-sku](api/shop/01-upsert-shop-product-sku/spec.md): `SHOP:allow`, `ALL:allow`
  - [shop/02-upsert-shop-product-sku-batch](api/shop/02-upsert-shop-product-sku-batch/spec.md): `SHOP:allow`, `ALL:allow`
  - [shop/08-upsert-shop](api/shop/08-upsert-shop/spec.md): `SHOP:allow`, `ALL:allow`
  - [shop/09-upsert-shop-batch](api/shop/09-upsert-shop-batch/spec.md): `SHOP:allow`, `ALL:allow`
  - [shop/10-inquiry-shop](api/shop/10-inquiry-shop/spec.md): `SHOP:allow`, `ALL:allow`
  - [shop/11-upsert-shop-user](api/shop/11-upsert-shop-user/spec.md): `SHOP:allow`, `ALL:allow`, `OWN:allow`
  - [shop/12-upsert-shop-user-batch](api/shop/12-upsert-shop-user-batch/spec.md): `SHOP:allow`, `ALL:allow`, `OWN:allow`
  - [shop/13-inquiry-shop-user](api/shop/13-inquiry-shop-user/spec.md): `SHOP:allow`, `ALL:allow`, `OWN:allow`

## API → Permission → Allow Scope

เครื่องหมาย **คิว40** คือรายการที่ Peter ต้อง review ต่อ; “นอกคิว40” ไม่ได้หมายความว่าเปิดใช้ scope policy แล้ว คอลัมน์เงื่อนไขยังแสดง baseline/ข้อยกเว้นที่ต้องรักษาจาก spec ส่วน OWN ที่ไม่มี permission ระบุเป็น boundary เท่านั้น ไม่สร้าง grant requirement ใหม่

### authen-and-author

| API / Spec                                                                               | Permission ที่เสนอ | Allow Scope / effect | เงื่อนไขและข้อยกเว้นที่ต้องรักษา                                                                                 | คิว      |
| ---------------------------------------------------------------------------------------- | ------------------ | -------------------- | ---------------------------------------------------------------------------------------------------------------- | -------- |
| [POST v1/auth/register](api/authen-and-author/01-register/spec.md)                       | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant  | public; validation และกฎ register/login/reset เดิม — ไม่ใช้ scope grant                                          | นอกคิว40 |
| [POST v1/auth/login](api/authen-and-author/02-login/spec.md)                             | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant  | public; validation และกฎ register/login/reset เดิม — ไม่ใช้ scope grant                                          | นอกคิว40 |
| [POST v1/auth/reset-password](api/authen-and-author/03-reset-password/spec.md)           | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant  | public; validation และกฎ register/login/reset เดิม — ไม่ใช้ scope grant                                          | นอกคิว40 |
| [POST v1/auth/create-new-password](api/authen-and-author/04-create-new-password/spec.md) | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant  | reset token ใช้ครั้งเดียว; ไม่ใช้ access-token scope — ไม่ใช้ scope grant                                        | นอกคิว40 |
| [POST v1/auth/refresh-token](api/authen-and-author/05-refresh-token/spec.md)             | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant  | refresh token/session ถูกต้อง; โหลด claims ล่าสุด — ไม่ใช้ access-token scope เป็นสิทธิ์ refresh                 | นอกคิว40 |
| [POST v1/auth/logout](api/authen-and-author/06-logout/spec.md)                           | ไม่บังคับเพิ่ม     | `OWN:allow`          | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [POST v1/user/profile/upsert](api/authen-and-author/07-upsert-user-profile/spec.md)      | ไม่บังคับเพิ่ม     | `OWN:allow`          | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [GET v1/user/profile](api/authen-and-author/08-inquiry-user-profile/spec.md)             | ไม่บังคับเพิ่ม     | `OWN:allow`          | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [POST v1/user/address/upsert](api/authen-and-author/09-upsert-user-address/spec.md)      | ไม่บังคับเพิ่ม     | `OWN:allow`          | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [GET v1/user/address](api/authen-and-author/10-inquiry-user-address/spec.md)             | ไม่บังคับเพิ่ม     | `OWN:allow`          | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |

### author

| API / Spec                                                                              | Permission ที่เสนอ | Allow Scope / effect | เงื่อนไขและข้อยกเว้นที่ต้องรักษา                                                                 | คิว       |
| --------------------------------------------------------------------------------------- | ------------------ | -------------------- | ------------------------------------------------------------------------------------------------ | --------- |
| [POST v1/author/role/upsert](api/author/01-upsert-role/spec.md)                         | `author.manage`    | `ALL:allow`          | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/role/upsert/batch](api/author/02-upsert-role-batch/spec.md)             | `author.manage`    | `ALL:allow`          | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [GET v1/author/role](api/author/03-inquiry-role/spec.md)                                | `author.manage`    | `ALL:allow`          | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/permission/upsert](api/author/04-upsert-permission/spec.md)             | `author.manage`    | `ALL:allow`          | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/permission/upsert/batch](api/author/05-upsert-permission-batch/spec.md) | `author.manage`    | `ALL:allow`          | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [GET v1/author/permission](api/author/06-inquiry-permission/spec.md)                    | `author.manage`    | `ALL:allow`          | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/scope/upsert](api/author/07-upsert-scope/spec.md)                       | `author.manage`    | `ALL:allow`          | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/scope/upsert/batch](api/author/08-upsert-scope-batch/spec.md)           | `author.manage`    | `ALL:allow`          | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | **คิว40** |
| [GET v1/author/scope](api/author/09-inquiry-scope/spec.md)                              | `author.manage`    | `ALL:allow`          | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | **คิว40** |
| [POST v1/author/user/role/upsert](api/author/10-upsert-user-role/spec.md)               | `author.manage`    | `ALL:allow`          | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | **คิว40** |
| [GET v1/author/user/role](api/author/11-inquiry-user-role/spec.md)                      | `author.manage`    | `ALL:allow`          | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | **คิว40** |
| [GET v1/author/me](api/author/12-me/spec.md)                                            | ไม่บังคับเพิ่ม     | `OWN:allow`          | token ถูกต้อง; คืนสิทธิ์ของ token ผู้เรียกเท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40  |

### campaign

| API / Spec                                                                | Permission ที่เสนอ       | Allow Scope / effect      | เงื่อนไขและข้อยกเว้นที่ต้องรักษา                                                                                              | คิว       |
| ------------------------------------------------------------------------- | ------------------------ | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | --------- |
| [POST v1/campaign/upsert](api/campaign/01-upsert-campaign/spec.md)        | `campaign.manage` (ใหม่) | `ALL:allow`               | PLATFORM_ADMIN; จัดการ campaign/budget หรืออ่าน ledger; shops ไม่ได้สิทธิ์นี้จากการเข้าร่วม campaign                          | **คิว40** |
| [GET v1/campaign](api/campaign/02-inquiry-campaign/spec.md)               | `campaign.read` (ใหม่)   | `SHOP:allow`, `ALL:allow` | SHOP: shopId ที่เป็น ACTIVE member และ campaign ที่ใช้ได้กับร้าน; ALL: PLATFORM_ADMIN; budget/remaining/shop list เฉพาะ admin | **คิว40** |
| [GET v1/campaign/ledger](api/campaign/03-inquiry-campaign-ledger/spec.md) | `campaign.manage` (ใหม่) | `ALL:allow`               | PLATFORM_ADMIN; จัดการ campaign/budget หรืออ่าน ledger; shops ไม่ได้สิทธิ์นี้จากการเข้าร่วม campaign                          | **คิว40** |

### cart

| API / Spec                                                                   | Permission ที่เสนอ | Allow Scope / effect | เงื่อนไขและข้อยกเว้นที่ต้องรักษา                                                                         | คิว      |
| ---------------------------------------------------------------------------- | ------------------ | -------------------- | -------------------------------------------------------------------------------------------------------- | -------- |
| [POST v1/cart/item/upsert](api/cart/01-upsert-cart-item/spec.md)             | ไม่บังคับเพิ่ม     | `OWN:allow`          | token ถูกต้อง; cart ของผู้เรียกเท่านั้น ไม่รับ userId อื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [POST v1/cart/item/upsert/batch](api/cart/02-upsert-cart-item-batch/spec.md) | ไม่บังคับเพิ่ม     | `OWN:allow`          | token ถูกต้อง; cart ของผู้เรียกเท่านั้น ไม่รับ userId อื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [GET v1/cart](api/cart/03-inquiry-cart/spec.md)                              | ไม่บังคับเพิ่ม     | `OWN:allow`          | token ถูกต้อง; cart ของผู้เรียกเท่านั้น ไม่รับ userId อื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |

### consent

| API / Spec                                                                            | Permission ที่เสนอ | Allow Scope / effect | เงื่อนไขและข้อยกเว้นที่ต้องรักษา                                                                               | คิว       |
| ------------------------------------------------------------------------------------- | ------------------ | -------------------- | -------------------------------------------------------------------------------------------------------------- | --------- |
| [GET v1/consent/active](api/consent/01-inquiry-active-consent/spec.md)                | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant  | public; ACTIVE/effective consent และชนิด ACTIVE ตาม Q3 — ไม่ใช้ scope grant                                    | นอกคิว40  |
| [POST v1/consent/upsert](api/consent/02-upsert-consent/spec.md)                       | `consent.manage`   | `ALL:allow`          | PLATFORM_ADMIN; กฎ version/type/reference เดิมยังบังคับ                                                        | **คิว40** |
| [GET v1/consent](api/consent/03-inquiry-consent/spec.md)                              | `consent.manage`   | `ALL:allow`          | PLATFORM_ADMIN ตาม Q18; management inquiry ดูทั้งหมดตาม filter ตาม Q19                                         | **คิว40** |
| [POST v1/consent/submit](api/consent/04-submit-consent/spec.md)                       | ไม่บังคับเพิ่ม     | `OWN:allow`          | token ถูกต้อง; read/result/pending ของผู้เรียก; Q3/Q5/Q8/Q16/Q17 — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40  |
| [GET v1/consent/pending](api/consent/05-inquiry-pending-consent/spec.md)              | ไม่บังคับเพิ่ม     | `OWN:allow`          | token ถูกต้อง; read/result/pending ของผู้เรียก; Q3/Q5/Q8/Q16/Q17 — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40  |
| [POST v1/consent/type/upsert](api/consent/06-upsert-consent-type/spec.md)             | `consent.manage`   | `ALL:allow`          | PLATFORM_ADMIN; กฎ version/type/reference เดิมยังบังคับ                                                        | **คิว40** |
| [POST v1/consent/type/upsert/batch](api/consent/07-upsert-consent-type-batch/spec.md) | `consent.manage`   | `ALL:allow`          | PLATFORM_ADMIN; กฎ version/type/reference เดิมยังบังคับ                                                        | **คิว40** |
| [GET v1/consent/type](api/consent/08-inquiry-consent-type/spec.md)                    | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant  | ผู้มี token ถูกต้องทุกคน; ไม่บังคับ PLATFORM_ADMIN — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant              | **คิว40** |

### payment

| API / Spec                                                              | Permission ที่เสนอ    | Allow Scope / effect      | เงื่อนไขและข้อยกเว้นที่ต้องรักษา                                                                                                | คิว       |
| ----------------------------------------------------------------------- | --------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | --------- |
| [POST v1/payment](api/payment/01-start-payment/spec.md)                 | ไม่บังคับเพิ่ม        | `OWN:allow`               | เจ้าของ order/payment ตาม sub; ห้ามจ่ายหรืออ่านแทนคนอื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                          | นอกคิว40  |
| [POST v1/payment/webhook/stripe](api/payment/02-stripe-webhook/spec.md) | ไม่บังคับเพิ่ม        | ไม่ใช้ scoped grant       | Stripe signature/provider event validation; ไม่ใช้ JWT user scope — provider webhook ไม่ถูกเปิดด้วย ALL/SHOP/OWN                | นอกคิว40  |
| [GET v1/payment](api/payment/03-inquiry-payment/spec.md)                | ไม่บังคับเพิ่ม        | `OWN:allow`               | เจ้าของ order/payment ตาม sub; ห้ามจ่ายหรืออ่านแทนคนอื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                          | นอกคิว40  |
| [GET v1/shop/payment](api/payment/04-inquiry-shop-payment/spec.md)      | `payment.read` (ใหม่) | `SHOP:allow`, `ALL:allow` | SHOP: ACTIVE member ร้าน; ALL: PLATFORM_ADMIN; provider ids เฉพาะ admin                                                         | **คิว40** |
| [POST v1/shop/payment/refund](api/payment/05-refund-payment/spec.md)    | `payment.refund`      | `SHOP:allow`, `ALL:allow` | SHOP: ACTIVE member ร้านของ order; ALL: PLATFORM_ADMIN; ลูกค้า refund เองไม่ได้; ตรวจ payment/order state และ provider recovery | **คิว40** |

### product

| API / Spec                                                                                                        | Permission ที่เสนอ | Allow Scope / effect | เงื่อนไขและข้อยกเว้นที่ต้องรักษา                                                                | คิว       |
| ----------------------------------------------------------------------------------------------------------------- | ------------------ | -------------------- | ----------------------------------------------------------------------------------------------- | --------- |
| [POST v1/product/upsert](api/product/01-upsert-product/spec.md)                                                   | `catalog.manage`   | `ALL:allow`          | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product](api/product/02-inquiry-product/spec.md)                                                          | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant  | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |
| [POST v1/product/upsert/batch](api/product/03-upsert-product-batch/spec.md)                                       | `catalog.manage`   | `ALL:allow`          | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-category/upsert](api/product/04-upsert-product-category/spec.md)                                 | `catalog.manage`   | `ALL:allow`          | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product-category](api/product/05-inquiry-product-category/spec.md)                                        | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant  | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |
| [POST v1/product-category/upsert/batch](api/product/06-upsert-product-category-batch/spec.md)                     | `catalog.manage`   | `ALL:allow`          | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-category-attribute/upsert](api/product/07-upsert-product-category-attribute/spec.md)             | `catalog.manage`   | `ALL:allow`          | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product-category-attribute](api/product/08-inquiry-product-category-attribute/spec.md)                    | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant  | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |
| [POST v1/product-category-attribute/upsert/batch](api/product/09-upsert-product-category-attribute-batch/spec.md) | `catalog.manage`   | `ALL:allow`          | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-type/upsert](api/product/10-upsert-product-type/spec.md)                                         | `catalog.manage`   | `ALL:allow`          | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-type/upsert/batch](api/product/11-upsert-product-type-batch/spec.md)                             | `catalog.manage`   | `ALL:allow`          | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product-type](api/product/12-inquiry-product-type/spec.md)                                                | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant  | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |
| [POST v1/product-brand/upsert](api/product/13-upsert-product-brand/spec.md)                                       | `catalog.manage`   | `ALL:allow`          | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-brand/upsert/batch](api/product/14-upsert-product-brand-batch/spec.md)                           | `catalog.manage`   | `ALL:allow`          | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product-brand](api/product/15-inquiry-product-brand/spec.md)                                              | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant  | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |

### sales

| API / Spec                                                   | Permission ที่เสนอ    | Allow Scope / effect                   | เงื่อนไขและข้อยกเว้นที่ต้องรักษา                                                                                                                                                                                                               | คิว       |
| ------------------------------------------------------------ | --------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| [GET v1/checkout](api/sales/01-inquiry-checkout/spec.md)     | ไม่บังคับเพิ่ม        | `OWN:allow`                            | ลูกค้าใช้ cart/address ของตัวเอง; checkout/create order — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                                                                                                                                          | นอกคิว40  |
| [POST v1/order](api/sales/02-create-order/spec.md)           | ไม่บังคับเพิ่ม        | `OWN:allow`                            | ลูกค้าใช้ cart/address ของตัวเอง; checkout/create order — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                                                                                                                                          | นอกคิว40  |
| [GET v1/order](api/sales/03-inquiry-order/spec.md)           | `order.read`          | `OWN:allow`                            | อ่านเฉพาะ order ของผู้เรียก; ไม่เปิด SHOP/ALL บน customer endpoint — owner route เดิมยังไม่บังคับให้ลูกค้ารับ grant ใหม่                                                                                                                       | นอกคิว40  |
| [GET v1/shop/order](api/sales/04-inquiry-shop-order/spec.md) | `order.read`          | `SHOP:allow`, `ALL:allow`              | SHOP: ACTIVE member ร้าน; ALL: PLATFORM_ADMIN; platformProfit เฉพาะ admin                                                                                                                                                                      | **คิว40** |
| [POST v1/order/cancel](api/sales/05-cancel-order/spec.md)    | `order.cancel` (ใหม่) | `OWN:allow`, `SHOP:allow`, `ALL:allow` | OWN: เจ้าของ order; SHOP: ACTIVE member ร้านของ order; ALL: PLATFORM_ADMIN; ทุกทางต้องผ่านสถานะ/stock/budget/payment checks — permission ใหม่ที่ยังไม่ seed; owner cancel เดิมไม่ต้องรับ grant ใหม่; scheduled system expiry ไม่ใช่ API caller | **คิว40** |

### shipping

| API / Spec                                                                        | Permission ที่เสนอ | Allow Scope / effect      | เงื่อนไขและข้อยกเว้นที่ต้องรักษา                                                                               | คิว       |
| --------------------------------------------------------------------------------- | ------------------ | ------------------------- | -------------------------------------------------------------------------------------------------------------- | --------- |
| [POST v1/shop/shipping](api/shipping/01-create-shipping/spec.md)                  | `shipping.manage`  | `SHOP:allow`, `ALL:allow` | SHOP: ACTIVE member ร้านของ order/shipping; ALL: PLATFORM_ADMIN; state/quantity/order locks ตาม spec           | **คิว40** |
| [POST v1/shop/shipping/status](api/shipping/02-update-shipping-status/spec.md)    | `shipping.manage`  | `SHOP:allow`, `ALL:allow` | SHOP: ACTIVE member ร้านของ order/shipping; ALL: PLATFORM_ADMIN; state/quantity/order locks ตาม spec           | **คิว40** |
| [POST v1/shop/shipping/stop/upsert](api/shipping/03-upsert-shipping-stop/spec.md) | `shipping.manage`  | `SHOP:allow`, `ALL:allow` | SHOP: ACTIVE member ร้านของ order/shipping; ALL: PLATFORM_ADMIN; state/quantity/order locks ตาม spec           | **คิว40** |
| [GET v1/shop/shipping](api/shipping/04-inquiry-shop-shipping/spec.md)             | `shipping.manage`  | `SHOP:allow`, `ALL:allow` | SHOP: ACTIVE member ร้านของ order/shipping; ALL: PLATFORM_ADMIN; state/quantity/order locks ตาม spec           | **คิว40** |
| [GET v1/shipping](api/shipping/05-inquiry-shipping/spec.md)                       | ไม่บังคับเพิ่ม     | `OWN:allow`               | อ่าน shipping ของ order ผู้เรียกเท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                         | นอกคิว40  |
| [POST v1/shipping/confirm](api/shipping/06-confirm-delivery/spec.md)              | ไม่บังคับเพิ่ม     | `OWN:allow`               | เฉพาะผู้รับ/เจ้าของ order ยืนยันรับของ; SHOP/ALL ยืนยันแทนไม่ได้ — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40  |

### shop

| API / Spec                                                                                 | Permission ที่เสนอ | Allow Scope / effect                   | เงื่อนไขและข้อยกเว้นที่ต้องรักษา                                                                                                                                                                                    | คิว       |
| ------------------------------------------------------------------------------------------ | ------------------ | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| [POST v1/shop/product-sku/upsert](api/shop/01-upsert-shop-product-sku/spec.md)             | `shop.manage`      | `SHOP:allow`, `ALL:allow`              | SHOP: ACTIVE member ADMIN/STAFF ของร้านเป้าหมาย; ALL: PLATFORM_ADMIN                                                                                                                                                | **คิว40** |
| [POST v1/shop/product-sku/upsert/batch](api/shop/02-upsert-shop-product-sku-batch/spec.md) | `shop.manage`      | `SHOP:allow`, `ALL:allow`              | SHOP: ACTIVE member ADMIN/STAFF ของร้านเป้าหมาย; ALL: PLATFORM_ADMIN                                                                                                                                                | **คิว40** |
| [GET v1/shop/product-sku](api/shop/03-inquiry-shop-product-sku/spec.md)                    | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant                    | token ถูกต้อง; inquiry ตาม filter/projection เดิม — ไม่เพิ่ม scoped grant; อย่าอนุมานสิทธิ์เขียนจากสิทธิ์อ่าน                                                                                                       | นอกคิว40  |
| [GET v1/storefront/product](api/shop/04-inquiry-storefront-product/spec.md)                | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant                    | public; projection storefront และสถานะข้อมูลตาม spec — ไม่ใช้ scope grant                                                                                                                                           | นอกคิว40  |
| [POST v1/shop/type/upsert](api/shop/05-upsert-shop-type/spec.md)                           | `catalog.manage`   | `ALL:allow`                            | PLATFORM_ADMIN; shop type เป็นข้อมูลอ้างอิงกลาง                                                                                                                                                                     | **คิว40** |
| [POST v1/shop/type/upsert/batch](api/shop/06-upsert-shop-type-batch/spec.md)               | `catalog.manage`   | `ALL:allow`                            | PLATFORM_ADMIN; shop type เป็นข้อมูลอ้างอิงกลาง                                                                                                                                                                     | **คิว40** |
| [GET v1/shop/type](api/shop/07-inquiry-shop-type/spec.md)                                  | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant                    | token ถูกต้อง; inquiry ตาม filter/projection เดิม — ไม่เพิ่ม scoped grant; อย่าอนุมานสิทธิ์เขียนจากสิทธิ์อ่าน                                                                                                       | นอกคิว40  |
| [POST v1/shop/upsert](api/shop/08-upsert-shop/spec.md)                                     | `shop.manage`      | `SHOP:allow`, `ALL:allow`              | Insert: ทุก token โดยไม่ต้องมี scoped grant; existing: SHOP เฉพาะ ADMIN หรือ ALL admin; เปลี่ยน platformMarginRate ต้อง PLATFORM_ADMIN — insert เป็น bootstrap exception; ไม่ต้องเป็นสมาชิกของร้านที่ยังไม่ถูกสร้าง | **คิว40** |
| [POST v1/shop/upsert/batch](api/shop/09-upsert-shop-batch/spec.md)                         | `shop.manage`      | `SHOP:allow`, `ALL:allow`              | Insert: ทุก token โดยไม่ต้องมี scoped grant; existing: SHOP เฉพาะ ADMIN หรือ ALL admin; เปลี่ยน platformMarginRate ต้อง PLATFORM_ADMIN — insert เป็น bootstrap exception; ไม่ต้องเป็นสมาชิกของร้านที่ยังไม่ถูกสร้าง | **คิว40** |
| [GET v1/shop](api/shop/10-inquiry-shop/spec.md)                                            | `shop.manage`      | `SHOP:allow`, `ALL:allow`              | ทุก token อ่านรายการพื้นฐานได้; SHOP/ALL ใช้กับ margin fields เท่านั้น; รายการอื่นคง null — ไม่มี grant ยังอ่าน projection พื้นฐานตาม spec ได้                                                                      | **คิว40** |
| [POST v1/shop/user/upsert](api/shop/11-upsert-shop-user/spec.md)                           | `shop.manage`      | `SHOP:allow`, `ALL:allow`, `OWN:allow` | SHOP: ADMIN จัดการสมาชิก; ALL: PLATFORM_ADMIN; OWN: STAFF ลบ/archive membership ตัวเองเท่านั้น; ห้ามเหลือ shop ADMIN ศูนย์ — OWN เป็นข้อเสนอ definition เพิ่ม; ทางออกจากร้านเดิมต้องไม่ถูกบังคับให้มี grant ใหม่    | **คิว40** |
| [POST v1/shop/user/upsert/batch](api/shop/12-upsert-shop-user-batch/spec.md)               | `shop.manage`      | `SHOP:allow`, `ALL:allow`, `OWN:allow` | SHOP: ADMIN จัดการสมาชิก; ALL: PLATFORM_ADMIN; OWN: STAFF ลบ/archive membership ตัวเองเท่านั้น; ห้ามเหลือ shop ADMIN ศูนย์ — OWN เป็นข้อเสนอ definition เพิ่ม; ทางออกจากร้านเดิมต้องไม่ถูกบังคับให้มี grant ใหม่    | **คิว40** |
| [GET v1/shop/user](api/shop/13-inquiry-shop-user/spec.md)                                  | `shop.manage`      | `SHOP:allow`, `ALL:allow`, `OWN:allow` | SHOP: ACTIVE member เมื่อระบุ shopId; ALL: PLATFORM_ADMIN เมื่ออ่าน userId คนอื่น; OWN: userId=sub โดยไม่ระบุ shopId เพื่อดู my shops — OWN เป็นข้อเสนอ definition เพิ่ม; my shops ของตัวเองยังใช้ token ตามกฎเดิม  | **คิว40** |
| [GET v1/storefront/shop/product](api/shop/14-inquiry-storefront-shop-product/spec.md)      | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant                    | public; projection storefront และสถานะข้อมูลตาม spec — ไม่ใช้ scope grant                                                                                                                                           | นอกคิว40  |
| [POST v1/shop/product-review/upsert](api/shop/15-upsert-shop-product-review/spec.md)       | ไม่บังคับเพิ่ม     | `OWN:allow`                            | review เป็นของผู้เรียก; insert ต้องมีการซื้อสำเร็จ COMPLETED; admin ไม่เขียนแทนลูกค้า — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                                                                                 | นอกคิว40  |
| [GET v1/storefront/product-review](api/shop/16-inquiry-storefront-product-review/spec.md)  | ไม่บังคับเพิ่ม     | ไม่ใช้ scoped grant                    | public; projection storefront และสถานะข้อมูลตาม spec — ไม่ใช้ scope grant                                                                                                                                           | นอกคิว40  |

## งานที่ยังต้องทำก่อนเปิดใช้จริง

1. Review/อนุมัติการจับคู่ API กับ permission และนิยาม scope เพิ่มที่ตารางระบุ โดยเฉพาะ `catalog.manage` สำหรับ product write, OWN ของ shop.manage และ permission ใหม่ `campaign.manage`, `campaign.read`, `order.cancel`, `payment.read`
2. ออกแบบที่เก็บ/จัดการ effect และ wire format ใน JWT โดยคง `(permissionId, scopeId)` ให้ครบ กำหนด migration ของ allow-only grants, validation และการใช้งาน deny โดยไม่ถือว่าคำสั่ง scope-name:effect อนุมัติ schema ใหม่ไปแล้ว
3. ประสาน WP5b ที่ยังพักไว้: API ให้/ถอน permission และตรวจสิทธิ์ยังไม่ถูกสร้าง การเขียนตารางนี้ไม่ทำให้สิทธิ์จัดการ grant เปิดใช้ได้เอง
4. ปรับ API ทีละเส้น พร้อม `### Allow Scope`, `spec.md`, `sequence.wsd` และ checker ใน PR เดียวกัน API ที่ review ไปแล้วก่อนมีตารางนี้ยังไม่ได้รับ section ย้อนหลัง ต้องติดตามเป็นงานของ API นั้น
5. ประสาน Tommy ก่อนแก้ `sales/05` และ `payment/05` ที่ซ้อนกับ T1; ไม่ถือว่าตารางนี้ส่งงานของเขาแล้ว
6. ตรวจ deny ที่ scope ทับกันและคนละ permission, token หมดอายุ/ถูกถอน, owner/member ที่เปลี่ยน, admin, field visibility, batch rollback, SQL parity และภาพ sequence ก่อนส่งแต่ละ API

Q18/Q19 ของ management consent ได้คำตอบแล้ว: เฉพาะ PLATFORM_ADMIN และค้นดูทั้งหมดตาม filter รวมฉบับหมดอายุ/ชนิดปิด; บันทึกในคำตัดสินกลางแล้ว รายละเอียด contract ของ consent/03 ยังรอ paired review

## หลักฐานและการตรวจ

- Source inventory: 83 route headings และ spec links; scope codes ทั้งสามตรงกับ seed ปัจจุบัน; seeded permission/definition counts เป็น 7/12
- Review queue: author 4, consent 5, product 10, shop 10, shipping 4, campaign 3, sales 2, payment 2 รวม 40; endpoint อื่นอีก 43 อยู่ใน inventory เพื่ออธิบายขอบเขตและข้อยกเว้น
- รายละเอียดวิธีตรวจและผลคำสั่งจริงอยู่ใน task handoff/PR; ไม่มีการทดสอบ backend effect enforcement เพราะ PR นี้ไม่ได้เปลี่ยน implementation
