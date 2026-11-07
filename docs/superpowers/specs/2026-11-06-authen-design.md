---
name: ยืนยันตัวตนให้ครบ (authen) — WP4
description: เอกสารออกแบบรอบ 1 ของ WP4 ใช้อ่านก่อนแก้ schema authen, เขียน API refresh, logout, reset password, create new password, โปรไฟล์และที่อยู่ และก่อนแก้สัญญา token ที่ spec ทุกเส้นพึ่งอยู่
status: in-review
approved_by: null
approved_at: null
---

# ยืนยันตัวตนให้ครบ (authen) — WP4

> Behavior decisions confirmed directly by the product owner on 2026-11-07 (Peter Q13); this revised document remains in-review: [API review decisions](2026-11-07-api-review-design.md) govern JWT authorization and consent changes. Detailed dependent endpoint revisions are delivered separately; this note does not claim that every endpoint already matches the new decisions.

วันที่: 2026-11-06 · ผู้เขียน: Marry (SA) · สถานะ: รอบ 1 รอ Josh ตรวจ (ประตู 1) ยังไม่แก้ migration หรือเขียน spec · `approved_by`: Ittikorn (Aof) Sopawan ตอบผ่าน Josh 2026-11-06 ("ตามที่แนะนำ" ต่อ Q1 ถึง Q5 และการเพิ่ม index ของตารางที่ส่งแล้ว)

ตาม [roadmap](../plans/2026-11-06-api-roadmap.md) WP4 ข้อเท็จจริงอ่านจาก `origin/main` (738f215) รวมถึงโค้ด backend ใน `e-commerce/repository/` ซึ่งอ่านอย่างเดียวเพื่อเทียบ (ไม่ได้รันและไม่ได้ทดสอบ) spec ที่ส่งแล้ว `01-register`, `02-login` ไม่ถูกแก้ ข้อเสนอแก้อยู่ในหัวข้อ "ข้อเสนอแก้ `02-login`"

## เป้าหมาย

- กำหนดสัญญา token ที่ spec 38 เส้นพึ่งอยู่ (header `authorization: Bearer <access token>`, 401 `E10002`, `userId` มาจาก token) ให้ชัดว่า token ออกอย่างไร ตรวจอย่างไร หมดอายุและถูกเพิกถอนเมื่อไร
- Login บันทึก token ลงตาราง, refresh token, logout, ขอรีเซ็ตรหัสผ่าน, ตั้งรหัสผ่านใหม่ด้วย reset token
- โปรไฟล์ผู้ใช้และที่อยู่จัดส่งของลูกค้า (upsert, inquiry) ให้ checkout (`sales/01`, `02`) ใช้ที่อยู่ได้ตามเดิม
- กันเดารหัสผ่านและไม่เปิดเผยว่า email มีในระบบหรือไม่ (ในเส้นที่ WP4 เป็นเจ้าของ)

## ไม่ใช่เป้าหมาย

- แก้ `01-register`, `02-login` ในรอบ 1 (ทำในรอบ 2 หลังอนุมัติ)
- เปลี่ยน username, email หรือรหัสผ่านขณะล็อกอินอยู่ (ไม่อยู่ในขอบเขต WP4 ตามแผน) ลบหรือปิดบัญชีผู้ใช้
- การส่ง email/SMS จริง (spec เขียนแค่ว่าระบบสั่งส่ง) 2FA, social login
- ตรวจสิทธิ์แบบ role/permission (WP5) และ `public.t_key` (นอกขอบเขตจนกว่าเจ้าของงานบอก)
- ความปลอดภัยของโครงสร้างพื้นฐาน (rate limit ระดับ gateway/IP, WAF)

## ผลงาน (หลังประตู 1)

- Schema (แก้ที่ `CREATE TABLE`): `authen.t_user_access_token` และ `t_user_refresh_token` เพิ่ม `session_id`; partial unique index 4 ตัว (`t_user_reset_password`, `m_user_password`, `m_user_information`, `t_user_address`); ตารางใหม่ `authen.l_user_login_attempt` (ตาราง 52 → 53); แบบทดสอบ SQL; schema doc, README, ER
- Spec 8 เส้นใน `e-commerce/doc/api/authen-and-author/`: `03-reset-password`, `04-create-new-password` (แทน template ว่าง), `05-refresh-token`, `06-logout`, `07-upsert-user-profile`, `08-inquiry-user-profile`, `09-upsert-user-address`, `10-inquiry-user-address`
- แก้ `01-register`, `02-login` ตามหัวข้อข้อเสนอ (หลังเจ้าของงานอนุมัติ ผ่านประตู 2 พร้อมกัน) และตัวตรวจ `authen-spec`, `authen-schema` ต่อท้าย `check_docs.py`

## ตารางข้อเท็จจริงที่อ้างอิง

| ข้อเท็จจริง | ที่มา | สถานะการตรวจ |
|---|---|---|
| `token BYTEA UNIQUE` (access, refresh), `reset_token BYTEA UNIQUE` มี `expired_at` ไม่มีคอลัมน์ session หรือผู้ออก | `01-authen.schema.up.sql` | อ่านจากไฟล์ |
| `m_user_password` มีหลายแถวต่อผู้ใช้ได้ (`row_type` PASSWORD, TEMPORARY_PASSWORD) ไม่มี unique ต่อผู้ใช้ | migration `01` | อ่านจากไฟล์ |
| `m_user_information` และ `t_user_address` ไม่มี unique ต่อ `user_id` และไม่มี unique เรื่อง default ของที่อยู่ | migration `01` | อ่านจากไฟล์ |
| `02-login`: `expiresIn` 3600 วินาที, refresh หมดอายุ 7 วัน, ตอบ 401 `E10002` "Invalid username or password." ทุกกรณีผิด, ตัวอย่าง access token เป็น JWT 3 ส่วน, **ไม่บันทึก token ลงตาราง**, คำอธิบายบอกว่า login ด้วย mobile no ได้ แต่ SQL ตรวจแค่ `username` และ `email_address` | spec login | อ่านจากไฟล์ |
| `01-register`: `username`, `emailAddress`, `password`, `firstName`, `lastName` ส่งแบบ "เข้ารหัส AES256 Key และ IV ฝั่ง frontend" และเก็บเป็นไบต์ตรงๆ (จึงเทียบ `username = bytes` ได้); `phoneNumber`, `address` และฟิลด์ที่อยู่ส่งเป็นข้อความธรรมดา (`...Bytes` ใน SQL) | spec register | อ่านจากไฟล์ |
| `register` ตอบ 409 `E10003` เมื่อ username หรือ email ซ้ำ (เปิดเผยว่ามีในระบบ) | spec register | อ่านจากไฟล์ |
| spec 38 ไฟล์ใช้ header `authorization` และ 38 ไฟล์ตอบ `E10002` ข้อความเดียว "Invalid or expired access token." | `grep` ใน `e-commerce/doc/api` | ค้นแล้ว |
| `sales/01`, `02` อ่าน `t_user_address` (ต้อง `ACTIVE` และเป็นของผู้ใช้) แล้วคัดลอก title, address, city, state, postal_code, country เข้าออเดอร์; `sales/04`, `shop/11`, `13`, `16` อ่าน `m_user.display_name` | spec เหล่านั้น | อ่านจากไฟล์ |
| backend (อ่านอย่างเดียว): JWT HS256 มี `sub`, `jti`; refresh และ reset token เป็นสุ่ม 32 ไบต์ base64url; เก็บ SHA-256 ของ token ลงตาราง; access 15 นาที, refresh 14 วัน, reset 30 นาที; PBKDF2-HMAC-SHA256 600,000 รอบ salt 16 ไบต์; `FieldProtector` เข้ารหัสฝั่งเซิร์ฟเวอร์แบบ deterministic (AES-256-CBC, IV จาก HMAC ของค่า) เพื่อเทียบ unique ได้; รหัสผ่านใหม่ 8–128 ตัวอักษร มีตัวใหญ่ ตัวเล็ก ตัวเลข; reset request ทำแถวเก่าเป็น `INACTIVE`; reset สำเร็จ revoke token ทุกตัวของผู้ใช้; ไม่มี lockout | `e-commerce/repository/src/...` | อ่านจากไฟล์ ไม่ได้รัน |
| backend ต่างจาก spec: endpoint `api/authen/...` (spec ใช้ `v1/auth/...`), รับ username/password เป็นข้อความธรรมดา (spec บอกเข้ารหัสฝั่ง frontend), อายุ token 15 นาที/14 วัน (spec 3600 วินาที/7 วัน) | เทียบสองฝั่ง | อ่านจากไฟล์ |
| backend ตรวจ access token กับแถวในตารางตอน authorize หรือไม่ | — | **ไม่ได้ตรวจ** |

## สัญญา token ที่ spec ทุกเส้นพึ่ง (เสนอให้ใช้ถ้อยคำนี้)

- **ผู้เรียก (`userId`)** คือ `sub` ของ access token ที่ผ่านการตรวจ ไม่มีเส้นใดรับ `userId` ของผู้เรียกจากคำขอ
- **ตรวจ access token** ตามลำดับ: มี header `authorization: Bearer <token>` → ลายเซ็น, `iss`, `aud`, `exp` ถูกต้อง → มีแถวใน `authen.t_user_access_token` ที่ `token = SHA-256(token)` สถานะ `ACTIVE` และ `expired_at` ยังไม่ถึง → ผู้ใช้ (`authen.m_user`) สถานะ `ACTIVE` ข้อใดไม่ผ่าน → **401 `E10002` "Invalid or expired access token."** ข้อความเดียว ไม่บอกเหตุ
- ผลต่อ spec ที่ส่งแล้ว: **ไม่ต้องแก้ spec ใด** เพราะ spec เหล่านั้นอ้างแค่ header และ 401 `E10002` สัญญานี้ไม่เพิ่มรหัสหรือฟิลด์ที่ spec เหล่านั้นต้องรู้

## Authorization revision (2026-11-07)

The JWT includes role, permission and permission-specific scope claims, resolved when a token is issued by login or refresh. These claims authorize the caller until that access token expires; assignment changes need not take effect earlier. Keep the access-token and ACTIVE-user database checks above so logout and password reset revoke credentials immediately. This revises the U1 payload description and separates U2 credential revocation from authorization-assignment changes. [Owner approval and scope](2026-11-07-api-review-design.md).

### Login technical corrections under review

The login endpoint revision proposes serializing the failure counter by a transaction-scoped identifier advisory lock, locking matched users before password verification, and committing FAILED/REFUSED with no token writes in that attempt transaction. This replaces the earlier ordering and the literal “outside the token transaction” wording for login: only SUCCESS writes tokens, and its token pair plus attempt commit atomically. These implementation-level details remain in-review in the endpoint; the owner-approved rules remain the same 5 FAILED / 15-minute limit and durable log before a 401. A timeout before commit rolls all writes back. This paragraph does not approve unseen backend code.

## การตัดสินใจ

ป้าย: **เจ้าของงานตอบแล้ว** (ยังไม่มี), **รอเจ้าของงาน** (ต้องส่งผ่าน Josh), **รอ Josh** (แตะงานที่ส่งแล้ว หรือเป็นข้อตกลงข้ามโดเมน), **ตัดสินเอง** (ผมเลือก ถ้าผิดแก้ตามที่ระบุ) ตัวเลขเวลาเป็นค่า config ไม่ฝังใน schema

### Token

- **U1 (ตัดสินเอง)** รูปแบบ token: access token เป็น JWT HS256 มี `sub` (user id), `jti`, `iss`, `aud`, `iat`, `exp` (ตรงกับตัวอย่างใน `02-login`); refresh token และ reset token เป็นสุ่ม 32 ไบต์ (256 บิต) แบบ base64url ไม่ใช่ JWT; ตารางเก็บ **SHA-256 ของข้อความ token ทั้งก้อน** (32 ไบต์) ใน `token` และ `reset_token` ไม่เก็บค่าจริง เพราะ token สุ่ม 256 บิตแฮชเร็วได้ปลอดภัยและค้นด้วย `=` ได้ ฐานข้อมูลรั่วแล้วใช้ token ไม่ได้ ถ้าผิด (อยากเก็บค่าจริง): ต้องเข้ารหัสแบบเดียวกับข้อมูลส่วนบุคคลและเทียบเป็น `=` ได้ ซึ่งเสี่ยงกว่า
- **U2 (Lead ตัดสิน: อนุมัติ)** access token ตรวจกับแถวในตารางทุกคำขอ (สัญญาด้านบน) เพื่อให้ logout และการตั้งรหัสผ่านใหม่ทำให้ token ที่ออกไปแล้วใช้ไม่ได้ทันที ราคา: อ่านฐานข้อมูลหนึ่งครั้งต่อคำขอที่ต้องมี token ถ้าผิด (ยอมให้ access token ใช้ได้จนหมดอายุ): ตัดการค้นแถวออก logout ใช้ได้แค่กับ refresh token และ access token ที่หลุดใช้ได้ถึง `exp` (สั้นที่สุด 15 นาที ตามค่าที่เสนอใน U3)
- **U3 (เจ้าของงานตอบแล้ว: ตามที่แนะนำ 2026-11-06)** อายุ token: `02-login` บอก access 3600 วินาที refresh 7 วัน แต่ backend ตั้ง 15 นาทีและ 14 วัน และ reset token 30 นาที ผมเสนอ **access 15 นาที, refresh 14 วัน, reset 30 นาที** (access สั้นปลอดภัยกว่าเมื่อมี rotation) ถ้ายึดค่าเดิมของ spec ต้องแก้ backend ตามแทน การเปลี่ยนเป็น 15/14 ต้องแก้ตัวอย่าง `expiresIn` และข้อความ "7 day" ใน `02-login` (ข้อเสนอ ไม่แก้เอง) ถ้าผิด: เปลี่ยนค่า config และตัวเลขในตัวอย่าง ไม่กระทบ schema
- **U4 (ตัดสินเอง ต้องแก้ schema; ข้อ session ผูกกับ Q3)** แต่ละ login คือหนึ่ง **session**: คอลัมน์ใหม่ `session_id UUID NOT NULL` ในทั้งสองตาราง token (สร้างตอน login, refresh ใช้ค่าเดิมต่อ) ทำให้ logout ปิดเฉพาะเครื่องนั้น และตรวจ refresh ซ้ำได้ ถ้าผิด (ออกจากระบบทุกเครื่องเสมอ): ไม่ต้องมี `session_id` และ logout/refresh ซ้ำ ปิด token ทั้งหมดของผู้ใช้เหมือน backend ปัจจุบัน
- **U5 (ตัดสินเอง)** สถานะแถว token: `ACTIVE` ใช้ได้, `INACTIVE` ถูกใช้แล้ว/ถูกเพิกถอน/ถูกแทนที่ (ตรงกับที่ backend ใช้ `INACTIVE`) ไม่มีเส้นใดเปิดแถว `INACTIVE` กลับเป็น `ACTIVE` ไม่มีเส้น API ลบแถว แต่ทุก login และ refresh เพิ่มแถวในตาราง token ทั้งสอง แถวที่ `expired_at` เกิน **30 วัน** (ค่า config) ลบจริงได้ด้วยงานของระบบ (แถว reset ที่หมดอายุเกิน 30 วันเช่นกัน, `l_user_login_attempt` เกิน 30 วันตาม U10) งานนี้เป็นข้อกำหนดการ implement ไม่เขียนเป็น spec และไม่มีใครอ่านแถวที่ลบไปแล้วเพราะ token ที่หมดอายุใช้ไม่ได้อยู่แล้ว ถ้าผิด (ต้องเก็บประวัติ): ไม่ลบ ตารางโตตามจำนวน login ถ้าผิดเรื่องค่าสถานะ: เพิ่มค่า ไม่กระทบ schema

### Refresh และ logout

- **U6 (ตัดสินเอง)** `POST v1/auth/refresh-token` รับ `refreshAccessToken` ใน body (ชื่อเดียวกับฟิลด์ที่ `02-login` ตอบ) **ไม่มี header `authorization`** เพราะ access token อาจหมดอายุแล้ว พิสูจน์ตัวด้วย refresh token เอง ตรวจ: แถว `token = SHA-256(...)` สถานะ `ACTIVE` ยังไม่หมดอายุ และผู้ใช้ `ACTIVE` ผิดข้อใด → 401 `E10002` ข้อความ "Invalid or expired refresh token." ขาดฟิลด์ → 400 `E10001` สำเร็จ → 200 ตอบ `tokenType`, `accessToken`, `refreshAccessToken`, `expiresIn` เหมือน login
- **U7 (ตัดสินเอง)** **rotation**: refresh สำเร็จแล้ว refresh token เก่าเป็น `INACTIVE` ทันที (ใช้ได้ครั้งเดียว) ออก refresh ใหม่ (อายุเต็มตาม U3, `session_id` เดิม) และ access ใหม่ ส่วน access token เก่าของ session ยังใช้ได้จนหมดอายุ (สั้นอยู่แล้ว) ดังนั้น session หนึ่งมี access token ที่ยังไม่หมดอายุได้หลายตัว (หนึ่งตัวต่อ login หรือ refresh แต่ละครั้ง) ทุกจุดที่ปิด session (U8, U9, U13) จึงต้องปิด access token **ทุกตัวที่มี `session_id` เดียวกัน** ไม่ใช่เฉพาะตัวของคำขอ ถ้าผิด (ไม่ต้องการ rotation): refresh ใช้ซ้ำได้จนหมดอายุ ซึ่ง refresh ที่หลุดใช้ได้ 14 วัน
- **U8 (ตัดสินเอง)** ตรวจ **refresh token ที่ถูกใช้ซ้ำ**: ถ้าส่ง refresh ที่เป็น `INACTIVE` และยังไม่หมดอายุ ตอบ 401 `E10002` และ **ปิดทุก token ของ session นั้น ทั้ง refresh และ access ทุกตัวที่มี `session_id` เดียวกัน** (สมมติว่าถูกขโมย) ยกเว้นถ้าแถวนั้นเพิ่งเป็น `INACTIVE` ภายใน 10 วินาที (`updated_at`) เพราะผู้ใช้กดซ้ำหรือสองแท็บส่งพร้อมกัน ให้ตอบ 401 เฉยๆ โดยไม่ปิด session ค่า 10 วินาทีเป็น config ถ้าผิด (อยากปิดทันทีทุกกรณี): ผู้ใช้ที่ refresh พร้อมกันถูกเด้งออก
- **U9 (ตัดสินเอง; session ผูกกับ Q3)** `POST v1/auth/logout` ต้องมี `authorization` ไม่มี body ปิด **access token และ refresh token ทุกตัวที่มี `session_id` เดียวกัน** (รวม access token เก่าที่ออกจาก refresh ก่อนหน้า ซึ่งยังไม่หมดอายุ) ทำในธุรกรรมเดียวหลังล็อกแถวผู้ใช้ (U23) ผลคือหลัง logout ไม่มี token ใดของ session นั้นใช้ได้อีกทันที ตอบ 200 (`S10000` "Logout Success" ไม่มี `data`) ไม่ต้องบอกผลต่อ token ที่ปิดไปแล้ว เพราะเรียกซ้ำจะไม่ผ่านการตรวจ token (401) อยู่แล้ว ถ้าผิด (ต้องออกจากทุกเครื่อง): ปิดทุก token ของผู้ใช้ ตัวเลือกพารามิเตอร์ `allSessions` ทำได้โดยไม่เปลี่ยน schema

### กันเดารหัสผ่าน และไม่เปิดเผยว่ามี email

- **U10 (ตัดสินเอง ต้องแก้ schema และเสนอแก้ login; ตัวเลขรอเจ้าของงาน Q2)** นับครั้งที่ login ผิดในตารางใหม่ `authen.l_user_login_attempt` (`identifier_hash` = SHA-256 ของ username ที่ส่งมา, `user_id` เป็น NULL ได้ (ชื่อที่ไม่มีในระบบก็นับ), `is_success`, `created_at`) กฎ: ผิดครบ **5 ครั้งใน 15 นาที** ต่อ `identifier_hash` → login ถัดไปในช่วงนั้นถูกปฏิเสธโดยไม่ตรวจรหัสผ่าน ด้วย **401 `E10002` "Invalid username or password." ข้อความเดียวกับรหัสผิดปกติ** เพื่อไม่บอกว่าถูกล็อก และนับครั้งที่ปฏิเสธเพิ่มด้วย ไม่ล็อกถาวร (สถานะ `LOCKED` ของ `m_user` สงวนไว้ให้ผู้ดูแล) ข้อมูลเก่าเกิน 30 วันลบได้ด้วยงานของระบบ (config) ราคา: ผู้ไม่หวังดีล็อก login ของคนอื่นได้ครั้งละ 15 นาที ถ้าผิด (ไม่ต้องการล็อก): จำกัดที่ gateway ตามไอพีอย่างเดียว ตาราง `l_user_login_attempt` ตัดออกได้
  - **ปรับโดย Lead หลังประตู 2 (2026-11-06; Josh แจ้งเจ้าของงาน):** ครั้งที่ถูกปฏิเสธเพราะล็อกอยู่ ต้องไม่ถูกนับ มิฉะนั้นคำขอใดๆ ทุก 15 นาทีทำให้ล็อกไม่หมด ดังนั้นตาราง `l_user_login_attempt` เก็บ `result` (`SUCCESS`, `FAILED`, `REFUSED`) แทน `is_success` บันทึกทุกคำขอ แต่นับเฉพาะ `FAILED` (ตรวจรหัสผ่านจริงแล้วผิด หรือไม่พบผู้ใช้) ล็อกจึงหมดเองเมื่อครั้งผิดครั้งที่ 5 เก่าเกิน 15 นาที คอลัมน์ยังมี 6 คอลัมน์ README ไม่เปลี่ยน ราคาที่เหลือ: ผู้ไม่หวังดีที่ส่งรหัสผิด 5 ครั้งทุกๆ 15 นาทีล็อกบัญชีนั้นได้ต่อเนื่อง (ต้องใช้ 5 คำขอต่อรอบ) ซึ่งเป็นราคาเดียวกับที่ระบุไว้ข้างต้น ถ้าผิด: จำกัดที่ gateway ด้วย
  - **U29 (ตัดสินเอง ตามคำสั่ง Josh)** `05-refresh-token` กรณีใช้ซ้ำ: การปิดทั้ง session ถูก commit แม้คำตอบเป็น 401 (เขียนในธุรกรรมของตัวเองที่ commit ก่อนตอบ ไม่ rollback พร้อมคำขอ) ผู้ใช้ที่ไม่ ACTIVE ถูกตัดตั้งแต่ขั้นล็อกแถวผู้ใช้ ก่อนการ rotation จึงไม่มีอะไรเปลี่ยน (refresh token ไม่ถูกทำเป็น `INACTIVE`) การ rotation ออก token ใหม่และตอบ 200 เป็นธุรกรรมเดียว ล้มแล้วไม่บันทึกอะไร ในทำนองเดียวกัน แถว `FAILED` และ `REFUSED` ของ login commit แม้ตอบ 401 ถ้าผิด: ผู้ implement ต้องเดา
- **U11 (ตัดสินเอง)** ขอรีเซ็ตรหัสผ่าน `POST v1/auth/reset-password` ไม่มี `authorization` รับ `emailAddress` (เข้ารหัสแบบ `register`) **ตอบ 200 ข้อความเดียวกันเสมอ** ไม่ว่า email มีในระบบหรือไม่ ผู้ใช้ไม่ `ACTIVE` หรือถูกจำกัดความถี่ ("If the email address is registered, a reset link has been sent.") ถ้ามีผู้ใช้ `ACTIVE`: ทำแถว reset เดิมที่ `ACTIVE` เป็น `INACTIVE` สร้างแถวใหม่ (`reset_token` = SHA-256 ของ token สุ่ม, `expired_at` = ตอนนี้ + 30 นาที) แล้วสั่งส่ง email ลิงก์ที่มี token (นอก spec) ความถี่: ผู้ใช้หนึ่งคนขอได้ไม่เกิน **3 ครั้งต่อชั่วโมง** (นับแถว `t_user_reset_password` ที่สร้างใน 1 ชั่วโมง) เกินแล้วตอบ 200 เหมือนเดิมแต่ไม่สร้างหรือส่งอะไร เหตุผล: 429 ใหม่เป็นรหัสใหม่ (ต้องถามก่อน) และบอกว่ามีผู้ใช้ ถ้าผิด (อยากให้ผู้ขอมากเกินรู้): เพิ่มรหัส 429 ต้องถามเจ้าของโครงสร้างรหัส เวลาตอบควรใกล้เคียงกันทุกกรณี (ไม่ตอบเร็วกว่าเมื่อไม่พบผู้ใช้) ข้อนี้เป็นข้อกำหนดการ implement
- **U12 (ตัดสินเอง)** `t_user_reset_password`: หนึ่งผู้ใช้มีแถว `ACTIVE` ได้ไม่เกินหนึ่งแถว บังคับด้วย partial unique index `uq_t_user_reset_password_user_id_active ON (user_id) WHERE row_status = 'ACTIVE'` ถ้าผิด: คุมในแอปแทน (เสี่ยงสองคำขอพร้อมกัน)
- **U13 (ตัดสินเอง)** ตั้งรหัสผ่านใหม่ `POST v1/auth/create-new-password` ไม่มี `authorization` รับ `resetToken` (ข้อความ token ตามที่ส่งใน email) และ `newPassword` (เข้ารหัสแบบ `register`) ตรวจ: ฟิลด์ครบ (400 `E10001`) → รหัสผ่านตามนโยบาย 8–128 ตัวอักษร มีตัวพิมพ์ใหญ่ ตัวพิมพ์เล็ก และตัวเลข (400 `E10001`; ตรงกับ backend; ค่านโยบายเป็น config) → แถว reset ที่ `reset_token = SHA-256(resetToken)` สถานะ `ACTIVE` ยังไม่หมดอายุ และผู้ใช้ `ACTIVE` (ผิดข้อใด → **400 `E10001` "Reset token is invalid or expired."** ข้อความเดียว ไม่แยกว่าหมดอายุ ถูกใช้แล้ว หรือไม่มี) → รหัสผ่านใหม่ต้องไม่ตรงกับรหัสผ่านปัจจุบัน (400 `E10001`) แล้วเขียนในธุรกรรมเดียว: แถว reset เป็น `INACTIVE` ด้วย `UPDATE ... WHERE id = ... AND row_status = 'ACTIVE' AND expired_at > <now> RETURNING id` (**ใช้ได้ครั้งเดียว**; ถ้าได้ 0 แถว เพราะมีคำขอซ้ำพร้อมกันที่ใช้ไปก่อนหรือหมดอายุระหว่างทาง ตอบ 400 `E10001` ข้อความเดียวกับไม่พบ และไม่เปลี่ยนอะไร), แถว `m_user_password` `PASSWORD` ปัจจุบันเป็น `INACTIVE`, เพิ่มแถว `PASSWORD` ใหม่ (hash ตาม U15), **ปิด access และ refresh token ทุกตัวของผู้ใช้ในทุก session** (ทุกแถว `ACTIVE` ของทั้งสองตารางตาม `user_id` รวม access token เก่าของแต่ละ session) ตอบ 200 ไม่มี `data` และไม่ล็อกอินให้ ผู้ใช้ต้อง login ใหม่ ถ้าผิด: เปลี่ยนที่ขั้นที่เกี่ยวข้อง
- **U14 (ตัดสินเอง ต้องแก้ schema ที่ส่งแล้ว รอ Josh)** `m_user_password`: หนึ่งผู้ใช้มีแถว `PASSWORD` ที่ `ACTIVE` ได้ไม่เกินหนึ่งแถว (partial unique index `uq_m_user_password_user_id_password ON (user_id) WHERE row_type = 'PASSWORD' AND row_status = 'ACTIVE'`) เพราะ `02-login` ไม่ระบุว่าจะเลือกแถวไหนถ้ามีสองแถว `01-register` เพิ่มหนึ่งแถวต่อผู้ใช้จึงไม่ชน และค่า `TEMPORARY_PASSWORD` ไม่ถูกใช้ใน WP4 (reset ใช้ token ไม่ใช่รหัสผ่านชั่วคราว) ถ้าผิด: ไม่ใส่ index ผลคือเสี่ยงมีสองแถว `ACTIVE`
- **U15 (Lead ตัดสิน: อนุมัติ ตรงกับค่าแนะนำปัจจุบันของ PBKDF2-SHA256)** การแฮชรหัสผ่าน: spec `register`/`login` เก็บ `password` และ `password_salt` แต่ไม่ระบุอัลกอริทึม ผมเสนอบันทึกใน spec ใหม่ว่าใช้ **PBKDF2-HMAC-SHA256, salt สุ่ม 16 ไบต์, 600,000 รอบ** (ตรงกับ backend ปัจจุบัน; จำนวนรอบเป็นค่าคงที่ในโค้ด เพราะ schema ไม่มีคอลัมน์เก็บ) และเทียบแบบ constant time ถ้าผิด (อยากใช้ Argon2id): ต้องเพิ่มคอลัมน์บอกอัลกอริทึมและพารามิเตอร์ใน `m_user_password`

### ข้อมูลส่วนบุคคลและโปรไฟล์

- **U16 (เจ้าของงานตอบ Q5 แล้ว: ตามที่แนะนำ — ฟิลด์อ่อนไหวส่งเป็นข้อความธรรมดาผ่าน TLS แล้วระบบเข้ารหัสฝั่งเซิร์ฟเวอร์)** ทุกเส้นใหม่รับ `emailAddress`, `newPassword`, `firstName`, `lastName`, `phoneNumber`, `address` และฟิลด์ที่อยู่เป็นข้อความธรรมดา ระบบเข้ารหัสแบบ deterministic ฝั่งเซิร์ฟเวอร์ก่อนเก็บเพื่อเทียบ unique ได้ inquiry คืนข้อความธรรมดา (ระบบถอดรหัสให้) ไม่คืน `username` `01-register` และ `02-login` ต้องตัดข้อความ "เข้ารหัส AES256 Key และ IV ฝั่ง frontend" ออกและบอกว่าส่งข้อความธรรมดาผ่าน TLS (แก้ในรอบ 2) ข้อความเดิมของ U16 ที่ว่า inquiry คืนค่าในรูปเดียวกับที่รับ ยังเป็นจริง (รับข้อความธรรมดา คืนข้อความธรรมดา) ถ้าผิด: เปลี่ยนรูปแบบ request/response ทุกเส้น ฟิลด์ที่ `register` รับแบบเข้ารหัสฝั่ง frontend (`username`, `emailAddress`, `password`, `firstName`, `lastName`) เส้นใหม่รับแบบเดียวกัน: `emailAddress` ในขอรีเซ็ต, `newPassword`, `firstName`, `lastName` ของโปรไฟล์ ฟิลด์ที่ `register` รับเป็นข้อความธรรมดาแล้วระบบเก็บเป็นไบต์ (`phoneNumber`, `address`, `title` ที่ไม่เข้ารหัส, `city`, `state`, `postalCode`, `country`) เส้นใหม่รับเป็นข้อความธรรมดาเช่นกัน inquiry คืนค่าในรูปเดียวกับที่รับ (ฟิลด์ที่ frontend เข้ารหัสคืนข้อความเข้ารหัสเดิม ฟิลด์ที่ระบบเข้ารหัสคืนข้อความธรรมดา) ไม่มีการคืน `username` ถ้าผิด: เปลี่ยนรูปแบบ request/response ของเส้นใหม่ที่เกี่ยวข้อง
- **U17 (ตัดสินเอง ต้องแก้ schema ที่ส่งแล้ว รอ Josh)** `m_user_information`: หนึ่งผู้ใช้มีได้หนึ่งแถว (partial unique index `uq_m_user_information_user_id ON (user_id) WHERE row_status <> 'DELETED'`) เพราะ `register` สร้างหนึ่งแถวและโปรไฟล์เป็นการแก้แถวเดียว ถ้าผิด: ไม่ใส่ index
- **U18 (ตัดสินเอง)** โปรไฟล์ `POST v1/user/profile/upsert` และ `GET v1/user/profile` เป็นข้อมูลของผู้เรียก (`userId` จาก token ไม่รับจากคำขอ) ไม่มี batch (แถวของลูกค้าเอง ตามกติกาโปรเจกต์) upsert แก้ `m_user` (`first_name`, `last_name`, `display_name`, `profile_picture_path`) และ `m_user_information` (`phone_number`, `address`, `date_of_birth`, `gender`) ในธุรกรรมเดียว ฟิลด์ที่ไม่ส่งคงค่าเดิม ส่ง `null` เพื่อล้างค่าที่ไม่บังคับ `username`, `emailAddress` แก้ไม่ได้ (ถ้าส่งมา 400) `displayName` ยังเป็นข้อความธรรมดาไม่เกิน 128 ตัวอักษรเหมือนเดิม เพราะ `shop/13`, `shop/16`, `sales/04` อ่านไปแสดง ผู้ใช้ `ACTIVE` เท่านั้นที่เรียกได้ ไม่มีการลบ (ไม่มีเส้นลบบัญชี) ถ้าผิด: เปลี่ยนที่ spec 07, 08
- **U19 (ตัดสินเอง ต้องแก้ schema ที่ส่งแล้ว รอ Josh)** ที่อยู่: `POST v1/user/address/upsert` และ `GET v1/user/address` ของผู้เรียก ไม่มี batch ไม่มี archive (สถานะที่ใช้: `ACTIVE`, `INACTIVE`, `DELETED`) ที่อยู่ที่ `ACTIVE` เท่านั้นที่ checkout ใช้ได้ (ตรงกับ `sales/01`, `02`) ที่อยู่ `default` ได้หนึ่งที่ต่อผู้ใช้ บังคับด้วย partial unique index `uq_t_user_address_user_id_default ON (user_id) WHERE is_default AND row_status <> 'DELETED'` ที่อยู่แรกเป็น default อัตโนมัติ ตั้ง default ใหม่แล้วที่อยู่เดิมถูกปลด default ในธุรกรรมเดียว ลบ (`DELETED`) หรือปิด (`INACTIVE`) ที่อยู่ default ได้ ระบบตั้งที่อยู่ `ACTIVE` ที่แก้ล่าสุดเป็น default แทน (ถ้ามี) ผู้ใช้มีที่อยู่ไม่เกิน 10 ที่ (config; เกิน → 400 `E10001`) ลบแบบ soft เท่านั้น เพราะ `sales.t_order.address_id` เป็น `RESTRICT` และออเดอร์เก็บสำเนาที่อยู่ไว้แล้ว (R42) ที่อยู่ของผู้ใช้อื่นนับว่าไม่พบ (404 `E10004`) ถ้าผิด (ห้ามลบที่อยู่ default): ตอบ 409 `E10006` แทนการตั้ง default ใหม่

### สัญญาและรหัส

- **U20 (ตัดสินเอง)** ไม่เพิ่ม bizCode ใหม่: ฟิลด์ขาด รหัสผ่านไม่ตามนโยบาย reset token ใช้ไม่ได้ เกินจำนวนที่อยู่ → 400 `E10001`; token ผิดหรือหมดอายุ (access, refresh), login ผิดหรือถูกจำกัด → 401 `E10002`; ไม่พบที่อยู่ → 404 `E10004`; timeout → 408 `E90001` ไม่มี 403 ในเส้นของ WP4 (ทุกเส้นเป็นข้อมูลของผู้เรียกหรือสาธารณะแบบมีลายเซ็น/token) ไม่มี 429 ถ้าผิด: ต้องถามเรื่องรหัสใหม่
- **U21 (ตัดสินเอง)** ตัวอย่าง token ใน spec ใหม่ตัดท้ายด้วย `...` และไม่ใช่ JWT เต็มสามส่วน (ตัวสแกนความลับจับ) ตัวอย่าง refresh/reset ใช้ข้อความ base64url ตัดท้าย `...`
- **U22 (ตัดสินเอง)** เลขโฟลเดอร์และ endpoint: `03-reset-password` (`POST v1/auth/reset-password`), `04-create-new-password` (`POST v1/auth/create-new-password`), `05-refresh-token` (`POST v1/auth/refresh-token`), `06-logout` (`POST v1/auth/logout`), `07-upsert-user-profile` (`POST v1/user/profile/upsert`), `08-inquiry-user-profile` (`GET v1/user/profile`), `09-upsert-user-address` (`POST v1/user/address/upsert`), `10-inquiry-user-address` (`GET v1/user/address`) โฟลเดอร์ `03`, `04` เป็น template ว่างอยู่แล้ว เติมเนื้อหาแทน ถ้าผิด: เปลี่ยนชื่อโฟลเดอร์และ endpoint ในไฟล์ใหม่

### ความพร้อมกัน

- **U23 (Lead เสนอ ผมรับ)** ลำดับล็อกของ WP4: **ล็อกแถว `authen.m_user` ของผู้ใช้ก่อนเสมอ** (`SELECT ... FOR UPDATE`) แล้วจึงอ่านและแก้ token, reset และ password ใช้เหมือนกันใน login (สร้าง session), refresh, logout, reset-password (สร้างแถว reset) และ create-new-password ทำให้ไม่เกิด deadlock และ refresh ซ้ำพร้อมกันสองคำขอผ่านได้แค่ตัวเดียว: ตัวที่สองเห็นแถว `INACTIVE` ที่เพิ่งเปลี่ยนจึงเข้ากรณี 10 วินาทีของ U8 (401 ไม่ปิด session) การเปลี่ยนสถานะ token ทุกครั้งเป็น `UPDATE` ที่ตรวจสถานะเดิม (`WHERE row_status = 'ACTIVE' ... RETURNING`) และได้ 0 แถวถือว่าไม่ผ่าน ไม่ใช่ข้อผิดพลาดของระบบ ตัวตรวจ access token (สัญญา token) เป็นการอ่านอย่างเดียว ไม่ล็อกแถวผู้ใช้ ถ้าผิด: เปลี่ยนลำดับล็อก (ผลต่อ spec คือประโยคกติกาและตัวอย่าง SQL ของ 5 เส้น)

### ตัดสินใจเพิ่มระหว่างรอบ 2 (ตัดสินเอง)

- **U24** `GET v1/user/profile` คืน `emailAddress` (อ่านอย่างเดียว ถอดรหัสให้) เพราะหน้าโปรไฟล์ต้องแสดง และไม่คืน `username` ตาม U16 ถ้าผิด: ตัดฟิลด์ออกจาก spec 08 และตัวตรวจ
- **U25** ดัชนีค้นของตาราง `l_user_login_attempt` เป็น `CREATE INDEX` ธรรมดา (`ix_l_user_login_attempt_identifier_hash_created_at`) ซึ่งเดิมไม่มีในโปรเจกต์ (มีแต่ unique) ผมแก้ `audit_all.py` ให้รู้จัก `CREATE INDEX` ธรรมดา (เปลี่ยนบรรทัดเดียวที่ `indexes_of` และข้อความ) ถ้าผิด (ไม่ต้องการดัชนีธรรมดา): ตัดดัชนีออกจาก migration, doc, ตัวตรวจและ test แล้วคืน `audit_all.py`
- **U26** `check_docs.py` มีข้อความ "52 tables in 11 schemas" ฝังอยู่ในตัวตรวจ `schema` ผมเปลี่ยนเป็น 53 (บรรทัดเดียว ต้องเปลี่ยนทุกครั้งที่เพิ่มตาราง) การรวมกับ branch อื่นที่เพิ่มตารางต้องปรับเลขนี้
- **U27** แถว `session_id` ในแผนภาพ ER วางที่ท้ายตาราง token (ไม่ใช่หลัง `user_id`) เพื่อไม่ต้องเลื่อนแถวและเส้น FK เดิม ตัวตรวจไม่เทียบลำดับแถว ถ้าผิด: ย้ายแถว
- **U28** ตัวสร้างไฟล์ spec 03–10 เป็นสคริปต์ชั่วคราวนอก repo (ใช้ `spec_helpers.py`) แล้วตรวจและแก้เอง ไม่มีสคริปต์ค้างใน repo

## ข้อเสนอแก้ `02-login` (Josh ให้ผมแก้ใน WP4 รอบ 2 หลังเจ้าของงานอนุมัติ ผ่านประตู 2 พร้อมกัน)

เมื่อ WP4 ผ่าน `02-login` ต้องเปลี่ยน มิฉะนั้นสัญญา token ด้านบนเป็นจริงไม่ได้:

1. **บันทึก token** (U1, U4): หลังรหัสผ่านถูก ในธุรกรรมเดียวสร้าง `session_id`, เพิ่มแถว `t_user_access_token` และ `t_user_refresh_token` (เก็บ SHA-256) พร้อมคำสั่ง SQL `INSERT` ในหัวข้อ Database Relations
2. **กันเดารหัสผ่าน** (U10): ก่อนตรวจรหัสผ่านนับ `l_user_login_attempt` และหลังตรวจบันทึกผล พร้อม query และกฎใน spec
3. **อายุ token** (U3): ถ้าเจ้าของงานเลือก 15 นาที/14 วัน แก้ `expiresIn` ในตัวอย่างและข้อความ "7 day"
4. **mobile no** : คำอธิบายบอกว่า login ด้วยเบอร์โทรได้ แต่ SQL ตรวจแค่ `username` และ `email_address` และเบอร์โทรเก็บเป็นไบต์ใน `m_user_information` โดยไม่มี unique ผมเสนอให้ตัดคำว่า mobile no ออกจากคำอธิบายและฟิลด์ (ถ้าต้องการจริง ต้องมีกฎเรื่องเบอร์ซ้ำ) ผมไม่ได้ตัดสินแทน
5. **ตัวอย่าง access token** เป็น JWT สามส่วนเต็ม ขัดกับกติกาตัวอย่างของ WP4 (U21) ตัวสแกนไม่ได้จับในงานที่ส่งแล้ว แต่ควรตัดท้ายด้วย `...` เมื่อแก้ครั้งเดียว
6. ผู้ใช้ที่ไม่ `ACTIVE` ตอบ 401 เหมือนรหัสผิด (ตรงกับที่ query ตรวจ `row_status = 'ACTIVE'` อยู่แล้ว) ไม่ต้องแก้ แต่ให้เขียนเป็นกฎ

## ข้อเสนอแก้ `01-register` (ไม่แก้เอง Josh ให้ผมแก้ใน WP4 รอบ 2 หลังเจ้าของงานอนุมัติ)

1. **ที่อยู่ default (U19):** spec ปัจจุบันระบุ `addresses` เป็นอ็อบเจ็กต์เดียว (ตัวอย่างและ SQL สร้างหนึ่งแถว) จึงยังไม่มีคำขอที่มี default สองที่ แต่กติกา U19 บอกว่าที่อยู่แรกของผู้ใช้เป็น default อัตโนมัติ register จึงต้องตั้ง `is_default = TRUE` ให้ที่อยู่ที่ส่งมา (ไม่ว่า `isDefault` จะเป็นอะไร) และเขียนไว้เป็นกฎ ถ้า contract เปลี่ยนเป็นรายการที่อยู่ (array) ในภายหลัง ต้องตรวจว่า default ได้ไม่เกินหนึ่งที่ (400 `E10001`) และถ้าไม่มีเลยให้ที่อยู่แรกเป็น default เพื่อไม่ให้ unique index ของ U19 ล้มที่ฐานข้อมูลโดยไม่มีข้อความใน spec
2. **รูปแบบ request (U16):** ปรับตามคำตอบ Q5 ถ้าเจ้าของงานเลือกให้ส่งข้อความธรรมดา
3. **ลำดับล็อก (U23):** ถ้า register ต้องล็อกอะไร ให้บันทึกไว้ (ตอนนี้ register สร้างผู้ใช้ใหม่ จึงไม่มีแถวให้ล็อก)

ข้อเสนออื่นที่ไม่แตะ login: `01-register` ตอบ 409 "Username or email address already exists." ซึ่งเปิดเผยว่า username หรือ email มีในระบบ (ผู้ไม่หวังดีเดาว่ามีบัญชีได้) แลกกับความสะดวกของผู้สมัคร ไม่แก้ใน WP4 Josh ลงเป็นประเด็นให้เจ้าของงานตัดสินเอง ไม่อยู่ใน WP4

## คำถามธุรกิจ (เสนอเป็นชุดเดียว เรียงตามความสำคัญ)

1. **Q1 อายุ token (U3)** — คำแนะนำ: access 15 นาที, refresh 14 วัน, reset 30 นาที (ตรงกับ backend; ต้องแก้ตัวอย่างใน `02-login`) · ถ้าผิด: ยึด 3600 วินาที/7 วัน ตามที่ spec เดิมเขียน โดยแก้ค่า config ของ backend แทน
2. **Q2 กฎล็อก login (U10)** — คำแนะนำ: ผิด 5 ครั้งใน 15 นาที ปฏิเสธชั่วคราวโดยตอบเหมือนรหัสผิด · ถ้าผิด: ไม่ล็อก (พึ่ง gateway) ผู้ไม่หวังดีเดารหัสผ่านต่อได้ไม่จำกัดที่ระดับแอป; หรือใช้ตัวเลขอื่น (ค่า config)
3. **Q3 logout (U9)** — คำแนะนำ: ออกจากระบบเฉพาะเครื่องที่กด · ถ้าผิด: ออกทุกเครื่อง ซึ่งง่ายกว่าและไม่ต้องมี `session_id`
4. **Q4 ขอบเขต** — คำแนะนำ: เปลี่ยน email/username และเปลี่ยนรหัสผ่านขณะล็อกอินอยู่ แยกเป็นงานทีหลัง (ไม่อยู่ใน WP4) · ถ้าผิด: เพิ่มเส้นใน WP4 และ schema (เช่น การยืนยัน email ใหม่)

5. **Q5 รูปแบบข้อมูลที่ส่ง (U16)** (Josh ถามเจ้าของงาน) — คำแนะนำของ Josh: ส่งข้อความธรรมดาผ่าน TLS แล้วระบบเข้ารหัสฝั่งเซิร์ฟเวอร์ เพราะกุญแจ AES ที่ฝังไปกับแอปไม่ให้ความลับและตรงกับ backend ที่มีอยู่ · ถ้าผิด (ยึดเข้ารหัสฝั่ง frontend ตาม spec เดิม): `register` และ `login` ไม่ต้องแก้ แต่ backend ต้องเปลี่ยนมารับข้อความเข้ารหัส · ผลต่อ spec ที่ส่งแล้ว: ถ้าเลือกข้อความธรรมดา ต้องแก้คำอธิบายฟิลด์และตัวอย่างของ `01-register`, `02-login` (ฟิลด์ `username`, `emailAddress`, `password`, `firstName`, `lastName`) ผมทำในรอบ 2 พร้อมข้อเสนอแก้อื่น

ประเด็นที่ Josh ลงให้เจ้าของงานตัดสินเอง (ไม่อยู่ใน WP4): `01-register` ตอบ 409 เปิดเผยว่ามี username หรือ email ในระบบ

ตัดสินโดย Lead แล้ว: U2 (ตรวจแถว token ทุกคำขอ), U15 (PBKDF2-HMAC-SHA256 salt 16 ไบต์ 600,000 รอบ) ที่ยังรอเจ้าของงาน: U10 (ตารางล็อก login), U14, U17, U19 (partial unique บนตารางที่ส่งแล้ว: `m_user_password`, `m_user_information`, `t_user_address`) และ Q1 ถึง Q5

## สิ่งที่พบนอกขอบเขต (ไม่แก้ รายงานแยก)

- spec `register`/`login` บอกเข้ารหัสฝั่ง frontend ด้วย AES256 Key และ IV แต่ backend รับข้อความธรรมดาแล้วเข้ารหัสฝั่งเซิร์ฟเวอร์ (deterministic) ต้องตัดสินว่ายึดฝั่งไหน ถ้า Key และ IV ฝั่ง frontend เป็นค่าคงที่ที่ส่งไปกับแอป ก็ไม่ได้ให้ความลับ (ใครก็ถอดได้) และ IV คงที่ทำให้เทียบ unique ได้แต่เดาค่าซ้ำได้ ผมเขียน spec ใหม่ตามแนว `register` (U16) และขอ Josh ตัดสิน
- `m_user.username` และ `email_address` เป็น `UNIQUE` ธรรมดา (ผู้ใช้ที่ถูกลบแบบ soft จะถือ username ตลอดไป) ไม่มีเส้นลบบัญชีจึงยังไม่เป็นปัญหา
- `m_user_information.address` (ที่อยู่ใน information) ซ้ำบทบาทกับ `t_user_address` ผมยังเก็บไว้ในโปรไฟล์ตาม `register` ไม่เสนอให้ลบ
- ผมไม่ได้ตรวจว่า backend ตรวจแถว token ตอน authorize หรือไม่ (ดูตารางข้อเท็จจริง)

## ยังไม่ได้ตรวจ

ยังไม่ได้รัน `check_docs.py`, `audit_all.py`, `run_db_tests.sh` (รอบ 1) โค้ด backend อ่านอย่างเดียว ไม่ได้ build หรือรัน ไม่ได้ตรวจเอกสารภายนอกใดๆ และไม่ได้ตรวจว่า branch อื่นของ Tommy (shipping, campaign) หรือ WP6 แตะ `01-authen`, `check_docs.py` ตำแหน่งเดียวกัน (Josh แจ้งว่าตำแหน่งแทรกก่อน `def main` ชนกันและจะเก็บทั้งสองบล็อกตอนแพ็ก)
