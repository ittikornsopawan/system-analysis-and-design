---
name: Identity, access & consent concepts — explanation and SQL traceability
description: อธิบาย domain diagram domain-identity-model พร้อมเหตุผล ตารางต้นทาง ความสัมพันธ์และcardinalityจากSQL ใช้ก่อนreviewหรือแก้ภาพนี้
status: in-review
approved_by: null
approved_at: null
---

# Identity, access & consent concepts

[ภาพแก้ไขได้](domain-identity-model.drawio.png) · [draw.io source](domain-identity-model.drawio) · [HTML](domain-identity-model.html) · [สารบัญ](README.md)

## สิ่งที่ภาพนี้อธิบาย

User เป็นตัวตนบัญชี ส่วน Password credential, Password reset request, User profile, Delivery address, Access/Refresh token และ evidence records เป็นแนวคิดที่ต่างหน้าที่กัน กล่อง authen เป็นการจัดกลุ่มตาม schema ไม่ได้ประกาศว่า objects ทั้งหมดเป็น aggregate เดียวหรือควรโหลดใน transaction เดียว

Authorization แยก Role, Permission, Scope และ association entities สามารถตามว่า role ได้ permission ใด มี scope ใด และ user ได้สิทธิ์ผ่าน role หรือ direct grant ใด คำว่า author ในชื่อ schema หมายถึง authorization ไม่ใช่ผู้เขียนบทความ การซ้อนกรอบไม่แปลว่า config/feature flag สามารถให้สิทธิ์แทนตารางเหล่านี้

Consent type เป็นชนิดข้อยินยอม Consent version คือเนื้อหาที่เผยแพร่ ส่วน Consent acknowledgement อยู่ authen และบันทึกผู้ใช้/เวอร์ชัน/ผลการตอบรับ การแยกสามแนวคิดนี้ช่วยไม่ให้สับสนระหว่างการแก้เอกสารกับหลักฐานที่ผู้ใช้เคยเห็น

## Cardinality และประวัติ

ใช้ all-row cardinality ตาม FK: แถวลูกที่มี FK NOT NULL อ้าง parentหนึ่งแถว; ลูกอาจมี0..*ต่อparent เพราะ DDL ไม่บังคับให้ parentต้องมีลูก และ partial indexesยังอนุญาตแถวเก่า/แถวที่ไม่เข้าpredicate กรณี User profile ไม่ใช่ unconditional1:1; Password credential จำกัดหนึ่ง ACTIVE PASSWORD; reset request จำกัดหนึ่ง ACTIVE; addressจำกัดหนึ่งdefaultที่ไม่DELETED แต่ไม่จำกัดว่าผู้ใช้มีaddressได้เพียงหนึ่ง

Scoped permission → Direct permission grant เป็น optional0..1จาก nullable permission_scope_id อีกด้านของ grantยังมี permission_id ที่ต้องตรวจความสอดคล้องกันเพิ่มเติม ไม่ใช่ FKแบบcompositeที่รับรองให้แล้วทุกกรณี

## ความแตกต่างระหว่าง DB evidence กับกฎที่ต้องออกแบบต่อ

| จุด | DDL ที่ยืนยันได้ | สิ่งที่ไม่ได้พิสูจน์จาก DDL |
| --- | --- | --- |
| Session | tokenทั้งสองชนิดมี session_id | ไม่มี Session table หรือ FKยืนยันว่า access/refreshเป็นคู่เดียวกัน |
| Consent acknowledgement | user_id/consent_id และ fields consent_version, result, is_read, read_at | ไม่มี UNIQUE(user,consent,version) หรือ CHECKบังคับread_atสัมพันธ์กับis_read |
| Referral event | user_idบังคับ, referrer_id nullable | ไม่ได้เป็นหนึ่งreferralต่อuserโดยอัตโนมัติ |
| Login attempt | user_id nullable รองรับidentifierที่ไม่ตรงบัญชี | ไม่มี User เป็นparentบังคับทุกattempt |
| Scoped grant | แต่ละFKมีparentจริง | ไม่รับรองว่า scoped permissionเป็นของ permission_idเดียวกับ direct grant |
| Key material | key_nameไม่ซ้ำ, binary value, effective/expiry fields | ไม่พิสูจน์ runtime key rotation, secret storage controls หรือ encryption of the value |

## เหตุผลของการจัดรูป

ใช้ entityชื่อธุรกิจแทน prefix m_/t_/l_ ทุกconceptมีชื่อตารางกำกับและ attributesที่ช่วยแยกบทบาท เส้นที่เลือก12เส้นเน้นบัญชี/credential, role grants และconsent publication; ความสัมพันธ์อื่นรวมทั้งUser→token,User→acknowledgement และoptionalreferrerอยู่ใน FK catalogue ด้านล่าง จึงไม่ควรตีความ entityที่ไม่มีเส้นในภาพว่าไม่มีreference

กฎที่ควรพิจารณาใน `Authen/Domain/` หรือ authorization domain เช่นความสอดคล้องของ grant เป็น candidateของการออกแบบต่อ ไม่อนุมานว่ามี methods/validatorsครบแล้ว และไม่ย้ายการคำนวณเงินภาษีเข้ามาใน Authen

## ตารางต้นทางและ concept ที่แสดง

กล่อง/ชื่อเป็นconceptual interpretationของschemaที่มีอยู่ ไม่ใช่รายชื่อclassที่implementแล้ว Universal audit fieldsยังคงอยู่ในDDL แม้ไม่แสดงบนภาพ

| SQL table / schema doc | Business concept | รายละเอียดที่เลือกแสดง | Migration |
| --- | --- | --- | --- |
| [public.t_key](../../doc/schema/public/t_key.md) | Key material | `# id; key_name; effective_at / expired_at` | [00-common.schema.up.sql](../../db/migrations/up/00-common.schema.up.sql) |
| [consent.m_consent_type](../../doc/schema/consent/m_consent_type.md) | Consent type | `# id; name / is_required` | [00-common.schema.up.sql](../../db/migrations/up/00-common.schema.up.sql) |
| [consent.t_consent](../../doc/schema/consent/t_consent.md) | Consent version | `# id / code; consent_type_id; consent_version / body` | [00-common.schema.up.sql](../../db/migrations/up/00-common.schema.up.sql) |
| [authen.m_user](../../doc/schema/authen/m_user.md) | User | `# id; username / email_address; display_name` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.t_user_consent](../../doc/schema/authen/t_user_consent.md) | Consent acknowledgement | `# id; user_id / consent_id; result / is_read` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.m_user_password](../../doc/schema/authen/m_user_password.md) | Password credential | `# id / user_id; row_type; password / password_salt` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.t_user_reset_password](../../doc/schema/authen/t_user_reset_password.md) | Password reset request | `# id / user_id; reset_token; expired_at` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.l_user_referral](../../doc/schema/authen/l_user_referral.md) | Referral event | `# id / user_id; referrer_id?` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.m_user_information](../../doc/schema/authen/m_user_information.md) | User profile | `# id / user_id; phone_number / date_of_birth; gender` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.t_user_address](../../doc/schema/authen/t_user_address.md) | Delivery address | `# id / user_id; address / city / postal_code; is_default` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.t_user_access_token](../../doc/schema/authen/t_user_access_token.md) | Access token | `# id / user_id; session_id / token; expired_at` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.t_user_refresh_token](../../doc/schema/authen/t_user_refresh_token.md) | Refresh token | `# id / user_id; session_id / token; expired_at` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.l_user_login_attempt](../../doc/schema/authen/l_user_login_attempt.md) | Login attempt | `# id / user_id?; identifier_hash; result` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [author.m_role](../../doc/schema/author/m_role.md) | Role | `# id / name; description` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.m_permission](../../doc/schema/author/m_permission.md) | Permission | `# id / name; description` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.m_scope](../../doc/schema/author/m_scope.md) | Scope | `# id / scope; name / description` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.t_permission_scope](../../doc/schema/author/t_permission_scope.md) | Scoped permission | `# id / permission_id; scope_id` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.t_role_permission](../../doc/schema/author/t_role_permission.md) | Role permission grant | `# id / role_id; permission_id` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.t_role_permission_scope](../../doc/schema/author/t_role_permission_scope.md) | Scoped role grant | `# id / role_permission_id; permission_scope_id` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.t_user_role](../../doc/schema/author/t_user_role.md) | User role assignment | `# id / user_id; role_id` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.t_user_permission](../../doc/schema/author/t_user_permission.md) | Direct permission grant | `# id / user_id; permission_id; permission_scope_id?` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |

## Associations ที่เลือกวาด

ตัวเลขใกล้parentคือจำนวนparentต่อchild ตัวเลขใกล้childคือจำนวนchildต่อparent เมื่อรวมทุกแถวในประวัติ เส้นไม่มีหัวลูกศรและไม่บอกลำดับเวลา

| Parent → child (อ่านassociation ไม่ใช่call) | FKของchild | Cardinalityที่ปลาย parent / child |
| --- | --- | --- |
| User — Password credential | `authen.m_user_password.user_id` | `1` / `0..*` |
| User — User profile | `authen.m_user_information.user_id` | `1` / `0..*` |
| User — Password reset request | `authen.t_user_reset_password.user_id` | `1` / `0..*` |
| User — Delivery address | `authen.t_user_address.user_id` | `1` / `0..*` |
| Role — Role permission grant | `author.t_role_permission.role_id` | `1` / `0..*` |
| Permission — Role permission grant | `author.t_role_permission.permission_id` | `1` / `0..*` |
| Permission — Scoped permission | `author.t_permission_scope.permission_id` | `1` / `0..*` |
| Role permission grant — Scoped role grant | `author.t_role_permission_scope.role_permission_id` | `1` / `0..*` |
| Scoped permission — Scoped role grant | `author.t_role_permission_scope.permission_scope_id` | `1` / `0..*` |
| Role — User role assignment | `author.t_user_role.role_id` | `1` / `0..*` |
| Scoped permission — Direct permission grant | `author.t_user_permission.permission_scope_id` | `0..1` / `0..*` |
| Consent type — Consent version | `consent.t_consent.consent_type_id` | `1` / `0..*` |

## FK catalogue — ครบทุกreferenceของตารางในหน้านี้

รายการที่ไม่ลากเส้นยังเป็นความสัมพันธ์จริงในDB ใช้ตารางนี้ต่อข้ามภาพ 1หมายถึงFKบังคับ, 0..1หมายถึงnullable FK; ด้านจำนวนchildrenเป็น0..*ในโมเดลรวมประวัติ การลบตามFKไม่ใช่หลักฐานUMLcompositionหรือDDDaggregate

| Child FK | Parent table | Parentต่อchild | Childต่อparent | ON DELETE | ในภาพ |
| --- | --- | --- | --- | --- | --- |
| `consent.t_consent.consent_type_id` | `consent.m_consent_type` | 1 | 0..* | RESTRICT | วาดเส้น |
| `authen.t_user_consent.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | field / catalogue |
| `authen.t_user_consent.consent_id` | `consent.t_consent` | 1 | 0..* | CASCADE | field / catalogue |
| `authen.m_user_password.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | วาดเส้น |
| `authen.t_user_reset_password.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | วาดเส้น |
| `authen.l_user_referral.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | field / catalogue |
| `authen.l_user_referral.referrer_id` | `authen.m_user` | 0..1 | 0..* | SET NULL | field / catalogue |
| `authen.m_user_information.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | วาดเส้น |
| `authen.t_user_address.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | วาดเส้น |
| `authen.t_user_access_token.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | field / catalogue |
| `authen.t_user_refresh_token.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | field / catalogue |
| `authen.l_user_login_attempt.user_id` | `authen.m_user` | 0..1 | 0..* | CASCADE | field / catalogue |
| `author.t_permission_scope.permission_id` | `author.m_permission` | 1 | 0..* | RESTRICT | วาดเส้น |
| `author.t_permission_scope.scope_id` | `author.m_scope` | 1 | 0..* | RESTRICT | field / catalogue |
| `author.t_role_permission.role_id` | `author.m_role` | 1 | 0..* | RESTRICT | วาดเส้น |
| `author.t_role_permission.permission_id` | `author.m_permission` | 1 | 0..* | RESTRICT | วาดเส้น |
| `author.t_role_permission_scope.role_permission_id` | `author.t_role_permission` | 1 | 0..* | CASCADE | วาดเส้น |
| `author.t_role_permission_scope.permission_scope_id` | `author.t_permission_scope` | 1 | 0..* | RESTRICT | วาดเส้น |
| `author.t_user_role.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | field / catalogue |
| `author.t_user_role.role_id` | `author.m_role` | 1 | 0..* | RESTRICT | วาดเส้น |
| `author.t_user_permission.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | field / catalogue |
| `author.t_user_permission.permission_id` | `author.m_permission` | 1 | 0..* | RESTRICT | field / catalogue |
| `author.t_user_permission.permission_scope_id` | `author.t_permission_scope` | 0..1 | 0..* | RESTRICT | วาดเส้น |

## Partial uniqueness ที่ต้องไม่อ่านเป็น unconditional1:1

| Table | Unique index / predicate |
| --- | --- |
| `consent.m_consent_type` | `uq_m_consent_type_name ON consent.m_consent_type (name) WHERE row_status <> 'DELETED';` |
| `authen.m_user_password` | `uq_m_user_password_user_id_password ON authen.m_user_password (user_id) WHERE row_type = 'PASSWORD' AND row_status = 'ACTIVE';` |
| `authen.t_user_reset_password` | `uq_t_user_reset_password_user_id_active ON authen.t_user_reset_password (user_id) WHERE row_status = 'ACTIVE';` |
| `authen.m_user_information` | `uq_m_user_information_user_id ON authen.m_user_information (user_id) WHERE row_status <> 'DELETED';` |
| `authen.t_user_address` | `uq_t_user_address_user_id_default ON authen.t_user_address (user_id) WHERE is_default AND row_status <> 'DELETED';` |
| `author.m_role` | `uq_m_role_name ON author.m_role (name) WHERE row_status <> 'DELETED';` |
| `author.m_permission` | `uq_m_permission_name ON author.m_permission (name) WHERE row_status <> 'DELETED';` |
| `author.m_scope` | `uq_m_scope_scope ON author.m_scope (scope) WHERE row_status <> 'DELETED';` |
| `author.t_permission_scope` | `uq_t_permission_scope_permission_id_scope_id ON author.t_permission_scope (permission_id, scope_id) WHERE row_status <> 'DELETED';` |
| `author.t_role_permission` | `uq_t_role_permission_role_id_permission_id ON author.t_role_permission (role_id, permission_id) WHERE row_status <> 'DELETED';` |
| `author.t_role_permission_scope` | `uq_t_role_permission_scope_role_permission_scope ON author.t_role_permission_scope (role_permission_id, permission_scope_id) WHERE row_status <> 'DELETED';` |
| `author.t_user_role` | `uq_t_user_role_user_id_role_id ON author.t_user_role (user_id, role_id) WHERE row_status <> 'DELETED';` |
| `author.t_user_permission` | `uq_t_user_permission_user_id_permission_id ON author.t_user_permission (user_id, permission_id) WHERE permission_scope_id IS NULL AND row_status <> 'DELETED';` |
| `author.t_user_permission` | `uq_t_user_permission_user_id_permission_scope ON author.t_user_permission (user_id, permission_id, permission_scope_id) WHERE permission_scope_id IS NOT NULL AND row_status <> 'DELETED';` |

## การตรวจและการสร้างซ้ำ

```sh
python3 -B e-commerce/scripts/diagrams/generate_domain_diagrams.py --check
```

Generatorเทียบtable/column/nullability/reference/constraint/indexและhashของmigration/schema docsกับ [source inventory](domain-source-inventory.json) ก่อนตรวจmodel, nativeparent/child, text capacity, routesและcardinality positions ถ้าDBหรือmappingเปลี่ยนให้reviewmodelแล้วใช้ `--refresh-inventory` และสร้างภาพใหม่ ไม่แก้DDLเพื่อให้ภาพผ่าน

```sh
python3 -B e-commerce/scripts/diagrams/generate_domain_diagrams.py
# export each .drawio with draw.io Desktop as shown in README
python3 -B e-commerce/scripts/diagrams/generate_domain_diagrams.py --finalize-pngs
```

ใช้styleอ่อน/แต้มส้มเดิมและA3landscape1584×1120 NativePNGใช้fontfallbacksที่READMEเปิดเผย ผลตรวจภาพจริงและeditabilityอยู่ใน [domain-model-verification.md](domain-model-verification.md) ไม่มีbackend/API/schema implementationหรือruntimeDB/provider testsในงานนี้

## แหล่งอ้างอิง

- [Schema index](../../doc/schema/README.md), [migrations](../../db/migrations/up/), [physical ER เดิม](../../db/er-diagram.drawio)
- [Microsoft domain analysis](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis): ใช้ประกอบการแยกconcept/ขอบเขตเชิงธุรกิจ; ไม่ถือว่าSQLschemaเท่ากับboundedcontext
- [PostgreSQL constraints](https://www.postgresql.org/docs/18/ddl-constraints.html) และ [partial indexes](https://www.postgresql.org/docs/18/indexes-partial.html): ใช้ตีความFK, nullabilityและconditionaluniqueness

SQL/schema baseline commit: `7007015ba770973daab0460f850b01bb789a4989`; file hashesบันทึกในinventoryเพื่อให้ตรวจdriftได้ แม้ภายหลังbranchมีcommitงานภาพเพิ่ม
