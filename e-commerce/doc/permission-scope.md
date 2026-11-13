---
name: E-commerce Permission and Scope API Matrix
description: รวม permission claim แบบ resource:action, scope claim แบบ type:value และ API allowlist พร้อมลิงก์ spec ตาม JWT payload ใหม่; อ่านก่อน review หรือเปิดใช้ authorization policy ของ API.
status: in-review
approved_by: null
approved_at: null
---

# Permission และ Scope ของ API

เจ้าของงานตัดสินเมื่อ 2026-11-13 ให้ใช้ **JWT payload ใหม่แทนรูปแบบเดิม** (`iss`, `sub`, `aud`, `jti`, `iat`, `exp`, `user`, `roles` เป็นชื่อ, `permissions` เป็น `resource:action`, `scopes` เป็น `type:value`) และให้รูปแบบนี้ **แทน Allow Scope สี่ส่วน `module:resource:action:effect`** รวม effect `deny` และกฎ "deny ชนะ" ที่อนุมัติเมื่อ 2026-11-09 ดู [คำตัดสิน](../../docs/superpowers/specs/2026-11-07-api-review-design.md) เอกสารนี้รวม API → permission claim → scope claim และรายการ API ที่แต่ละ permission เปิดได้ พร้อมลิงก์ spec ครบ **83 API** โดยทำเครื่องหมายคิว review 40 API

## สถานะและขอบเขต

- **สิ่งที่ถูกแทนที่:** rule สี่ส่วน `module:resource:action:allow` เดิมถูกแปลงเป็น permission claim `module.resource:action` (resource ที่มีขีดกลางใช้ underscore ให้ตรง naming ของ `m_permission.name` เช่น `management:shop-type:crud:allow` เป็น `management.shop_type:crud`); ชื่อใน DB คือ claim ที่เปลี่ยน `:` ตัวสุดท้ายกลับเป็น `.` (`management.shop_type.crud`) ส่วน effect `deny` และกฎ deny ชนะ **ถูกยกเลิก**: มี permission ที่ต้องใช้ = ทำได้ ไม่มี = ทำไม่ได้
- การจับคู่ permission/API แต่ละรายการยัง **in-review**; ชื่อ permission ใหม่ในตารางเป็นข้อเสนอที่ยังไม่อยู่ใน [seed ปัจจุบัน](../db/seed/author.seed.sql) (3 scope codes, 7 permission names, 12 definition pairs) และเอกสารนี้ไม่เปลี่ยน seed/schema
- **Scope claim** คือ `<รหัส scope ตัวเล็ก>:*` (`ALL` เป็น `all:*`, `SHOP` เป็น `shop:*`, `OWN` เป็น `own:*`) หมายถึงทุก instance ของ type นั้น ไม่มีค่า instance ใน DB; การตรวจว่าเป็นสมาชิก ACTIVE ของร้านนั้นหรือเป็นเจ้าของข้อมูลนั้นยังทำที่ API ตามเดิม (Q10) ไม่ใช่ที่ scope claim
- [login](api/authen-and-author/02-login/spec.md) และ [refresh](api/authen-and-author/05-refresh-token/spec.md) ยังคง Q12 ตอน resolve (scope ของ permission หนึ่งไม่ให้ permission อื่น) แต่ payload แบบแบนไม่แสดงการผูกนี้ ผู้ตรวจห้ามถือว่า scope ใดใช้ได้กับทุก permission
- คง role gate, current token/user checks, ownership, ACTIVE shop membership, ADMIN-only actions และ business invariants ใน spec การมีชื่อสิทธิ์ในเอกสารไม่สร้าง grant และไม่แปลว่า API บังคับใช้แล้ว
- ไม่เพิ่ม grant requirement ให้ public/token-only/owner/bootstrap/provider routes โดยการจัดทำตารางนี้ รูปแบบการอ้างสิทธิ์ใน spec ของแต่ละ API จะกำหนดพร้อม template ใหม่ และทยอยแยก API ละหนึ่ง PR

## Permission และ Scope claim

```text
permissions: ["<module>.<resource>:<action>"]   เช่น "management.consent:crud"
scopes:      ["<boundary>:*"]                    เช่น "all:*", "shop:*", "own:*"
```

| ส่วน     | ความหมาย                                                   | ตัวอย่าง                                             |
| -------- | ---------------------------------------------------------- | ---------------------------------------------------- |
| module   | namespace ของงาน ต้อง match แบบ exact                      | management, shop, sales, payment, shipping, campaign |
| resource | ประเภทข้อมูล ไม่ใช่ id ของข้อมูลจริง; หลายคำใช้ underscore | user, user_role, product, member, order, shipment    |
| action   | operation ที่เปิดให้                                       | create, read, update, delete, crud, cancel, refund   |

ชื่อทั้งหมดใช้ตัวพิมพ์เล็กและต้องไม่ว่าง ไม่อนุมาน wildcard, alias หรือ parent namespace

### การตัดสินสิทธิ์

- API ที่เปิดใช้ enforcement ตรวจว่า `permissions` ใน verified JWT มี permission ที่ API นั้นต้องการแบบ exact; ไม่มี = ปฏิเสธ (403 E10009) ไม่มีกฎ deny และไม่มี admin exemption แยก
- `crud` เป็น permission ที่เปิด create, read, update และ delete ของ resource นั้นเพียงชื่อเดียว ไม่ขยายไปยัง permission อื่นหรือ custom action เช่น cancel/refund ส่วน archive ใช้ action update ตาม rowStatus ของ endpoint
- แม้มี permission ยังต้องผ่านกฎ owner/member/ADMIN, field masking, สถานะธุรกิจ, reference และ last-admin checks ของ endpoint และผ่าน current token/user check
- ห้ามใช้ `user` ใน payload (id, username, displayName, email) ตัดสินสิทธิ์; ใช้ `sub`, `roles`, `permissions`, `scopes` เท่านั้น

### ขอบเขตข้อมูล

| Scope claim | เงื่อนไขที่ API ต้องตรวจเพิ่ม                                                              |
| ----------- | ------------------------------------------------------------------------------------------ |
| `all:*`     | ข้อมูลใน API นั้นทั้งแพลตฟอร์ม; role และ business restrictions ยังบังคับ                   |
| `shop:*`    | ร้านเป้าหมายที่ผู้เรียกเป็น ACTIVE member; ถ้า operation ต้อง ADMIN การเป็น STAFF ยังไม่พอ |
| `own:*`     | ข้อมูลของ verified JWT sub ตามนิยาม operation นั้น ไม่ใช่ userId ที่ client ส่งมาเอง       |

## Permission → API Allowlist

รายการต่อไปนี้คือ **candidate allowlist รอ review** รายการแสดง API ที่ permission นั้นเปิดได้ การมี definition ใน seed ไม่เท่ากับได้รับ grant และ rule ที่อ่านข้อมูลได้ไม่ข้าม field visibility

### campaign.campaign:crud

- [campaign/01-upsert-campaign](api/campaign/01-upsert-campaign/spec.md) — scope `all:*`

### campaign.campaign:read

- [campaign/02-inquiry-campaign](api/campaign/02-inquiry-campaign/spec.md) — scope `shop:*`, `all:*`

### campaign.ledger:read

- [campaign/03-inquiry-campaign-ledger](api/campaign/03-inquiry-campaign-ledger/spec.md) — scope `all:*`

### management.category_attribute:crud

- [product/07-upsert-product-category-attribute](api/product/07-upsert-product-category-attribute/spec.md) — scope `all:*`
- [product/09-upsert-product-category-attribute-batch](api/product/09-upsert-product-category-attribute-batch/spec.md) — scope `all:*`

### management.consent_type:crud

- [consent/06-upsert-consent-type](api/consent/06-upsert-consent-type/spec.md) — scope `all:*`
- [consent/07-upsert-consent-type-batch](api/consent/07-upsert-consent-type-batch/spec.md) — scope `all:*`

### management.consent:crud

- [consent/02-upsert-consent](api/consent/02-upsert-consent/spec.md) — scope `all:*`

### management.consent:read

- [consent/03-inquiry-consent](api/consent/03-inquiry-consent/spec.md) — scope `all:*`

### management.permission:crud

- [author/04-upsert-permission](api/author/04-upsert-permission/spec.md) — scope `all:*`
- [author/05-upsert-permission-batch](api/author/05-upsert-permission-batch/spec.md) — scope `all:*`

### management.permission:read

- [author/06-inquiry-permission](api/author/06-inquiry-permission/spec.md) — scope `all:*`

### management.product_brand:crud

- [product/13-upsert-product-brand](api/product/13-upsert-product-brand/spec.md) — scope `all:*`
- [product/14-upsert-product-brand-batch](api/product/14-upsert-product-brand-batch/spec.md) — scope `all:*`

### management.product_category:crud

- [product/04-upsert-product-category](api/product/04-upsert-product-category/spec.md) — scope `all:*`
- [product/06-upsert-product-category-batch](api/product/06-upsert-product-category-batch/spec.md) — scope `all:*`

### management.product_type:crud

- [product/10-upsert-product-type](api/product/10-upsert-product-type/spec.md) — scope `all:*`
- [product/11-upsert-product-type-batch](api/product/11-upsert-product-type-batch/spec.md) — scope `all:*`

### management.product:crud

- [product/01-upsert-product](api/product/01-upsert-product/spec.md) — scope `all:*`
- [product/03-upsert-product-batch](api/product/03-upsert-product-batch/spec.md) — scope `all:*`

### management.role:crud

- [author/01-upsert-role](api/author/01-upsert-role/spec.md) — scope `all:*`
- [author/02-upsert-role-batch](api/author/02-upsert-role-batch/spec.md) — scope `all:*`

### management.role:read

- [author/03-inquiry-role](api/author/03-inquiry-role/spec.md) — scope `all:*`

### management.scope:crud

- [author/07-upsert-scope](api/author/07-upsert-scope/spec.md) — scope `all:*`
- [author/08-upsert-scope-batch](api/author/08-upsert-scope-batch/spec.md) — scope `all:*`

### management.scope:read

- [author/09-inquiry-scope](api/author/09-inquiry-scope/spec.md) — scope `all:*`

### management.shop_type:crud

- [shop/05-upsert-shop-type](api/shop/05-upsert-shop-type/spec.md) — scope `all:*`
- [shop/06-upsert-shop-type-batch](api/shop/06-upsert-shop-type-batch/spec.md) — scope `all:*`

### management.user_role:crud

- [author/10-upsert-user-role](api/author/10-upsert-user-role/spec.md) — scope `all:*`

### management.user_role:read

- [author/11-inquiry-user-role](api/author/11-inquiry-user-role/spec.md) — scope `all:*`

### payment.payment:read

- [payment/04-inquiry-shop-payment](api/payment/04-inquiry-shop-payment/spec.md) — scope `shop:*`, `all:*`

### payment.payment:refund

- [payment/05-refund-payment](api/payment/05-refund-payment/spec.md) — scope `shop:*`, `all:*`

### sales.order:cancel

- [sales/05-cancel-order](api/sales/05-cancel-order/spec.md) — scope `own:*`, `shop:*`, `all:*`

### sales.order:read

- [sales/03-inquiry-order](api/sales/03-inquiry-order/spec.md) — scope `own:*`
- [sales/04-inquiry-shop-order](api/sales/04-inquiry-shop-order/spec.md) — scope `shop:*`, `all:*`

### shipping.shipment:create

- [shipping/01-create-shipping](api/shipping/01-create-shipping/spec.md) — scope `shop:*`, `all:*`

### shipping.shipment:read

- [shipping/04-inquiry-shop-shipping](api/shipping/04-inquiry-shop-shipping/spec.md) — scope `shop:*`, `all:*`

### shipping.shipment:update

- [shipping/02-update-shipping-status](api/shipping/02-update-shipping-status/spec.md) — scope `shop:*`, `all:*`

### shipping.stop:crud

- [shipping/03-upsert-shipping-stop](api/shipping/03-upsert-shipping-stop/spec.md) — scope `shop:*`, `all:*`

### shop.member:crud

- [shop/11-upsert-shop-user](api/shop/11-upsert-shop-user/spec.md) — scope `shop:*`, `all:*`, `own:*`
- [shop/12-upsert-shop-user-batch](api/shop/12-upsert-shop-user-batch/spec.md) — scope `shop:*`, `all:*`, `own:*`

### shop.member:read

- [shop/13-inquiry-shop-user](api/shop/13-inquiry-shop-user/spec.md) — scope `shop:*`, `all:*`, `own:*`

### shop.shop:crud

- [shop/08-upsert-shop](api/shop/08-upsert-shop/spec.md) — scope `shop:*`, `all:*`
- [shop/09-upsert-shop-batch](api/shop/09-upsert-shop-batch/spec.md) — scope `shop:*`, `all:*`

### shop.shop:read

- [shop/10-inquiry-shop](api/shop/10-inquiry-shop/spec.md) — scope `shop:*`, `all:*`

### shop.sku:crud

- [shop/01-upsert-shop-product-sku](api/shop/01-upsert-shop-product-sku/spec.md) — scope `shop:*`, `all:*`
- [shop/02-upsert-shop-product-sku-batch](api/shop/02-upsert-shop-product-sku-batch/spec.md) — scope `shop:*`, `all:*`

## API → Permission → Scope claim

**คิว40** คือ API ที่ Peter ต้อง review ต่อ; นอกคิว40 ไม่ได้หมายความว่าเปิดใช้ policy ใหม่แล้ว Seed permission เป็นชื่ออ้างอิงจากข้อเสนอรอบก่อนเพื่อ trace กลับ seed ไม่ใช่ permission claim ใหม่ที่ติดตั้งแล้ว `own:*` ที่ไม่มี permission เป็นขอบเขตของ token/owner route เดิม ไม่เพิ่ม grant ใหม่

### authen-and-author

| API / Spec                                                                               | Permission claim     | Scope claim | Seed permission | เงื่อนไขและข้อยกเว้น                                                                                             | คิว      |
| ---------------------------------------------------------------------------------------- | -------------------- | ----------- | --------------- | ---------------------------------------------------------------------------------------------------------------- | -------- |
| [POST v1/auth/register](api/authen-and-author/01-register/spec.md)                       | ไม่บังคับ permission | ไม่ใช้      | ไม่บังคับเพิ่ม  | public; validation และกฎ register/login/reset เดิม — ไม่ใช้ scope grant                                          | นอกคิว40 |
| [POST v1/auth/login](api/authen-and-author/02-login/spec.md)                             | ไม่บังคับ permission | ไม่ใช้      | ไม่บังคับเพิ่ม  | public; validation และกฎ register/login/reset เดิม — ไม่ใช้ scope grant                                          | นอกคิว40 |
| [POST v1/auth/reset-password](api/authen-and-author/03-reset-password/spec.md)           | ไม่บังคับ permission | ไม่ใช้      | ไม่บังคับเพิ่ม  | public; validation และกฎ register/login/reset เดิม — ไม่ใช้ scope grant                                          | นอกคิว40 |
| [POST v1/auth/create-new-password](api/authen-and-author/04-create-new-password/spec.md) | ไม่บังคับ permission | ไม่ใช้      | ไม่บังคับเพิ่ม  | reset token ใช้ครั้งเดียว; ไม่ใช้ access-token scope — ไม่ใช้ scope grant                                        | นอกคิว40 |
| [POST v1/auth/refresh-token](api/authen-and-author/05-refresh-token/spec.md)             | ไม่บังคับ permission | ไม่ใช้      | ไม่บังคับเพิ่ม  | refresh token/session ถูกต้อง; โหลด claims ล่าสุด — ไม่ใช้ access-token scope เป็นสิทธิ์ refresh                 | นอกคิว40 |
| [POST v1/auth/logout](api/authen-and-author/06-logout/spec.md)                           | ไม่บังคับ permission | `own:*`     | ไม่บังคับเพิ่ม  | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [POST v1/user/profile/upsert](api/authen-and-author/07-upsert-user-profile/spec.md)      | ไม่บังคับ permission | `own:*`     | ไม่บังคับเพิ่ม  | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [GET v1/user/profile](api/authen-and-author/08-inquiry-user-profile/spec.md)             | ไม่บังคับ permission | `own:*`     | ไม่บังคับเพิ่ม  | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [POST v1/user/address/upsert](api/authen-and-author/09-upsert-user-address/spec.md)      | ไม่บังคับ permission | `own:*`     | ไม่บังคับเพิ่ม  | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [GET v1/user/address](api/authen-and-author/10-inquiry-user-address/spec.md)             | ไม่บังคับ permission | `own:*`     | ไม่บังคับเพิ่ม  | token ถูกต้อง; session/profile/address ของผู้เรียกจาก sub เท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |

### author

| API / Spec                                                                              | Permission claim             | Scope claim | Seed permission | เงื่อนไขและข้อยกเว้น                                                                             | คิว       |
| --------------------------------------------------------------------------------------- | ---------------------------- | ----------- | --------------- | ------------------------------------------------------------------------------------------------ | --------- |
| [POST v1/author/role/upsert](api/author/01-upsert-role/spec.md)                         | `management.role:crud`       | `all:*`     | `author.manage` | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/role/upsert/batch](api/author/02-upsert-role-batch/spec.md)             | `management.role:crud`       | `all:*`     | `author.manage` | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [GET v1/author/role](api/author/03-inquiry-role/spec.md)                                | `management.role:read`       | `all:*`     | `author.manage` | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/permission/upsert](api/author/04-upsert-permission/spec.md)             | `management.permission:crud` | `all:*`     | `author.manage` | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/permission/upsert/batch](api/author/05-upsert-permission-batch/spec.md) | `management.permission:crud` | `all:*`     | `author.manage` | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [GET v1/author/permission](api/author/06-inquiry-permission/spec.md)                    | `management.permission:read` | `all:*`     | `author.manage` | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/scope/upsert](api/author/07-upsert-scope/spec.md)                       | `management.scope:crud`      | `all:*`     | `author.manage` | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | นอกคิว40  |
| [POST v1/author/scope/upsert/batch](api/author/08-upsert-scope-batch/spec.md)           | `management.scope:crud`      | `all:*`     | `author.manage` | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | **คิว40** |
| [GET v1/author/scope](api/author/09-inquiry-scope/spec.md)                              | `management.scope:read`      | `all:*`     | `author.manage` | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | **คิว40** |
| [POST v1/author/user/role/upsert](api/author/10-upsert-user-role/spec.md)               | `management.user_role:crud`  | `all:*`     | `author.manage` | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | **คิว40** |
| [GET v1/author/user/role](api/author/11-inquiry-user-role/spec.md)                      | `management.user_role:read`  | `all:*`     | `author.manage` | PLATFORM_ADMIN; กฎผู้ดูแลคนสุดท้าย/role ระบบ/ข้อมูลถูกใช้งานยังบังคับ                            | **คิว40** |
| [GET v1/author/me](api/author/12-me/spec.md)                                            | ไม่บังคับ permission         | `own:*`     | ไม่บังคับเพิ่ม  | token ถูกต้อง; คืนสิทธิ์ของ token ผู้เรียกเท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40  |

### campaign

| API / Spec                                                                | Permission claim         | Scope claim       | Seed permission   | เงื่อนไขและข้อยกเว้น                                                                                                          | คิว       |
| ------------------------------------------------------------------------- | ------------------------ | ----------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------- | --------- |
| [POST v1/campaign/upsert](api/campaign/01-upsert-campaign/spec.md)        | `campaign.campaign:crud` | `all:*`           | `campaign.manage` | PLATFORM_ADMIN; จัดการ campaign/budget หรืออ่าน ledger; shops ไม่ได้สิทธิ์นี้จากการเข้าร่วม campaign                          | **คิว40** |
| [GET v1/campaign](api/campaign/02-inquiry-campaign/spec.md)               | `campaign.campaign:read` | `shop:*`, `all:*` | `campaign.read`   | SHOP: shopId ที่เป็น ACTIVE member และ campaign ที่ใช้ได้กับร้าน; ALL: PLATFORM_ADMIN; budget/remaining/shop list เฉพาะ admin | **คิว40** |
| [GET v1/campaign/ledger](api/campaign/03-inquiry-campaign-ledger/spec.md) | `campaign.ledger:read`   | `all:*`           | `campaign.manage` | PLATFORM_ADMIN; จัดการ campaign/budget หรืออ่าน ledger; shops ไม่ได้สิทธิ์นี้จากการเข้าร่วม campaign                          | **คิว40** |

### cart

| API / Spec                                                                   | Permission claim     | Scope claim | Seed permission | เงื่อนไขและข้อยกเว้น                                                                                     | คิว      |
| ---------------------------------------------------------------------------- | -------------------- | ----------- | --------------- | -------------------------------------------------------------------------------------------------------- | -------- |
| [POST v1/cart/item/upsert](api/cart/01-upsert-cart-item/spec.md)             | ไม่บังคับ permission | `own:*`     | ไม่บังคับเพิ่ม  | token ถูกต้อง; cart ของผู้เรียกเท่านั้น ไม่รับ userId อื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [POST v1/cart/item/upsert/batch](api/cart/02-upsert-cart-item-batch/spec.md) | ไม่บังคับ permission | `own:*`     | ไม่บังคับเพิ่ม  | token ถูกต้อง; cart ของผู้เรียกเท่านั้น ไม่รับ userId อื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |
| [GET v1/cart](api/cart/03-inquiry-cart/spec.md)                              | ไม่บังคับ permission | `own:*`     | ไม่บังคับเพิ่ม  | token ถูกต้อง; cart ของผู้เรียกเท่านั้น ไม่รับ userId อื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40 |

### consent

| API / Spec                                                                            | Permission claim               | Scope claim | Seed permission  | เงื่อนไขและข้อยกเว้น                                                                                           | คิว       |
| ------------------------------------------------------------------------------------- | ------------------------------ | ----------- | ---------------- | -------------------------------------------------------------------------------------------------------------- | --------- |
| [GET v1/consent/active](api/consent/01-inquiry-active-consent/spec.md)                | ไม่บังคับ permission           | ไม่ใช้      | ไม่บังคับเพิ่ม   | public; ACTIVE/effective consent และชนิด ACTIVE ตาม Q3 — ไม่ใช้ scope grant                                    | นอกคิว40  |
| [POST v1/consent/upsert](api/consent/02-upsert-consent/spec.md)                       | `management.consent:crud`      | `all:*`     | `consent.manage` | PLATFORM_ADMIN; กฎ version/type/reference เดิมยังบังคับ                                                        | **คิว40** |
| [GET v1/consent](api/consent/03-inquiry-consent/spec.md)                              | `management.consent:read`      | `all:*`     | `consent.manage` | PLATFORM_ADMIN ตาม Q18; management inquiry ดูทั้งหมดตาม filter ตาม Q19                                         | **คิว40** |
| [POST v1/consent/submit](api/consent/04-submit-consent/spec.md)                       | ไม่บังคับ permission           | `own:*`     | ไม่บังคับเพิ่ม   | token ถูกต้อง; read/result/pending ของผู้เรียก; Q3/Q5/Q8/Q16/Q17 — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40  |
| [GET v1/consent/pending](api/consent/05-inquiry-pending-consent/spec.md)              | ไม่บังคับ permission           | `own:*`     | ไม่บังคับเพิ่ม   | token ถูกต้อง; read/result/pending ของผู้เรียก; Q3/Q5/Q8/Q16/Q17 — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40  |
| [POST v1/consent/type/upsert](api/consent/06-upsert-consent-type/spec.md)             | `management.consent_type:crud` | `all:*`     | `consent.manage` | PLATFORM_ADMIN; กฎ version/type/reference เดิมยังบังคับ                                                        | **คิว40** |
| [POST v1/consent/type/upsert/batch](api/consent/07-upsert-consent-type-batch/spec.md) | `management.consent_type:crud` | `all:*`     | `consent.manage` | PLATFORM_ADMIN; กฎ version/type/reference เดิมยังบังคับ                                                        | **คิว40** |
| [GET v1/consent/type](api/consent/08-inquiry-consent-type/spec.md)                    | ไม่บังคับ permission           | ไม่ใช้      | ไม่บังคับเพิ่ม   | ผู้มี token ถูกต้องทุกคน; ไม่บังคับ PLATFORM_ADMIN — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant              | **คิว40** |

### payment

| API / Spec                                                              | Permission claim         | Scope claim       | Seed permission  | เงื่อนไขและข้อยกเว้น                                                                                                            | คิว       |
| ----------------------------------------------------------------------- | ------------------------ | ----------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------- | --------- |
| [POST v1/payment](api/payment/01-start-payment/spec.md)                 | ไม่บังคับ permission     | `own:*`           | ไม่บังคับเพิ่ม   | เจ้าของ order/payment ตาม sub; ห้ามจ่ายหรืออ่านแทนคนอื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                          | นอกคิว40  |
| [POST v1/payment/webhook/stripe](api/payment/02-stripe-webhook/spec.md) | ไม่บังคับ permission     | ไม่ใช้            | ไม่บังคับเพิ่ม   | Stripe signature/provider event validation; ไม่ใช้ JWT user scope — provider webhook ไม่ถูกเปิดด้วย ALL/SHOP/OWN                | นอกคิว40  |
| [GET v1/payment](api/payment/03-inquiry-payment/spec.md)                | ไม่บังคับ permission     | `own:*`           | ไม่บังคับเพิ่ม   | เจ้าของ order/payment ตาม sub; ห้ามจ่ายหรืออ่านแทนคนอื่น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                          | นอกคิว40  |
| [GET v1/shop/payment](api/payment/04-inquiry-shop-payment/spec.md)      | `payment.payment:read`   | `shop:*`, `all:*` | `payment.read`   | SHOP: ACTIVE member ร้าน; ALL: PLATFORM_ADMIN; provider ids เฉพาะ admin                                                         | **คิว40** |
| [POST v1/shop/payment/refund](api/payment/05-refund-payment/spec.md)    | `payment.payment:refund` | `shop:*`, `all:*` | `payment.refund` | SHOP: ACTIVE member ร้านของ order; ALL: PLATFORM_ADMIN; ลูกค้า refund เองไม่ได้; ตรวจ payment/order state และ provider recovery | **คิว40** |

### product

| API / Spec                                                                                                        | Permission claim                     | Scope claim | Seed permission  | เงื่อนไขและข้อยกเว้น                                                                            | คิว       |
| ----------------------------------------------------------------------------------------------------------------- | ------------------------------------ | ----------- | ---------------- | ----------------------------------------------------------------------------------------------- | --------- |
| [POST v1/product/upsert](api/product/01-upsert-product/spec.md)                                                   | `management.product:crud`            | `all:*`     | `catalog.manage` | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product](api/product/02-inquiry-product/spec.md)                                                          | ไม่บังคับ permission                 | ไม่ใช้      | ไม่บังคับเพิ่ม   | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |
| [POST v1/product/upsert/batch](api/product/03-upsert-product-batch/spec.md)                                       | `management.product:crud`            | `all:*`     | `catalog.manage` | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-category/upsert](api/product/04-upsert-product-category/spec.md)                                 | `management.product_category:crud`   | `all:*`     | `catalog.manage` | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product-category](api/product/05-inquiry-product-category/spec.md)                                        | ไม่บังคับ permission                 | ไม่ใช้      | ไม่บังคับเพิ่ม   | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |
| [POST v1/product-category/upsert/batch](api/product/06-upsert-product-category-batch/spec.md)                     | `management.product_category:crud`   | `all:*`     | `catalog.manage` | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-category-attribute/upsert](api/product/07-upsert-product-category-attribute/spec.md)             | `management.category_attribute:crud` | `all:*`     | `catalog.manage` | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product-category-attribute](api/product/08-inquiry-product-category-attribute/spec.md)                    | ไม่บังคับ permission                 | ไม่ใช้      | ไม่บังคับเพิ่ม   | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |
| [POST v1/product-category-attribute/upsert/batch](api/product/09-upsert-product-category-attribute-batch/spec.md) | `management.category_attribute:crud` | `all:*`     | `catalog.manage` | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-type/upsert](api/product/10-upsert-product-type/spec.md)                                         | `management.product_type:crud`       | `all:*`     | `catalog.manage` | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-type/upsert/batch](api/product/11-upsert-product-type-batch/spec.md)                             | `management.product_type:crud`       | `all:*`     | `catalog.manage` | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product-type](api/product/12-inquiry-product-type/spec.md)                                                | ไม่บังคับ permission                 | ไม่ใช้      | ไม่บังคับเพิ่ม   | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |
| [POST v1/product-brand/upsert](api/product/13-upsert-product-brand/spec.md)                                       | `management.product_brand:crud`      | `all:*`     | `catalog.manage` | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [POST v1/product-brand/upsert/batch](api/product/14-upsert-product-brand-batch/spec.md)                           | `management.product_brand:crud`      | `all:*`     | `catalog.manage` | PLATFORM_ADMIN; ไม่เพิ่ม SHOP/OWN ให้ข้อมูล catalog กลาง                                        | **คิว40** |
| [GET v1/product-brand](api/product/15-inquiry-product-brand/spec.md)                                              | ไม่บังคับ permission                 | ไม่ใช้      | ไม่บังคับเพิ่ม   | token ถูกต้อง; inquiry reference ตาม filter เดิม — อ่านข้อมูลอ้างอิงได้โดยไม่เพิ่ม scoped grant | นอกคิว40  |

### sales

| API / Spec                                                   | Permission claim     | Scope claim                | Seed permission | เงื่อนไขและข้อยกเว้น                                                                                                                                                                                                                           | คิว       |
| ------------------------------------------------------------ | -------------------- | -------------------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| [GET v1/checkout](api/sales/01-inquiry-checkout/spec.md)     | ไม่บังคับ permission | `own:*`                    | ไม่บังคับเพิ่ม  | ลูกค้าใช้ cart/address ของตัวเอง; checkout/create order — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                                                                                                                                          | นอกคิว40  |
| [POST v1/order](api/sales/02-create-order/spec.md)           | ไม่บังคับ permission | `own:*`                    | ไม่บังคับเพิ่ม  | ลูกค้าใช้ cart/address ของตัวเอง; checkout/create order — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                                                                                                                                          | นอกคิว40  |
| [GET v1/order](api/sales/03-inquiry-order/spec.md)           | `sales.order:read`   | `own:*`                    | `order.read`    | อ่านเฉพาะ order ของผู้เรียก; ไม่เปิด SHOP/ALL บน customer endpoint — owner route เดิมยังไม่บังคับให้ลูกค้ารับ grant ใหม่                                                                                                                       | นอกคิว40  |
| [GET v1/shop/order](api/sales/04-inquiry-shop-order/spec.md) | `sales.order:read`   | `shop:*`, `all:*`          | `order.read`    | SHOP: ACTIVE member ร้าน; ALL: PLATFORM_ADMIN; platformProfit เฉพาะ admin                                                                                                                                                                      | **คิว40** |
| [POST v1/order/cancel](api/sales/05-cancel-order/spec.md)    | `sales.order:cancel` | `own:*`, `shop:*`, `all:*` | `order.cancel`  | OWN: เจ้าของ order; SHOP: ACTIVE member ร้านของ order; ALL: PLATFORM_ADMIN; ทุกทางต้องผ่านสถานะ/stock/budget/payment checks — permission ใหม่ที่ยังไม่ seed; owner cancel เดิมไม่ต้องรับ grant ใหม่; scheduled system expiry ไม่ใช่ API caller | **คิว40** |

### shipping

| API / Spec                                                                        | Permission claim           | Scope claim       | Seed permission   | เงื่อนไขและข้อยกเว้น                                                                                           | คิว       |
| --------------------------------------------------------------------------------- | -------------------------- | ----------------- | ----------------- | -------------------------------------------------------------------------------------------------------------- | --------- |
| [POST v1/shop/shipping](api/shipping/01-create-shipping/spec.md)                  | `shipping.shipment:create` | `shop:*`, `all:*` | `shipping.manage` | SHOP: ACTIVE member ร้านของ order/shipping; ALL: PLATFORM_ADMIN; state/quantity/order locks ตาม spec           | **คิว40** |
| [POST v1/shop/shipping/status](api/shipping/02-update-shipping-status/spec.md)    | `shipping.shipment:update` | `shop:*`, `all:*` | `shipping.manage` | SHOP: ACTIVE member ร้านของ order/shipping; ALL: PLATFORM_ADMIN; state/quantity/order locks ตาม spec           | **คิว40** |
| [POST v1/shop/shipping/stop/upsert](api/shipping/03-upsert-shipping-stop/spec.md) | `shipping.stop:crud`       | `shop:*`, `all:*` | `shipping.manage` | SHOP: ACTIVE member ร้านของ order/shipping; ALL: PLATFORM_ADMIN; state/quantity/order locks ตาม spec           | **คิว40** |
| [GET v1/shop/shipping](api/shipping/04-inquiry-shop-shipping/spec.md)             | `shipping.shipment:read`   | `shop:*`, `all:*` | `shipping.manage` | SHOP: ACTIVE member ร้านของ order/shipping; ALL: PLATFORM_ADMIN; state/quantity/order locks ตาม spec           | **คิว40** |
| [GET v1/shipping](api/shipping/05-inquiry-shipping/spec.md)                       | ไม่บังคับ permission       | `own:*`           | ไม่บังคับเพิ่ม    | อ่าน shipping ของ order ผู้เรียกเท่านั้น — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                         | นอกคิว40  |
| [POST v1/shipping/confirm](api/shipping/06-confirm-delivery/spec.md)              | ไม่บังคับ permission       | `own:*`           | ไม่บังคับเพิ่ม    | เฉพาะผู้รับ/เจ้าของ order ยืนยันรับของ; SHOP/ALL ยืนยันแทนไม่ได้ — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant | นอกคิว40  |

### shop

| API / Spec                                                                                 | Permission claim            | Scope claim                | Seed permission  | เงื่อนไขและข้อยกเว้น                                                                                                                                                                                                | คิว       |
| ------------------------------------------------------------------------------------------ | --------------------------- | -------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| [POST v1/shop/product-sku/upsert](api/shop/01-upsert-shop-product-sku/spec.md)             | `shop.sku:crud`             | `shop:*`, `all:*`          | `shop.manage`    | SHOP: ACTIVE member ADMIN/STAFF ของร้านเป้าหมาย; ALL: PLATFORM_ADMIN                                                                                                                                                | **คิว40** |
| [POST v1/shop/product-sku/upsert/batch](api/shop/02-upsert-shop-product-sku-batch/spec.md) | `shop.sku:crud`             | `shop:*`, `all:*`          | `shop.manage`    | SHOP: ACTIVE member ADMIN/STAFF ของร้านเป้าหมาย; ALL: PLATFORM_ADMIN                                                                                                                                                | **คิว40** |
| [GET v1/shop/product-sku](api/shop/03-inquiry-shop-product-sku/spec.md)                    | ไม่บังคับ permission        | ไม่ใช้                     | ไม่บังคับเพิ่ม   | token ถูกต้อง; inquiry ตาม filter/projection เดิม — ไม่เพิ่ม scoped grant; อย่าอนุมานสิทธิ์เขียนจากสิทธิ์อ่าน                                                                                                       | นอกคิว40  |
| [GET v1/storefront/product](api/shop/04-inquiry-storefront-product/spec.md)                | ไม่บังคับ permission        | ไม่ใช้                     | ไม่บังคับเพิ่ม   | public; projection storefront และสถานะข้อมูลตาม spec — ไม่ใช้ scope grant                                                                                                                                           | นอกคิว40  |
| [POST v1/shop/type/upsert](api/shop/05-upsert-shop-type/spec.md)                           | `management.shop_type:crud` | `all:*`                    | `catalog.manage` | PLATFORM_ADMIN; shop type เป็นข้อมูลอ้างอิงกลาง                                                                                                                                                                     | **คิว40** |
| [POST v1/shop/type/upsert/batch](api/shop/06-upsert-shop-type-batch/spec.md)               | `management.shop_type:crud` | `all:*`                    | `catalog.manage` | PLATFORM_ADMIN; shop type เป็นข้อมูลอ้างอิงกลาง                                                                                                                                                                     | **คิว40** |
| [GET v1/shop/type](api/shop/07-inquiry-shop-type/spec.md)                                  | ไม่บังคับ permission        | ไม่ใช้                     | ไม่บังคับเพิ่ม   | token ถูกต้อง; inquiry ตาม filter/projection เดิม — ไม่เพิ่ม scoped grant; อย่าอนุมานสิทธิ์เขียนจากสิทธิ์อ่าน                                                                                                       | นอกคิว40  |
| [POST v1/shop/upsert](api/shop/08-upsert-shop/spec.md)                                     | `shop.shop:crud`            | `shop:*`, `all:*`          | `shop.manage`    | Insert: ทุก token โดยไม่ต้องมี scoped grant; existing: SHOP เฉพาะ ADMIN หรือ ALL admin; เปลี่ยน platformMarginRate ต้อง PLATFORM_ADMIN — insert เป็น bootstrap exception; ไม่ต้องเป็นสมาชิกของร้านที่ยังไม่ถูกสร้าง | **คิว40** |
| [POST v1/shop/upsert/batch](api/shop/09-upsert-shop-batch/spec.md)                         | `shop.shop:crud`            | `shop:*`, `all:*`          | `shop.manage`    | Insert: ทุก token โดยไม่ต้องมี scoped grant; existing: SHOP เฉพาะ ADMIN หรือ ALL admin; เปลี่ยน platformMarginRate ต้อง PLATFORM_ADMIN — insert เป็น bootstrap exception; ไม่ต้องเป็นสมาชิกของร้านที่ยังไม่ถูกสร้าง | **คิว40** |
| [GET v1/shop](api/shop/10-inquiry-shop/spec.md)                                            | `shop.shop:read`            | `shop:*`, `all:*`          | `shop.manage`    | ทุก token อ่านรายการพื้นฐานได้; SHOP/ALL ใช้กับ margin fields เท่านั้น; รายการอื่นคง null — ไม่มี grant ยังอ่าน projection พื้นฐานตาม spec ได้                                                                      | **คิว40** |
| [POST v1/shop/user/upsert](api/shop/11-upsert-shop-user/spec.md)                           | `shop.member:crud`          | `shop:*`, `all:*`, `own:*` | `shop.manage`    | SHOP: ADMIN จัดการสมาชิก; ALL: PLATFORM_ADMIN; OWN: STAFF ลบ/archive membership ตัวเองเท่านั้น; ห้ามเหลือ shop ADMIN ศูนย์ — OWN เป็นข้อเสนอ definition เพิ่ม; ทางออกจากร้านเดิมต้องไม่ถูกบังคับให้มี grant ใหม่    | **คิว40** |
| [POST v1/shop/user/upsert/batch](api/shop/12-upsert-shop-user-batch/spec.md)               | `shop.member:crud`          | `shop:*`, `all:*`, `own:*` | `shop.manage`    | SHOP: ADMIN จัดการสมาชิก; ALL: PLATFORM_ADMIN; OWN: STAFF ลบ/archive membership ตัวเองเท่านั้น; ห้ามเหลือ shop ADMIN ศูนย์ — OWN เป็นข้อเสนอ definition เพิ่ม; ทางออกจากร้านเดิมต้องไม่ถูกบังคับให้มี grant ใหม่    | **คิว40** |
| [GET v1/shop/user](api/shop/13-inquiry-shop-user/spec.md)                                  | `shop.member:read`          | `shop:*`, `all:*`, `own:*` | `shop.manage`    | SHOP: ACTIVE member เมื่อระบุ shopId; ALL: PLATFORM_ADMIN เมื่ออ่าน userId คนอื่น; OWN: userId=sub โดยไม่ระบุ shopId เพื่อดู my shops — OWN เป็นข้อเสนอ definition เพิ่ม; my shops ของตัวเองยังใช้ token ตามกฎเดิม  | **คิว40** |
| [GET v1/storefront/shop/product](api/shop/14-inquiry-storefront-shop-product/spec.md)      | ไม่บังคับ permission        | ไม่ใช้                     | ไม่บังคับเพิ่ม   | public; projection storefront และสถานะข้อมูลตาม spec — ไม่ใช้ scope grant                                                                                                                                           | นอกคิว40  |
| [POST v1/shop/product-review/upsert](api/shop/15-upsert-shop-product-review/spec.md)       | ไม่บังคับ permission        | `own:*`                    | ไม่บังคับเพิ่ม   | review เป็นของผู้เรียก; insert ต้องมีการซื้อสำเร็จ COMPLETED; admin ไม่เขียนแทนลูกค้า — ขอบเขตข้อมูลเดิม; ไม่เพิ่ม permission grant                                                                                 | นอกคิว40  |
| [GET v1/storefront/product-review](api/shop/16-inquiry-storefront-product-review/spec.md)  | ไม่บังคับ permission        | ไม่ใช้                     | ไม่บังคับเพิ่ม   | public; projection storefront และสถานะข้อมูลตาม spec — ไม่ใช้ scope grant                                                                                                                                           | นอกคิว40  |

## งานที่ยังต้องทำก่อนเปิดใช้จริง

1. Review module/resource/action/API mappings ในเอกสารนี้; โดยเฉพาะ management กับ shop, resource user กับ user_role, `crud` ที่เป็นชื่อเดียว และ custom cancel/refund แยกต่างหาก รายการใหม่ทั้งหมดยังไม่ใช่ permission ที่ติดตั้งแล้ว
2. ออกแบบ seed/ข้อมูล permission ใหม่ให้ตรงชื่อ `module.resource.action` ใน DB (claim คือชื่อนี้ที่เปลี่ยน `.` ตัวสุดท้ายเป็น `:`) และการแปลง grants เดิมของ 7 permission names ก่อนเปลี่ยน seed/login/refresh จริง
3. WP5b grant-management/check APIs ยังพักไว้ ต้องออกแบบและอนุมัติก่อนเปิดจัดการสิทธิ์ละเอียด การมีตารางนี้ไม่สร้าง API เหล่านั้นเอง
4. ทยอยเพิ่มการอ้างสิทธิ์ใน spec และ sequence ของแต่ละ API (รูปแบบตาม template ใหม่) พร้อม checker/ตัวอย่างผล 403 ใน PR เดียวกัน; API ละหนึ่ง PR และไม่อ้างว่าปรับทั้ง 83 endpoint แล้ว
5. แก้ประโยค `roles` แบบ `{roleId,name}` ใน spec/sequence/checker ของ API อื่นให้เป็นชื่อ role ตาม payload ใหม่ (แต่ละคนในกลุ่มของตัวเองตอนจัด template)
6. ประสาน Tommy ก่อนแก้ sales/05 และ payment/05 ที่ซ้อน T1 และรักษา current token/user, owner/member/ADMIN, bootstrap, public/provider, field masking และ business invariants ทั้งหมด
7. ทดสอบ exact permission claim, `crud` ที่ไม่ขยายไป action อื่น, scope claim ที่ไม่ตรง, batch rollback และ strict SQL/render parity ก่อนส่งแต่ละ endpoint

Q18/Q19 ได้คำตอบแล้ว: consent/03 เฉพาะ PLATFORM_ADMIN และค้นดูทั้งหมดตาม filter รวมฉบับหมดอายุ/ชนิดปิด; บันทึกคำตัดสินแล้ว รายละเอียด query/filter ยังอยู่ใน paired review

## หลักฐานและการตรวจ

- Inventory 83 API/spec links และคิว 40 API; ชื่อ route เทียบจากไฟล์จริงที่มีและไม่มี frontmatter
- ทุก API ที่มี candidate permission อยู่ใน reverse allowlist; ตารางผูก permission claim ใหม่กับ scope claim และ seed permission โดยไม่แก้ endpoint หรือฐานข้อมูล
- Seed เดิม 3 scopes / 7 permissions / 12 definitions ไม่เปลี่ยน; ไม่มี backend/JWT enforcement ในงานนี้ ผลตรวจเป็นความสอดคล้องของเอกสารเท่านั้น
