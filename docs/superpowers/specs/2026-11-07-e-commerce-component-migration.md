---
name: E-commerce Backend Component Repository Migration
description: แผนย้าย backend ที่ยัง track ใน Showcase ไปเป็น Component Repository ใช้ยืนยันชื่อ remote ประวัติ การสำรองไฟล์ และลำดับส่งมอบก่อน migration
status: approved
approved_by: ittikorn
approved_at: 2026-11-07T14:00:23Z
---

# E-commerce Backend Component Repository Migration

## 1. เหตุผลและหลักฐาน

ผู้ใช้ขอแก้การวาง backend ใต้ `e-commerce/repository/` และสร้าง repository บน GitHub ที่ยังไม่มี ตาม [component-repositories rule](../../../.agents/rules/component-repositories.md) และ [ADR 0001](../../adr/0001-independent-component-repositories.md)

ข้อเท็จจริงที่ตรวจเมื่อ 7 พฤศจิกายน 2026:

- Showcase คือ `ittikornsopawan/system-analysis-and-design` มี visibility PUBLIC และ default branch `main`
- `e-commerce/REPOS.md` ยังไม่มี จึงเป็น migration-pending
- backend อยู่ตรง `e-commerce/repository/` และมีไฟล์ tracked 81 ไฟล์ รวมคู่มือ `code.md`
- ไม่มี nested `.git` ที่ root ของ backend; source ยังเป็นของ Showcase
- มี ignored build artifacts ใต้ source/tests ต้องเก็บไว้โดยไม่ใส่ใน repository ใหม่
- ไม่พบ repository ชื่อเกี่ยวกับ e-commerce ในรายการ GitHub repositories ที่บัญชีนี้เข้าถึงขณะตรวจ
- PR #33 ของ code guide merge แล้วที่ `cb5e4e1aeaa040237674810f0f52ebbc20ee02e1`
- planning branch เริ่มจาก `48c75ab59f27e915d0bff7acf4395eeaafca330a`; ก่อน export ต้องตรวจ upstream อีกครั้งและบันทึก source SHA ที่ใช้จริง

bootstrap skill หยุดก่อน materialize เมื่อไม่มี manifest งานนี้จึงเป็น migration ที่ขออนุมัติแยก ไม่ใช่การให้ bootstrap ย้าย legacy directory เอง หลัง migration จึงใช้ขั้นตอน bootstrap กับ manifest ที่ถูกต้อง

## 2. ข้อเสนอที่ต้องยืนยันก่อนเปลี่ยน ownership

| Decision | ข้อเสนอ | เหตุผลและผลกระทบ |
| --- | --- | --- |
| M1 GitHub owner/name | `ittikornsopawan/e-commerce-backend` | สื่อว่าเป็น backend ของ e-commerce โดยใช้ owner เดียวกับ Showcase ต้องตรวจว่าชื่อยังว่างก่อนสร้าง |
| M2 Visibility | PUBLIC | รักษาระดับการเปิดเผยเดียวกับ Showcase เดิม; ไม่เพิ่มสิทธิ์เข้าถึง private code |
| M3 Checkout path | `e-commerce/repository/e-commerce-backend/` | ชื่อ directory ตรง remote slug และมี Git history/remote แยกตาม rule |
| M4 History | เก็บเฉพาะประวัติ subtree `e-commerce/repository/` | ใช้ `git subtree split` ใน temporary clone โดยไม่ rewrite ประวัติ Showcase; filtered commit SHAs จะเปลี่ยน แต่รักษา backend changes และ authorship ที่เกี่ยวข้อง |
| M5 Component contents | source, tests, solution/build configuration, `.gitignore`, README และ coding guides | ส่งเฉพาะ tracked files ของ backend; ไม่มี build output, Showcase Git metadata, credentials หรือ unrelated handoffs |
| M6 Initial publication | ส่ง filtered history และ migration documentation commit ไป `main` ของ repository ใหม่ | เป็น initial import สำหรับ remote ที่เพิ่งสร้าง ไม่แก้หรือ force-push branch ของ repository ที่มีอยู่ |
| M7 Showcase delivery | เปิด PR แยกสำหรับ migration โดยไม่ merge | แยกการเปลี่ยน ownership ออกจาก PR คู่มือที่ merge แล้ว; parent pin เกิดหลัง child delivery/verification สำเร็จ |
| M8 Existing files | เก็บ original backend directory ทั้งชุดใน backup ที่ระบุตำแหน่งได้ ก่อนเปลี่ยน checkout layout | รักษา ignored artifacts และ local state; ไม่ reset/clean/delete backup ระหว่างงานนี้ |

การอนุมัติแผนนี้ครอบคลุม M1–M8 ได้แก่การสร้าง repository ใหม่, initial import บน child main, migration layout และ commit/push/open PR ของ Showcase โดยไม่รวม merge, force push, เปลี่ยน visibility ภายหลัง, ลบ repository หรือแก้ backend behavior

## 3. โครงสร้างปลายทาง

```text
Showcase Repository
├── .gitignore
├── .agents/knowledge/projects/e-commerce.md
└── e-commerce/
    ├── REPOS.md
    ├── api/
    ├── db/
    ├── diagram/
    ├── doc/
    └── repository/
        ├── .gitkeep
        └── e-commerce-backend/     ignored by Showcase; independent clone
            ├── .git/
            ├── .gitignore
            ├── Ecommerce.sln
            ├── Directory.Build.props
            ├── README.md
            ├── project-structure.md
            ├── code.md
            ├── src/
            └── tests/
```

Showcase ติดตามเฉพาะ manifest และ `.gitkeep` ใต้ Checkout Directory โดยไม่ใช้ submodule ส่วน API/schema/migrations/diagrams และ shared agent resources ยังคงเป็นของ Showcase

Manifest ใช้ fields ตาม [repository-manifest template](../../../.agents/templates/repository-manifest.md): `name`, credential-free `remote`, `path`, `default_branch`, full `revision`, `release_tag: null`, `required: true`, `purpose` ระบุ backend baseline ตามความเป็นจริง ยังไม่สร้าง SHA สมมติหรือ pin local-only commit

Root `.gitignore` ต้องมีทั้ง `/e-commerce/repository/e-commerce-backend/` และ `/*/repository/.bootstrap-*/`

## 4. ลำดับ migration และการรักษาข้อมูล

1. ตรวจ source revision, tracked/ignored/untracked inventory และ hash ของไฟล์ทุกไฟล์ที่จะย้าย หากพบการแก้ source โดย session อื่น ให้หยุดการย้ายและแยก state ให้ชัดเจน
2. สร้าง temporary export workspace ที่มีชื่อเฉพาะใน `/private/tmp/` โดยไม่ใส่ Git metadata ใน legacy Checkout Directory
3. สร้าง filtered history เฉพาะ backend ด้วย `git subtree split` ใน temporary clone ไม่แก้ commits/refs ของ Showcase main
4. เทียบ exported tree กับ tracked backend snapshot ต้องมีไฟล์ source/test/configuration ครบและ content ตรงทุกไฟล์ก่อนปรับเฉพาะเอกสารสำหรับ cross-repository links
5. ใน component staging ปรับ README/คู่มือที่อ้าง Showcase-relative paths ให้เป็น cross-repository URLs ที่ชี้ source revision ชัดเจน และระบุ provenance ของ filtered history
6. ตรวจ component build/tests และ repository content; หาก baseline ไม่ผ่าน ให้รายงานผลก่อน pin revision โดยไม่แอบแก้ behavior/framework/packages ในงาน migration
7. สร้าง GitHub repository เมื่อยืนยัน M1–M8 แล้วเท่านั้น ไม่ overwrite remote ที่มีอยู่ ส่ง initial history และตรวจ default branch/full commit จาก GitHub/Git remote
8. เขียน manifest ด้วย remote-reachable verified SHA ที่เลือกเป็น baseline แล้วตรวจ manifest และ ignore rules
9. สร้าง backup parent ที่เป็นของ run นี้ใน `/private/tmp/` และย้าย legacy directory ทั้งชุดเข้า backup ด้วย no-clobber checks บันทึกตำแหน่งและ hashes โดยไม่ลบทิ้ง
10. สร้าง Checkout Directory ใหม่พร้อม `.gitkeep` แล้ว materialize เฉพาะ repo ที่ประกาศจาก GitHub ผ่านขั้นตอน bootstrap: staging, remote/revision checks, detached checkout และ no-clobber publication
11. เทียบ source ที่ materialize กับ exported source snapshot และ baseline commit ตรวจ independent `.git`, exact stored origin URL และ clean status ของ component
12. Update live path references และ project knowledge ให้ใช้ manifest แทน migration-pending; historical reports คง provenance ของสถานะในอดีต
13. Parent diff ต้องถอด tracked backend files เดิมออกและเพิ่ม manifest/ignore/knowledge/แผนงานเท่าที่จำเป็น โดยไม่ stage component content หรือ Git metadata
14. ตรวจทั้งสอง repository และเปิด Showcase migration PR ตาม authorization ที่ยืนยันไว้ ผู้ใช้เป็นผู้พิจารณา merge

หาก child delivery ไม่สำเร็จ ยังไม่ถอด source เดิมออกหรือบันทึก manifest revision หาก bootstrap หลัง backup ไม่สำเร็จ ต้องคง backup ไว้และรายงานตำแหน่ง ไม่ overwrite state เพื่อซ่อนความล้มเหลว

## 5. การตรวจและ completion criteria

| หลักฐาน | เกณฑ์ผ่าน |
| --- | --- |
| Source inventory | ระบุ source Showcase SHA และ tracked-file inventory; export ตรง snapshot |
| History | filtered history มีเฉพาะ backend tree; Showcase history ไม่ถูก rewrite |
| No content loss | source/tests/configuration ตรงก่อนและหลัง migration ยกเว้นเอกสารที่แก้ links โดยแสดง diff ได้ |
| Component verification | build และ tests ของ solution ผ่านด้วย framework/dependency เดิม |
| Child delivery | GitHub repository มี identity/visibility/default branch ที่ยืนยันและ SHA อยู่บน remote จริง |
| Manifest | safe YAML, required fields, full SHA, exact path/remote, required boolean และ ignore entries ถูกต้อง |
| Bootstrap | independent clone, exact origin, pinned detached HEAD, clean worktree และไม่มี ignored-file collision |
| Ownership | Showcase ไม่ track child source/metadata และไม่ใช้ submodule |
| Documentation | live references และ cross-repository links ชี้ถูก; ไม่มีการอ้างว่า known spec gaps ถูกแก้แล้ว |
| Existing state | handoffs ของงานอื่นและ backup original artifacts ถูกเก็บครบ |
| Delivery | parent PR มี scope เฉพาะ migration พร้อมผล verification จริง โดยไม่ merge |

Manifest pin นี้รับรอง reproducible legacy backend baseline ที่ผ่าน verification เท่านั้น ไม่ได้รับรองว่า backend ตรงกับ latest Authen API specs ทั้งหมด ช่องว่างที่บันทึกใน `code.md` ยังคงเป็นงานแยก

## 6. Approval และสิ่งที่ยังไม่อนุมัติ

ผู้ใช้อนุมัติ M1–M8 ผ่านคำถามที่ระบุแผนฉบับนี้โดยตรง ด้วยข้อความ: “อนุมัติตามแผน ใช้ repository แบบ Public” บันทึก approval เมื่อ `2026-11-07T14:00:23Z` (7 พฤศจิกายน 2026 เวลา 21:00:23 น. Asia/Bangkok)

ก่อนบันทึก approval ยังไม่มีการสร้าง GitHub repository, export/move legacy files หรือสร้าง nested `.git` การลงมือถัดจากนี้อยู่ใน scope ที่ระบุในหัวข้อ 2 โดยใช้ `ittikornsopawan/e-commerce-backend` แบบ PUBLIC และเก็บ filtered backend history

## 7. Baseline verification ก่อน migration

รอบ sandbox แรกติดข้อจำกัดการเขียน .NET first-run sentinel และ MSBuild IPC จึงย้าย CLI home ไป temporary storage และรันซ้ำโดยอนุญาต local IPC นอก sandbox:

```text
env DOTNET_CLI_HOME=/private/tmp/ecommerce-component-baseline DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 DOTNET_CLI_TELEMETRY_OPTOUT=1 dotnet test Ecommerce.sln --no-restore --disable-build-servers -m:1 --verbosity minimal
Passed! Failed: 0, Passed: 10, Skipped: 0, Total: 10 — Ecommerce.Application.Tests
Passed! Failed: 0, Passed: 30, Skipped: 0, Total: 30 — Ecommerce.Domain.Tests
```

ผลรวม 40 tests ผ่าน ไม่มี fail/skip เป็น baseline ของ source เดิม ไม่ใช่หลักฐานว่า implementation ตรง latest API specs ทุกข้อ

## 8. Migration verification

| หลักฐานที่ตรวจจริง | ผล |
| --- | --- |
| Source snapshot | `48c75ab59f27e915d0bff7acf4395eeaafca330a`; export 81/81 tracked files ตรงต้นฉบับแบบ byte-for-byte ก่อนแก้เอกสาร |
| Filtered history | สี่ backend-only commits; split tip `8a42bedc6455910e3b6434c3cefd8ec50b6aa159` |
| Component content changes | แก้เฉพาะ README, project-structure และ code guide ให้ใช้งานแยก repository; source/tests/build configuration คงเดิม |
| History safety scan | ตรวจสี่ commits และ 83 unique blobs ก่อน publication ไม่พบ secret-pattern หรือ tracked build output |
| Child delivery | `https://github.com/ittikornsopawan/e-commerce-backend` เป็น PUBLIC; default branch main; GitHub ยืนยัน SHA `d8255183cba54d0c2b218607456b895a70df32f0` ก่อนเขียน manifest |
| Manifest | safe YAML ที่ปฏิเสธ duplicate keys/aliases; exact remote/path/full SHA/required fields และ root ignores ผ่าน |
| Original backup | `/private/tmp/ecommerce-component-migration-ofejl0ty/legacy-checkout`; เทียบ inventory ทั้ง 591 file/directory entries หลัง atomic move ผ่าน รวม ignored artifacts |
| Bootstrap | clone จาก GitHub ผ่าน staging ไป path ที่ประกาศ; independent `.git`, exact origin, clean status และ detached HEAD ตรง manifest |
| Build จาก checkout จริง | full solution build ผ่าน 0 warnings, 0 errors |
| Tests จาก checkout จริง | Application 10/10 และ Domain 30/30 ผ่าน ไม่มี fail/skip |

Restore ใช้ package versions เดิมกับ cache ที่มีอยู่ และปิด NuGet audit เฉพาะ verification command ไม่มีการเปลี่ยน dependencies หรือ configuration ใน source ไม่ได้รัน database/API integration tests หรือ security audit; known specification gaps ยังคงเดิม

ระหว่าง export มี session อื่นสลับและอัปเดต primary checkout จึงตรวจ backend snapshot equality อีกครั้ง กลับ branch migration และรับ origin/main ล่าสุดก่อนย้ายจริง โดยรักษางานที่ merge ใหม่และคืนเฉพาะ task-plan section ของ migration ที่หายจาก working tree ไม่ได้ย้อน history ของ Showcase

Backup คงอยู่หลังส่งมอบ ไม่มีขั้นตอนลบทิ้งอัตโนมัติ การ cleanup เป็นงานที่ผู้ใช้เลือกภายหลัง
