---
name: E-commerce Permission and Scope API Matrix
description: รวม Allow Scope แบบ module:resource:action:effect, ขอบเขตข้อมูล และ API allowlist พร้อมลิงก์ spec; อ่านก่อน review หรือเปิดใช้ authorization policy ของ API.
status: in-review
approved_by: null
approved_at: null
---

# Permission และ Allow Scope ของ API

เจ้าของงานขอให้แสดงสิทธิ์แบบ **`<module>:<resource>:<action>:<effect>`** เช่น `management:user:read:allow` และ `management:user:crud:deny` เอกสารนี้รวม API → Allow Scope และรายการ API ที่แต่ละ rule อนุญาต พร้อมลิงก์ spec ครบ **83 API** โดยทำเครื่องหมายคิว review 40 API ตาม [คำตัดสินกลาง](../../docs/superpowers/specs/2026-11-07-api-review-design.md)

## สถานะและขอบเขต

- รูปแบบสี่ส่วนนี้แทนรูปแบบ scope-name:effect ที่เสนอใน PR88 รอบแรก กฎ deny ชนะเมื่อครอบคลุม operation/ข้อมูลเดียวกันยังคงอยู่ การจับคู่ namespace/action/API แต่ละรายการยัง **in-review**
- `ALL`, `SHOP`, `OWN` คือ **ขอบเขตข้อมูล** แยกจากชื่อสิทธิ์สี่ส่วน ไม่ใช่ชื่อ module/resource/action และไม่ใช่ effect
- [seed ปัจจุบัน](../db/seed/author.seed.sql) ยังมี 3 scope codes, 7 permission names และ 12 definition pairs; JWT ใน [login](api/authen-and-author/02-login/spec.md)/[refresh](api/authen-and-author/05-refresh-token/spec.md) ยังเป็น permission-specific scope แบบ allow-only ไม่มี effect หรือชื่อสิทธิ์สี่ส่วนที่รองรับแล้ว
- รูปแบบใหม่นี้ไม่ผ่าน naming contract ของ permission/scope เดิมโดยอัตโนมัติ จึงยังไม่ใส่ colon string ลง `m_scope.scope`/`m_permission.name` หรือ JWT และไม่เปลี่ยน seed/schema ใน PR นี้ ต้องออกแบบการเก็บ/ผูกกับ permissionId/scopeId และการแปลง grants เดิมก่อนเปิดใช้จริง
- คง role gate, current token/user checks, ownership, ACTIVE shop membership, ADMIN-only actions และ business invariants ใน spec การมีชื่อสิทธิ์ในเอกสารไม่สร้าง grant และไม่แปลว่า API บังคับใช้แล้ว
- ไม่เพิ่ม grant requirement ให้ public/token-only/owner/bootstrap/provider routes โดยการจัดทำตารางนี้ การเพิ่ม `### Allow Scope` และ flow บังคับใช้ใน spec/sequence จะทยอยแยก API ละหนึ่ง PR

## Allow Scope

```text
<module>:<resource>:<action>:<effect>
management:user:read:allow
management:user:crud:deny
```

| ส่วน     | ความหมาย                              | ตัวอย่าง                                             |
| -------- | ------------------------------------- | ---------------------------------------------------- |
| module   | namespace ของงาน ต้อง match แบบ exact | management, shop, sales, payment, shipping, campaign |
| resource | ประเภทข้อมูล ไม่ใช่ id ของข้อมูลจริง  | user, user-role, product, member, order, shipment    |
| action   | operation ที่อนุญาตหรือห้าม           | create, read, update, delete, crud, cancel, refund   |
| effect   | ผลของ rule                            | allow, deny                                          |

ชื่อ module/resource/action/effect ใช้ตัวพิมพ์เล็ก; resource หลายคำใช้ hyphen ต้องมี **4 ส่วนที่ไม่ว่าง** คั่นด้วย colon ไม่อนุมาน wildcard, alias, parent namespace หรือ effect “อื่นๆ” ที่ยังไม่กำหนด ค่าที่ไม่รู้จักไม่ให้สิทธิ์จนกว่าจะกำหนดและอนุมัติความหมาย

`management:user:*` ในตัวอย่างอธิบายรูปแบบเท่านั้น ไม่ประกาศ API จัดการ user ใหม่ ขณะนี้ [user-role](api/author/10-upsert-user-role/spec.md) และ [own-user profile](api/authen-and-author/07-upsert-user-profile/spec.md) เป็นคนละ resource/เงื่อนไข ห้ามใช้ user scope ไปเปิด user-role หรือ profile ของคนอื่น

### Action และ deny precedence

- `crud` เป็นกลุ่ม **create, read, update, delete** จึงครอบคลุม read ด้วย ส่วน archive ใช้กฎ update ตาม rowStatus ของ endpoint; CRUD ไม่เปิด custom action เช่น cancel/refund โดยอัตโนมัติ
- Rule ต้อง match module/resource แบบ exact, action ที่ร้องขอหรือกลุ่ม CRUD ที่ครอบคลุม action นั้น และ **ข้อมูลเป้าหมายเดียวกัน** ภายใน permission association ที่ถูกต้อง ขอบเขต ALL/SHOP/OWN ต้อง match resource จริงด้วย ห้ามดึง scope ของ permission อื่นมารวมกัน
- **matching deny ชนะ matching allow** รวมถึงกรณี read:allow ชน crud:deny และรวมผู้เรียก PLATFORM_ADMIN เมื่อเปิดใช้ policy ใหม่ ไม่มี admin exemption จาก explicit deny
- หากไม่มี matching deny จึงพิจารณา matching allow สำหรับ route ที่เปิดใช้ enforcement; การไม่มี rule ไม่สร้าง grant ขึ้นมาเอง ไม่ใช้กฎนี้ปิด exception เดิมที่ยังเป็น token-only/public/bootstrap
- แม้ผ่าน allow ยังต้องผ่านกฎ owner/member/ADMIN, field masking, สถานะธุรกิจ, reference และ last-admin checks ของ endpoint

| Rules ที่ครอบคลุมข้อมูลเดียวกัน                        | Operation ที่เรียก                   | ผล                                  |
| ------------------------------------------------------ | ------------------------------------ | ----------------------------------- |
| management:user:read:allow                             | management / user / read             | allow                               |
| management:user:crud:allow                             | management / user / read หรือ update | allow ตามกลุ่ม CRUD                 |
| management:user:read:allow + management:user:crud:deny | management / user / read             | **deny** เพราะ CRUD รวม read        |
| management:user:crud:allow + management:user:read:deny | management / user / read             | **deny**                            |
| management:user:crud:allow + management:user:read:deny | management / user / update           | allow; read deny ไม่ครอบคลุม update |
| management:user:read:allow + management:role:crud:deny | management / user / read             | allow; คนละ resource                |
| management:user:read:allow + shop:user:crud:deny       | management / user / read             | allow; คนละ module                  |
| sales:order:crud:allow                                 | sales / order / cancel               | ไม่อนุญาต custom cancel จาก CRUD    |

ดังนั้น **ตัวอย่างสอง rule ของเจ้าของงานเมื่อใช้พร้อมกันจะอ่าน user ไม่ได้** ถ้าตั้งใจให้อ่านได้แต่ห้ามเขียน ให้ใช้ `management:user:read:allow` ร่วมกับ create/update/delete:deny แยก action แทน crud:deny ไม่เปลี่ยนความหมาย CRUD ให้เหลือเฉพาะ write

### ขอบเขตข้อมูล

| Boundary | เงื่อนไขที่ต้อง match                                                                      |
| -------- | ------------------------------------------------------------------------------------------ |
| ALL      | ข้อมูลใน API/permission นั้นทั้งแพลตฟอร์ม; role และ business restrictions ยังบังคับ        |
| SHOP     | ร้านเป้าหมายที่ผู้เรียกเป็น ACTIVE member; ถ้า operation ต้อง ADMIN การเป็น STAFF ยังไม่พอ |
| OWN      | ข้อมูลของ verified JWT sub ตามนิยาม operation นั้น ไม่ใช่ userId ที่ client ส่งมาเอง       |

Boundary เป็นคุณสมบัติของ grant/branch แยกจากชื่อ rule; ยังไม่ได้กำหนด storage/wire format เมื่อ allow และ deny มี boundary ต่างกัน ต้องตรวจข้อมูลเดียวกันก่อน เช่น deny ที่ ALL ครอบคลุม order ร้าน A ด้วย แต่ SHOP deny ของผู้ที่ไม่ได้เป็นสมาชิกร้าน B ไม่ match ร้าน B การ match action/resource ไม่แทนการ match boundary

### รูปแบบ section สำหรับ spec แต่ละ API

```markdown
### Allow Scope

- Rules: `management:user:read:allow`, `management:user:crud:deny`
- Requested action: `read`
- Data boundary: `ALL` ตาม role/resource ของ API
- Resolution: deny; CRUD ครอบคลุม read และ matching deny ชนะ
- Status: in-review; ตัวอย่างรูปแบบ ไม่ใช่ endpoint จัดการ user ที่สร้างแล้ว
- Reference: [permission-scope.md](../../../permission-scope.md)
```

เมื่อใส่ใน spec จริง ให้ใช้ module/resource/action ของ API นั้นจากตารางถัดไปและระบุผลของ allow/deny ใน sequence/error/checker ให้ตรงกัน สำหรับ route ที่ไม่มี scoped grant ให้เขียนว่า “ไม่บังคับ scoped rule” แล้วระบุ public/token/owner/provider condition เดิม ไม่สร้าง PUBLIC/SYSTEM/TOKEN scope ปลอม

## Rule → API Allowlist

รายการต่อไปนี้คือ **candidate allowlist รอ review** ค่า effect ในรายการเป็น allow เพื่อแสดง API ที่ rule นั้นเปิดได้ ไม่สร้าง explicit deny ให้ทุก scope ที่ไม่ได้ระบุ การมี definition ใน seed ไม่เท่ากับได้รับ grant และ rule ที่อ่านข้อมูลได้ไม่ข้าม field visibility

### campaign:campaign:crud:allow

- [campaign/01-upsert-campaign](api/campaign/01-upsert-campaign/spec.md) — boundary `ALL`

### campaign:campaign:read:allow

- [campaign/02-inquiry-campaign](api/campaign/02-inquiry-campaign/spec.md) — boundary `SHOP`, `ALL`

### campaign:ledger:read:allow

- [campaign/03-inquiry-campaign-ledger](api/campaign/03-inquiry-campaign-ledger/spec.md) — boundary `ALL`

### management:category-attribute:crud:allow

- [product/07-upsert-product-category-attribute](api/product/07-upsert-product-category-attribute/spec.md) — boundary `ALL`
- [product/09-upsert-product-category-attribute-batch](api/product/09-upsert-product-category-attribute-batch/spec.md) — boundary `ALL`

### management:consent-type:crud:allow

- [consent/06-upsert-consent-type](api/consent/06-upsert-consent-type/spec.md) — boundary `ALL`
- [consent/07-upsert-consent-type-batch](api/consent/07-upsert-consent-type-batch/spec.md) — boundary `ALL`

### management:consent:crud:allow

- [consent/02-upsert-consent](api/consent/02-upsert-consent/spec.md) — boundary `ALL`

### management:consent:read:allow

- [consent/03-inquiry-consent](api/consent/03-inquiry-consent/spec.md) — boundary `ALL`

### management:permission:crud:allow

- [author/04-upsert-permission](api/author/04-upsert-permission/spec.md) — boundary `ALL`
- [author/05-upsert-permission-batch](api/author/05-upsert-permission-batch/spec.md) — boundary `ALL`

### management:permission:read:allow

- [author/06-inquiry-permission](api/author/06-inquiry-permission/spec.md) — boundary `ALL`

### management:product-brand:crud:allow

- [product/13-upsert-product-brand](api/product/13-upsert-product-brand/spec.md) — boundary `ALL`
- [product/14-upsert-product-brand-batch](api/product/14-upsert-product-brand-batch/spec.md) — boundary `ALL`

### management:product-category:crud:allow

- [product/04-upsert-product-category](api/product/04-upsert-product-category/spec.md) — boundary `ALL`
- [product/06-upsert-product-category-batch](api/product/06-upsert-product-category-batch/spec.md) — boundary `ALL`

### management:product-type:crud:allow

- [product/10-upsert-product-type](api/product/10-upsert-product-type/spec.md) — boundary `ALL`
- [product/11-upsert-product-type-batch](api/product/11-upsert-product-type-batch/spec.md) — boundary `ALL`

### management:product:crud:allow

- [product/01-upsert-product](api/product/01-upsert-product/spec.md) — boundary `ALL`
- [product/03-upsert-product-batch](api/product/03-upsert-product-batch/spec.md) — boundary `ALL`

### management:role:crud:allow

- [author/01-upsert-role](api/author/01-upsert-role/spec.md) — boundary `ALL`
- [author/02-upsert-role-batch](api/author/02-upsert-role-batch/spec.md) — boundary `ALL`

### management:role:read:allow

- [author/03-inquiry-role](api/author/03-inquiry-role/spec.md) — boundary `ALL`

### management:scope:crud:allow

- [author/07-upsert-scope](api/author/07-upsert-scope/spec.md) — boundary `ALL`
- [author/08-upsert-scope-batch](api/author/08-upsert-scope-batch/spec.md) — boundary `ALL`

### management:scope:read:allow

- [author/09-inquiry-scope](api/author/09-inquiry-scope/spec.md) — boundary `ALL`

### management:shop-type:crud:allow

- [shop/05-upsert-shop-type](api/shop/05-upsert-shop-type/spec.md) — boundary `ALL`
- [shop/06-upsert-shop-type-batch](api/shop/06-upsert-shop-type-batch/spec.md) — boundary `ALL`

### management:user-role:crud:allow

- [author/10-upsert-user-role](api/author/10-upsert-user-role/spec.md) — boundary `ALL`

### management:user-role:read:allow

- [author/11-inquiry-user-role](api/author/11-inquiry-user-role/spec.md) — boundary `ALL`

### payment:payment:read:allow

- [payment/04-inquiry-shop-payment](api/payment/04-inquiry-shop-payment/spec.md) — boundary `SHOP`, `ALL`

### payment:payment:refund:allow

- [payment/05-refund-payment](api/payment/05-refund-payment/spec.md) — boundary `SHOP`, `ALL`

### sales:order:cancel:allow

- [sales/05-cancel-order](api/sales/05-cancel-order/spec.md) — boundary `OWN`, `SHOP`, `ALL`

### sales:order:read:allow

- [sales/03-inquiry-order](api/sales/03-inquiry-order/spec.md) — boundary `OWN`
- [sales/04-inquiry-shop-order](api/sales/04-inquiry-shop-order/spec.md) — boundary `SHOP`, `ALL`

### shipping:shipment:create:allow

- [shipping/01-create-shipping](api/shipping/01-create-shipping/spec.md) — boundary `SHOP`, `ALL`

### shipping:shipment:read:allow

- [shipping/04-inquiry-shop-shipping](api/shipping/04-inquiry-shop-shipping/spec.md) — boundary `SHOP`, `ALL`

### shipping:shipment:update:allow

- [shipping/02-update-shipping-status](api/shipping/02-update-shipping-status/spec.md) — boundary `SHOP`, `ALL`

### shipping:stop:crud:allow

- [shipping/03-upsert-shipping-stop](api/shipping/03-upsert-shipping-stop/spec.md) — boundary `SHOP`, `ALL`

### shop:member:crud:allow

- [shop/11-upsert-shop-user](api/shop/11-upsert-shop-user/spec.md) — boundary `SHOP`, `ALL`, `OWN`
- [shop/12-upsert-shop-user-batch](api/shop/12-upsert-shop-user-batch/spec.md) — boundary `SHOP`, `ALL`, `OWN`

### shop:member:read:allow

- [shop/13-inquiry-shop-user](api/shop/13-inquiry-shop-user/spec.md) — boundary `SHOP`, `ALL`, `OWN`

### shop:shop:crud:allow

- [shop/08-upsert-shop](api/shop/08-upsert-shop/spec.md) — boundary `SHOP`, `ALL`
- [shop/09-upsert-shop-batch](api/shop/09-upsert-shop-batch/spec.md) — boundary `SHOP`, `ALL`

### shop:shop:read:allow

- [shop/10-inquiry-shop](api/shop/10-inquiry-shop/spec.md) — boundary `SHOP`, `ALL`

### shop:sku:crud:allow

- [shop/01-upsert-shop-product-sku](api/shop/01-upsert-shop-product-sku/spec.md) — boundary `SHOP`, `ALL`
- [shop/02-upsert-shop-product-sku-batch](api/shop/02-upsert-shop-product-sku-batch/spec.md) — boundary `SHOP`, `ALL`

## API → Allow Scope → ขอบเขตข้อมูล

**คิว40** คือ API ที่ Peter ต้อง review ต่อ; นอกคิว40 ไม่ได้หมายความว่าเปิดใช้ policy ใหม่แล้ว Legacy permission เป็นชื่ออ้างอิงจากข้อเสนอรอบก่อนเพื่อ trace กลับ seed ไม่ใช่ชื่อสิทธิ์สี่ส่วนที่ติดตั้งแล้ว OWN ที่ไม่มี rule เป็น boundary ของ token/owner route เดิม ไม่เพิ่ม grant ใหม่

### authen-and-author

| API / Spec                                                                               | Allow Scope           | Data boundary | Legacy permission | เงื่อนไขและข้อยกเว้น                                                                                             | คิว      |
| ---------------------------------------------------------------------------------------- | --------------------- | ------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------- | -------- |
| [POST v1/auth/register](api/authen-and-author/01-register/spec.md)                       | ไม่บังคับ scoped rule | ไม่ใช้        | ไม่บังคับเพิ่ม    | public; validation และกฎ register/login/reset เดิม — ไม่ใช้ scope grant                                          | นอกคิว40 |
| [POST v1/auth/login](api/authen-and-author/02-login/spec.md)                             | ไม่บังคับ scoped rule | ไม่ใช้        | ไม่บังคับเพิ่ม    | public; validation และกฎ register/login/reset เดิม — ไม่ใช้ scope grant                                          | นอกคิว40 |
| [POST v1/auth/reset-password](api/authen-and-author/03-reset-password/spec.md)           | ไม่บังคับ scoped rule | ไม่ใช้        | ไม่บังคับเพิ่ม    | public; validation และกฎ register/login/reset เดิม — ไม่ใช้ scope grant                                          | นอกคิว40 |
| [POST v1/auth/create-new-password](api/authen-and-author/04-create-new-password/spec.md) | ไม่บังคับ scoped rule | ไม่ใช้        | ไม่บังคับเพิ่ม    | reset token ใช้ครั้งเดียว; ไม่ใช้ access-token scope — ไม่ใช้ scope grant                                        | นอกคิว40 |
| [POST v1/auth/refresh-token](api/authen-and-author/05-refresh-token/spec.md)             | ไม่บังคับ scoped rule | ไม่ใช้        | ไม่บังคับเพิ่ม    | refresh token/session ถูกต้อง; โหลด claims ล่าสุด — ไม่ใช้ access-token scope เป็นสิทธิ์ refresh                 | นอกคิว40 |
| [POST v1/auth/logout](api/authen-and-author/06-logout/spec.md)                           | ไม่บังคับ scoped rule | `OWN`         | ไม่บังคับเพิ่ม    | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [POST v1/user/profile/upsert](api/authen-and-author/07-upsert-user-profile/spec.md)      | ไม่บังคับ scoped rule | `OWN`         | ไม่บังคับเพิ่ม    | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [GET v1/user/profile](api/authen-and-author/08-inquiry-user-profile/spec.md)             | ไม่บังคับ scoped rule | `OWN`         | ไม่บังคับเพิ่ม    | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [POST v1/user/address/upsert](api/authen-and-author/09-upsert-user-address/spec.md)      | ไม่บังคับ scoped rule | `OWN`         | ไม่บังคับเพิ่ม    | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [GET v1/user/address](api/authen-and-author/10-inquiry-user-address/spec.md)             | ไม่บังคับ scoped rule | `OWN`         | ไม่บังคับเพิ่ม    | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |

### author

| API / Spec                                                                              | Allow Scope                        | Data boundary | Legacy permission | เงื่อนไขและข้อยกเว้น                                                                             | คิว       |
| --------------------------------------------------------------------------------------- | ---------------------------------- | ------------- | ----------------- | ------------------------------------------------------------------------------------------------ | --------- |
| [POST v1/author/role/upsert](api/author/01-upsert-role/spec.md)                         | `management:role:crud:allow`       | `ALL`         | `author.manage`   | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/role/upsert/batch](api/author/02-upsert-role-batch/spec.md)             | `management:role:crud:allow`       | `ALL`         | `author.manage`   | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [GET v1/author/role](api/author/03-inquiry-role/spec.md)                                | `management:role:read:allow`       | `ALL`         | `author.manage`   | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/permission/upsert](api/author/04-upsert-permission/spec.md)             | `management:permission:crud:allow` | `ALL`         | `author.manage`   | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/permission/upsert/batch](api/author/05-upsert-permission-batch/spec.md) | `management:permission:crud:allow` | `ALL`         | `author.manage`   | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [GET v1/author/permission](api/author/06-inquiry-permission/spec.md)                    | `management:permission:read:allow` | `ALL`         | `author.manage`   | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/scope/upsert](api/author/07-upsert-scope/spec.md)                       | `management:scope:crud:allow`      | `ALL`         | `author.manage`   | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/scope/upsert/batch](api/author/08-upsert-scope-batch/spec.md)           | `management:scope:crud:allow`      | `ALL`         | `author.manage`   | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | **คิว40** |
| [GET v1/author/scope](api/author/09-inquiry-scope/spec.md)                              | `management:scope:read:allow`      | `ALL`         | `author.manage`   | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | **คิว40** |
| [POST v1/author/user/role/upsert](api/author/10-upsert-user-role/spec.md)               | `management:user-role:crud:allow`  | `ALL`         | `author.manage`   | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | **คิว40** |
| [GET v1/author/user/role](api/author/11-inquiry-user-role/spec.md)                      | `management:user-role:read:allow`  | `ALL`         | `author.manage`   | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | **คิว40** |
| [GET v1/author/me](api/author/12-me/spec.md)                                            | ไม่บังคับ scoped rule              | `OWN`         | ไม่บังคับเพิ่ม    | token ถูกต้อง; คืนสิทธิ์ของ token ผู้เรียกเท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40  |

### campaign

| API / Spec                                                                | Allow Scope                    | Data boundary | Legacy permission | เงื่อนไขและข้อยกเว้น                                                                                                          | คิว       |
| ------------------------------------------------------------------------- | ------------------------------ | ------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------- | --------- |
| [POST v1/campaign/upsert](api/campaign/01-upsert-campaign/spec.md)        | `campaign:campaign:crud:allow` | `ALL`         | `campaign.manage` | PLATFORM_ADMIN; จัดการ campaign/budget หรืออ่าน ledger; shops ไม่ได้สิทธิ์นี้จากการเข้าร่วม campaign                          | **คิว40** |
| [GET v1/campaign](api/campaign/02-inquiry-campaign/spec.md)               | `campaign:campaign:read:allow` | `SHOP`, `ALL` | `campaign.read`   | SHOP: shopId ที่เป็น ACTIVE member และ campaign ที่ใช้ได้กับร้าน; ALL: PLATFORM_ADMIN; budget/remaining/shop list เฉพาะ admin | **คิว40** |
| [GET v1/campaign/ledger](api/campaign/03-inquiry-campaign-ledger/spec.md) | `campaign:ledger:read:allow`   | `ALL`         | `campaign.manage` | PLATFORM_ADMIN; จัดการ campaign/budget หรืออ่าน ledger; shops ไม่ได้สิทธิ์นี้จากการเข้าร่วม campaign                          | **คิว40** |

### cart

| API / Spec                                                                   | Allow Scope           | Data boundary | Legacy permission | เงื่อนไขและข้อยกเว้น                                                                                     | คิว      |
| ---------------------------------------------------------------------------- | --------------------- | ------------- | ----------------- | -------------------------------------------------------------------------------------------------------- | -------- |
| [POST v1/cart/item/upsert](api/cart/01-upsert-cart-item/spec.md)             | ไม่บังคับ scoped rule | `OWN`         | ไม่บังคับเพิ่ม    | token ถูกต้อง; cart ของผู้เรียกเท่านั้น ไม่รับ userId อื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [POST v1/cart/item/upsert/batch](api/cart/02-upsert-cart-item-batch/spec.md) | ไม่บังคับ scoped rule | `OWN`         | ไม่บังคับเพิ่ม    | token ถูกต้อง; cart ของผู้เรียกเท่านั้น ไม่รับ userId อื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [GET v1/cart](api/cart/03-inquiry-cart/spec.md)                              | ไม่บังคับ scoped rule | `OWN`         | ไม่บังคับเพิ่ม    | token ถูกต้อง; cart ของผู้เรียกเท่านั้น ไม่รับ userId อื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |

### consent

| API / Spec                                                                            | Allow Scope                          | Data boundary | Legacy permission | เงื่อนไขและข้อยกเว้น                                                                                           | คิว       |
| ------------------------------------------------------------------------------------- | ------------------------------------ | ------------- | ----------------- | -------------------------------------------------------------------------------------------------------------- | --------- |
| [GET v1/consent/active](api/consent/01-inquiry-active-consent/spec.md)                | ไม่บังคับ scoped rule                | ไม่ใช้        | ไม่บังคับเพิ่ม    | public; ACTIVE/effective consent และชนิด ACTIVE ตาม Q3 — ไม่ใช้ scope grant                                    | นอกคิว40  |
| [POST v1/consent/upsert](api/consent/02-upsert-consent/spec.md)                       | `management:consent:crud:allow`      | `ALL`         | `consent.manage`  | PLATFORM_ADMIN; กฎ version/type/reference เดิมยังบังคับ                                                        | **คิว40** |
| [GET v1/consent](api/consent/03-inquiry-consent/spec.md)                              | `management:consent:read:allow`      | `ALL`         | `consent.manage`  | PLATFORM_ADMIN ตาม Q18; management inquiry ดูทั้งหมดตาม filter ตาม Q19                                         | **คิว40** |
| [POST v1/consent/submit](api/consent/04-submit-consent/spec.md)                       | ไม่บังคับ scoped rule                | `OWN`         | ไม่บังคับเพิ่ม    | token ถูกต้อง; read/result/pending ของผู้เรียก; Q3/Q5/Q8/Q16/Q17 — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40  |
| [GET v1/consent/pending](api/consent/05-inquiry-pending-consent/spec.md)              | ไม่บังคับ scoped rule                | `OWN`         | ไม่บังคับเพิ่ม    | token ถูกต้อง; read/result/pending ของผู้เรียก; Q3/Q5/Q8/Q16/Q17 — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40  |
| [POST v1/consent/type/upsert](api/consent/06-upsert-consent-type/spec.md)             | `management:consent-type:crud:allow` | `ALL`         | `consent.manage`  | PLATFORM_ADMIN; กฎ version/type/reference เดิมยังบังคับ                                                        | **คิว40** |
| [POST v1/consent/type/upsert/batch](api/consent/07-upsert-consent-type-batch/spec.md) | `management:consent-type:crud:allow` | `ALL`         | `consent.manage`  | PLATFORM_ADMIN; กฎ version/type/reference เดิมยังบังคับ                                                        | **คิว40** |
| [GET v1/consent/type](api/consent/08-inquiry-consent-type/spec.md)                    | ไม่บังคับ scoped rule                | ไม่ใช้        | ไม่บังคับเพิ่ม    | ผู้มี token ถูกต้องทุกคน; ไม่บังคับ PLATFORM_ADMIN — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant              | **คิว40** |

### payment

| API / Spec                                                              | Allow Scope                    | Data boundary | Legacy permission | เงื่อนไขและข้อยกเว้น                                                                                                            | คิว       |
| ----------------------------------------------------------------------- | ------------------------------ | ------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------- | --------- |
| [POST v1/payment](api/payment/01-start-payment/spec.md)                 | ไม่บังคับ scoped rule          | `OWN`         | ไม่บังคับเพิ่ม    | เจ้าของ order/payment ตาม sub; ห้ามจ่ายหรืออ่านแทนคนอื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                          | นอกคิว40  |
| [POST v1/payment/webhook/stripe](api/payment/02-stripe-webhook/spec.md) | ไม่บังคับ scoped rule          | ไม่ใช้        | ไม่บังคับเพิ่ม    | Stripe signature/provider event validation; ไม่ใช้ JWT user scope — provider webhook ไม่ถูกเปิดด้วย ALL/SHOP/OWN                | นอกคิว40  |
| [GET v1/payment](api/payment/03-inquiry-payment/spec.md)                | ไม่บังคับ scoped rule          | `OWN`         | ไม่บังคับเพิ่ม    | เจ้าของ order/payment ตาม sub; ห้ามจ่ายหรืออ่านแทนคนอื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                          | นอกคิว40  |
| [GET v1/shop/payment](api/payment/04-inquiry-shop-payment/spec.md)      | `payment:payment:read:allow`   | `SHOP`, `ALL` | `payment.read`    | SHOP: ACTIVE member ร้าน; ALL: PLATFORM_ADMIN; provider ids เฉพาะ admin                                                         | **คิว40** |
| [POST v1/shop/payment/refund](api/payment/05-refund-payment/spec.md)    | `payment:payment:refund:allow` | `SHOP`, `ALL` | `payment.refund`  | SHOP: ACTIVE member ร้านของ order; ALL: PLATFORM_ADMIN; ลูกค้า refund เองไม่ได้; ตรวจ payment/order state และ provider recovery | **คิว40** |

### product

| API / Spec                                                                                                        | Allow Scope                                | Data boundary | Legacy permission | เงื่อนไขและข้อยกเว้น                                                                            | คิว       |
| ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | ------------- | ----------------- | ----------------------------------------------------------------------------------------------- | --------- |
| [POST v1/product/upsert](api/product/01-upsert-product/spec.md)                                                   | `management:product:crud:allow`            | `ALL`         | `catalog.manage`  | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product](api/product/02-inquiry-product/spec.md)                                                          | ไม่บังคับ scoped rule                      | ไม่ใช้        | ไม่บังคับเพิ่ม    | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |
| [POST v1/product/upsert/batch](api/product/03-upsert-product-batch/spec.md)                                       | `management:product:crud:allow`            | `ALL`         | `catalog.manage`  | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-category/upsert](api/product/04-upsert-product-category/spec.md)                                 | `management:product-category:crud:allow`   | `ALL`         | `catalog.manage`  | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product-category](api/product/05-inquiry-product-category/spec.md)                                        | ไม่บังคับ scoped rule                      | ไม่ใช้        | ไม่บังคับเพิ่ม    | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |
| [POST v1/product-category/upsert/batch](api/product/06-upsert-product-category-batch/spec.md)                     | `management:product-category:crud:allow`   | `ALL`         | `catalog.manage`  | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-category-attribute/upsert](api/product/07-upsert-product-category-attribute/spec.md)             | `management:category-attribute:crud:allow` | `ALL`         | `catalog.manage`  | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product-category-attribute](api/product/08-inquiry-product-category-attribute/spec.md)                    | ไม่บังคับ scoped rule                      | ไม่ใช้        | ไม่บังคับเพิ่ม    | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |
| [POST v1/product-category-attribute/upsert/batch](api/product/09-upsert-product-category-attribute-batch/spec.md) | `management:category-attribute:crud:allow` | `ALL`         | `catalog.manage`  | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-type/upsert](api/product/10-upsert-product-type/spec.md)                                         | `management:product-type:crud:allow`       | `ALL`         | `catalog.manage`  | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-type/upsert/batch](api/product/11-upsert-product-type-batch/spec.md)                             | `management:product-type:crud:allow`       | `ALL`         | `catalog.manage`  | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product-type](api/product/12-inquiry-product-type/spec.md)                                                | ไม่บังคับ scoped rule                      | ไม่ใช้        | ไม่บังคับเพิ่ม    | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |
| [POST v1/product-brand/upsert](api/product/13-upsert-product-brand/spec.md)                                       | `management:product-brand:crud:allow`      | `ALL`         | `catalog.manage`  | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-brand/upsert/batch](api/product/14-upsert-product-brand-batch/spec.md)                           | `management:product-brand:crud:allow`      | `ALL`         | `catalog.manage`  | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product-brand](api/product/15-inquiry-product-brand/spec.md)                                              | ไม่บังคับ scoped rule                      | ไม่ใช้        | ไม่บังคับเพิ่ม    | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |

### sales

| API / Spec                                                   | Allow Scope                | Data boundary        | Legacy permission | เงื่อนไขและข้อยกเว้น                                                                                                                                                                                                                           | คิว       |
| ------------------------------------------------------------ | -------------------------- | -------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| [GET v1/checkout](api/sales/01-inquiry-checkout/spec.md)     | ไม่บังคับ scoped rule      | `OWN`                | ไม่บังคับเพิ่ม    | ลูกค้าใช้ cart/address ของตัวเอง; checkout/create order — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                                                                                                                                          | นอกคิว40  |
| [POST v1/order](api/sales/02-create-order/spec.md)           | ไม่บังคับ scoped rule      | `OWN`                | ไม่บังคับเพิ่ม    | ลูกค้าใช้ cart/address ของตัวเอง; checkout/create order — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                                                                                                                                          | นอกคิว40  |
| [GET v1/order](api/sales/03-inquiry-order/spec.md)           | `sales:order:read:allow`   | `OWN`                | `order.read`      | อ่านเฉพาะ order ของผู้เรียก; ไม่เปิด SHOP/ALL บน customer endpoint — owner route เดิมยังไม่บังคับให้ลูกค้ารับ grant ใหม่                                                                                                                       | นอกคิว40  |
| [GET v1/shop/order](api/sales/04-inquiry-shop-order/spec.md) | `sales:order:read:allow`   | `SHOP`, `ALL`        | `order.read`      | SHOP: ACTIVE member ร้าน; ALL: PLATFORM_ADMIN; platformProfit เฉพาะ admin                                                                                                                                                                      | **คิว40** |
| [POST v1/order/cancel](api/sales/05-cancel-order/spec.md)    | `sales:order:cancel:allow` | `OWN`, `SHOP`, `ALL` | `order.cancel`    | OWN: เจ้าของ order; SHOP: ACTIVE member ร้านของ order; ALL: PLATFORM_ADMIN; ทุกทางต้องผ่านสถานะ/stock/budget/payment checks — permission ใหม่ที่ยังไม่ seed; owner cancel เดิมไม่ต้องรับ grant ใหม่; scheduled system expiry ไม่ใช่ API caller | **คิว40** |

### shipping

| API / Spec                                                                        | Allow Scope                      | Data boundary | Legacy permission | เงื่อนไขและข้อยกเว้น                                                                                           | คิว       |
| --------------------------------------------------------------------------------- | -------------------------------- | ------------- | ----------------- | -------------------------------------------------------------------------------------------------------------- | --------- |
| [POST v1/shop/shipping](api/shipping/01-create-shipping/spec.md)                  | `shipping:shipment:create:allow` | `SHOP`, `ALL` | `shipping.manage` | SHOP: ACTIVE member ร้านของ order/shipping; ALL: PLATFORM_ADMIN; state/quantity/order locks ตาม spec           | **คิว40** |
| [POST v1/shop/shipping/status](api/shipping/02-update-shipping-status/spec.md)    | `shipping:shipment:update:allow` | `SHOP`, `ALL` | `shipping.manage` | SHOP: ACTIVE member ร้านของ order/shipping; ALL: PLATFORM_ADMIN; state/quantity/order locks ตาม spec           | **คิว40** |
| [POST v1/shop/shipping/stop/upsert](api/shipping/03-upsert-shipping-stop/spec.md) | `shipping:stop:crud:allow`       | `SHOP`, `ALL` | `shipping.manage` | SHOP: ACTIVE member ร้านของ order/shipping; ALL: PLATFORM_ADMIN; state/quantity/order locks ตาม spec           | **คิว40** |
| [GET v1/shop/shipping](api/shipping/04-inquiry-shop-shipping/spec.md)             | `shipping:shipment:read:allow`   | `SHOP`, `ALL` | `shipping.manage` | SHOP: ACTIVE member ร้านของ order/shipping; ALL: PLATFORM_ADMIN; state/quantity/order locks ตาม spec           | **คิว40** |
| [GET v1/shipping](api/shipping/05-inquiry-shipping/spec.md)                       | ไม่บังคับ scoped rule            | `OWN`         | ไม่บังคับเพิ่ม    | อ่าน shipping ของ order ผู้เรียกเท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                         | นอกคิว40  |
| [POST v1/shipping/confirm](api/shipping/06-confirm-delivery/spec.md)              | ไม่บังคับ scoped rule            | `OWN`         | ไม่บังคับเพิ่ม    | เฉพาะผู้รับ/เจ้าของ order ยืนยันรับของ; SHOP/ALL ยืนยันแทนไม่ได้ — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40  |

### shop

| API / Spec                                                                                 | Allow Scope                       | Data boundary        | Legacy permission | เงื่อนไขและข้อยกเว้น                                                                                                                                                                                                | คิว       |
| ------------------------------------------------------------------------------------------ | --------------------------------- | -------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| [POST v1/shop/product-sku/upsert](api/shop/01-upsert-shop-product-sku/spec.md)             | `shop:sku:crud:allow`             | `SHOP`, `ALL`        | `shop.manage`     | SHOP: ACTIVE member ADMIN/STAFF ของร้านเป้าหมาย; ALL: PLATFORM_ADMIN                                                                                                                                                | **คิว40** |
| [POST v1/shop/product-sku/upsert/batch](api/shop/02-upsert-shop-product-sku-batch/spec.md) | `shop:sku:crud:allow`             | `SHOP`, `ALL`        | `shop.manage`     | SHOP: ACTIVE member ADMIN/STAFF ของร้านเป้าหมาย; ALL: PLATFORM_ADMIN                                                                                                                                                | **คิว40** |
| [GET v1/shop/product-sku](api/shop/03-inquiry-shop-product-sku/spec.md)                    | ไม่บังคับ scoped rule             | ไม่ใช้               | ไม่บังคับเพิ่ม    | token ถูกต้อง; inquiry ตาม filter/projection เดิม — ไม่เพิ่ม scoped grant; อย่าอนุมานสิทธิ์เขียนจากสิทธิ์อ่าน                                                                                                       | นอกคิว40  |
| [GET v1/storefront/product](api/shop/04-inquiry-storefront-product/spec.md)                | ไม่บังคับ scoped rule             | ไม่ใช้               | ไม่บังคับเพิ่ม    | public; projection storefront และสถานะข้อมูลตาม spec — ไม่ใช้ scope grant                                                                                                                                           | นอกคิว40  |
| [POST v1/shop/type/upsert](api/shop/05-upsert-shop-type/spec.md)                           | `management:shop-type:crud:allow` | `ALL`                | `catalog.manage`  | PLATFORM_ADMIN; shop type เป็นข้อมูลอ้างอิงกลาง                                                                                                                                                                     | **คิว40** |
| [POST v1/shop/type/upsert/batch](api/shop/06-upsert-shop-type-batch/spec.md)               | `management:shop-type:crud:allow` | `ALL`                | `catalog.manage`  | PLATFORM_ADMIN; shop type เป็นข้อมูลอ้างอิงกลาง                                                                                                                                                                     | **คิว40** |
| [GET v1/shop/type](api/shop/07-inquiry-shop-type/spec.md)                                  | ไม่บังคับ scoped rule             | ไม่ใช้               | ไม่บังคับเพิ่ม    | token ถูกต้อง; inquiry ตาม filter/projection เดิม — ไม่เพิ่ม scoped grant; อย่าอนุมานสิทธิ์เขียนจากสิทธิ์อ่าน                                                                                                       | นอกคิว40  |
| [POST v1/shop/upsert](api/shop/08-upsert-shop/spec.md)                                     | `shop:shop:crud:allow`            | `SHOP`, `ALL`        | `shop.manage`     | Insert: ทุก token โดยไม่ต้องมี scoped grant; existing: SHOP เฉพาะ ADMIN หรือ ALL admin; เปลี่ยน platformMarginRate ต้อง PLATFORM_ADMIN — insert เป็น bootstrap exception; ไม่ต้องเป็นสมาชิกของร้านที่ยังไม่ถูกสร้าง | **คิว40** |
| [POST v1/shop/upsert/batch](api/shop/09-upsert-shop-batch/spec.md)                         | `shop:shop:crud:allow`            | `SHOP`, `ALL`        | `shop.manage`     | Insert: ทุก token โดยไม่ต้องมี scoped grant; existing: SHOP เฉพาะ ADMIN หรือ ALL admin; เปลี่ยน platformMarginRate ต้อง PLATFORM_ADMIN — insert เป็น bootstrap exception; ไม่ต้องเป็นสมาชิกของร้านที่ยังไม่ถูกสร้าง | **คิว40** |
| [GET v1/shop](api/shop/10-inquiry-shop/spec.md)                                            | `shop:shop:read:allow`            | `SHOP`, `ALL`        | `shop.manage`     | ทุก token อ่านรายการพื้นฐานได้; SHOP/ALL ใช้กับ margin fields เท่านั้น; รายการอื่นคง null — ไม่มี grant ยังอ่าน projection พื้นฐานตาม spec ได้                                                                      | **คิว40** |
| [POST v1/shop/user/upsert](api/shop/11-upsert-shop-user/spec.md)                           | `shop:member:crud:allow`          | `SHOP`, `ALL`, `OWN` | `shop.manage`     | SHOP: ADMIN จัดการสมาชิก; ALL: PLATFORM_ADMIN; OWN: STAFF ลบ/archive membership ตัวเองเท่านั้น; ห้ามเหลือ shop ADMIN ศูนย์ — OWN เป็นข้อเสนอ definition เพิ่ม; ทางออกจากร้านเดิมต้องไม่ถูกบังคับให้มี grant ใหม่    | **คิว40** |
| [POST v1/shop/user/upsert/batch](api/shop/12-upsert-shop-user-batch/spec.md)               | `shop:member:crud:allow`          | `SHOP`, `ALL`, `OWN` | `shop.manage`     | SHOP: ADMIN จัดการสมาชิก; ALL: PLATFORM_ADMIN; OWN: STAFF ลบ/archive membership ตัวเองเท่านั้น; ห้ามเหลือ shop ADMIN ศูนย์ — OWN เป็นข้อเสนอ definition เพิ่ม; ทางออกจากร้านเดิมต้องไม่ถูกบังคับให้มี grant ใหม่    | **คิว40** |
| [GET v1/shop/user](api/shop/13-inquiry-shop-user/spec.md)                                  | `shop:member:read:allow`          | `SHOP`, `ALL`, `OWN` | `shop.manage`     | SHOP: ACTIVE member เมื่อระบุ shopId; ALL: PLATFORM_ADMIN เมื่ออ่าน userId คนอื่น; OWN: userId=sub โดยไม่ระบุ shopId เพื่อดู my shops — OWN เป็นข้อเสนอ definition เพิ่ม; my shops ของตัวเองยังใช้ token ตามกฎเดิม  | **คิว40** |
| [GET v1/storefront/shop/product](api/shop/14-inquiry-storefront-shop-product/spec.md)      | ไม่บังคับ scoped rule             | ไม่ใช้               | ไม่บังคับเพิ่ม    | public; projection storefront และสถานะข้อมูลตาม spec — ไม่ใช้ scope grant                                                                                                                                           | นอกคิว40  |
| [POST v1/shop/product-review/upsert](api/shop/15-upsert-shop-product-review/spec.md)       | ไม่บังคับ scoped rule             | `OWN`                | ไม่บังคับเพิ่ม    | review เป็นของผู้เรียก; insert ต้องมีการซื้อสำเร็จ COMPLETED; admin ไม่เขียนแทนลูกค้า — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                                                                                 | นอกคิว40  |
| [GET v1/storefront/product-review](api/shop/16-inquiry-storefront-product-review/spec.md)  | ไม่บังคับ scoped rule             | ไม่ใช้               | ไม่บังคับเพิ่ม    | public; projection storefront และสถานะข้อมูลตาม spec — ไม่ใช้ scope grant                                                                                                                                           | นอกคิว40  |

## งานที่ยังต้องทำก่อนเปิดใช้จริง

1. Review module/resource/action/API mappings ในเอกสารนี้; โดยเฉพาะ management กับ shop, resource user กับ user-role, CRUD ที่รวม read และ custom cancel/refund แยกต่างหาก รายการใหม่ทั้งหมดยังไม่ใช่ grant ที่ติดตั้งแล้ว
2. ออกแบบ storage/JWT ของชื่อสิทธิ์สี่ส่วน, effect, boundary และความสัมพันธ์ permissionId/scopeId รวมการแปลง allow-only grants เดิม ก่อนเปลี่ยน naming rules/schema/seed/login/refresh ไม่อนุมานว่า colon string ใช้กับรูปแบบเดิมได้เลย
3. WP5b grant-management/check APIs ยังพักไว้ ต้องออกแบบและอนุมัติก่อนเปิดจัดการสิทธิ์ละเอียด การมีตารางนี้ไม่สร้าง API เหล่านั้นเอง
4. ทยอยเพิ่ม Allow Scope ใน spec และ sequence ของแต่ละ API พร้อม checker/ตัวอย่างผล deny ใน PR เดียวกัน; API ละหนึ่ง PR และไม่อ้างว่าปรับทั้ง 83 endpoint แล้ว
5. ประสาน Tommy ก่อนแก้ sales/05 และ payment/05 ที่ซ้อน T1 และรักษา current token/user, owner/member/ADMIN, bootstrap, public/provider, field masking และ business invariants ทั้งหมด
6. ทดสอบ exact namespace, CRUD/read overlap, custom actions, different/nonmatching boundaries, deny ของ permission อื่น, batch rollback และ strict SQL/render parity ก่อนส่งแต่ละ endpoint

Q18/Q19 ได้คำตอบแล้ว: consent/03 เฉพาะ PLATFORM_ADMIN และค้นดูทั้งหมดตาม filter รวมฉบับหมดอายุ/ชนิดปิด; บันทึกคำตัดสินแล้ว รายละเอียด query/filter ยังอยู่ใน paired review

## หลักฐานและการตรวจ

- Inventory 83 API/spec links และคิว 40 API; ชื่อ route เทียบจากไฟล์จริงที่มีและไม่มี frontmatter
- ทุก API ที่มี candidate rule อยู่ใน reverse allowlist; ตารางผูกชื่อสิทธิ์ใหม่กับ boundary และ legacy permission โดยไม่แก้ endpoint หรือฐานข้อมูล
- Seed เดิม 3 scopes / 7 permissions / 12 definitions ไม่เปลี่ยน รายละเอียดผลตรวจและข้อจำกัดของ reference evaluator อยู่ใน handoff/PR; ไม่มี backend/JWT effect enforcement ในงานนี้
