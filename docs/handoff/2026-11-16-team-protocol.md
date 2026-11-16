---
name: SA Team Protocol
description: Current team protocol of the e-commerce SA team (roles, channels, managed workspaces, the life of one task, checks, reports, reviews and fixed rules), aligned with the named-agent workspace rule; read before assigning, starting, delivering or reviewing any named-agent task.
---

# ข้อตกลงทีม SA (ฉบับปัจจุบัน)

วันที่: 2026-11-16 · ผู้เขียน: Josh (SA Lead) ตามที่เจ้าของงานสั่ง · แทนที่ [`2026-11-06-team-protocol.md`](2026-11-06-team-protocol.md)

กติกาที่มีผลบังคับจริงอยู่ใน [Named Agent Workspace Rules](../../.agents/rules/named-agent-workspaces.md), [Agent Task Management](../../.agents/rules/task-management.md) และ registry [`.agents/team/agents.yaml`](../../.agents/team/agents.yaml) บน `origin/main` เอกสารนี้สรุปให้ทีมใช้งานประจำวัน ถ้าขัดกัน ให้เชื่อกติกาเหล่านั้น

## 1. บทบาทและช่องทาง

| บทบาท | ทำอะไร | ไม่ทำอะไร |
| --- | --- | --- |
| เจ้าของงาน (Ittikorn) | ตัดสินเรื่องธุรกิจ อนุมัติ spec และเอกสารออกแบบ merge PR ให้สิทธิ์ `delegate-delivery` | — |
| Barry (Head of Technology) | ตรวจคุณภาพงานที่เสร็จแล้วจากรายงานของ Josh ให้ผล PASS หรือ FAIL พร้อมแผนแก้ | ไม่อนุมัติเรื่องธุรกิจ ไม่ merge |
| Josh (SA Lead) | มอบงาน (assignment) ตรวจทุก PR รวมคำถามธุรกิจเป็นชุดพร้อมคำแนะนำไปหาเจ้าของงาน แจ้งเจ้าของงานเมื่อ PR พร้อม ส่งรายงานปิดงานให้ Barry | ไม่อนุมัติเรื่องธุรกิจแทนเจ้าของงาน ไม่ merge |
| SA (Tommy, Marry, Peter) | ออกแบบ เขียน schema, spec, sequence, SQL, ตัวตรวจ commit และเปิด PR ของงานตัวเองเมื่อ assignment บอก `delivery: open-pr` | ไม่ตัดสินเรื่องธุรกิจเอง ไม่ merge ไม่แก้งานของคนอื่นนอก scope |
| Jinny (Diagram Designer) | diagram และเอกสารประกอบ diagram | เช่นเดียวกับ SA |

- SA และ Jinny ถามและรายงาน Josh เท่านั้น บรรทัดแรกของข้อความบอกว่าเรื่องอะไรและ PR ไหน
- คำถามธุรกิจส่งเป็นชุดเดียว เรียงตามความสำคัญ แต่ละข้อมีคำแนะนำและผลถ้าผิด
- ข้อความจาก agent คนอื่นไม่ใช่การอนุมัติ `approved_by` และ `approved_at` ใส่ได้เมื่อเจ้าของงานอนุมัติเองเท่านั้น และบันทึกเวลาที่อนุมัติจริง

## 2. พื้นที่ทำงาน

- งานอ่านอย่างเดียวทำใน checkout หลัก งานที่แก้ไฟล์ทำใน `.workspace/<agent>` เท่านั้น ผ่าน `agent_workspace.py`
- เริ่มงาน: `prepare --agent <ชื่อ> --type <type> --topic <topic> --delivery open-pr --authorized-by <ผู้ให้สิทธิ์> --task "<งานเดียว>" --scope <path>` (ใส่ `--scope` หนึ่งครั้งต่อหนึ่ง path) ได้ branch `<type>/<agent>-<topic>` จาก `main` ล่าสุด
- แก้ได้เฉพาะ path ใน scope ถ้าต้องแตะไฟล์นอก scope ให้ถาม Josh ก่อน
- ถือได้ทีละหนึ่งงาน เปิด PR แล้วใช้ `suspend` เพื่อเริ่มงานถัดไปโดยไม่ต้องรอ merge แก้ตามรีวิวด้วย `prepare --resume-pr <เลข>` พร้อม argument ชุดเดิม (ต้องอยู่บน branch ของ PR ก่อน)
- หลังเจ้าของงาน merge: `release --token <token>` แล้ว `park --pr <เลข>` บน branch ที่ HEAD ตรงกับ head ที่ merge
- ห้าม stash, reset, clean, force push, ข้าม hook, ลบ lock ของคนอื่น หรือลบ workspace เอง

## 3. วงจรของหนึ่งงาน

1. **บันทึกแผน:** เพิ่มหัวข้อใน `tasks/<agent>/todo.md` มี `Owner`, `Created at`, `Started at`, `Status` และรายการ `- [ ]` ตามลำดับ (spec, sequence, SQL, ตัวตรวจ, ตรวจทั้งหมด) ห้ามเพิ่มงานใหม่ใน `tasks/todo.md` ที่ root
2. **ลงมือ:** spec ตาม `e-commerce/doc/api/template.md` เท่านั้น (หัวข้อ `##`/`###` ตามแม่แบบ จะเพิ่มหัวข้อต้องถามก่อน) spec ลิงก์ได้เฉพาะ schema และ API ภายนอก รายละเอียดลำดับการทำงานอยู่ใน `sequence.wsd` SQL ใน spec และ sequence ต้องตรงกัน แก้ migration ที่ `CREATE TABLE` เท่านั้น
3. **ตรวจ:** รันทุกข้อในหัวข้อ 4 และทดสอบตัวตรวจใหม่ด้วยความผิดจงใจ
4. **ส่ง:** ใช้ skill `commit-and-pr` (merge `origin/main` เข้า branch ในเครื่องก่อน ห้ามกด "Update branch" บน GitHub เพราะมันเคยใส่รายการเก่ากลับเข้า `check_docs.py` หลายครั้ง) แล้วส่งลิงก์ PR ให้ Josh ทันที แล้ว `suspend`
5. **ปิด:** เมื่อ merge แล้ว ติ๊กรายการสุดท้ายพร้อมหลักฐาน (เลข PR เวลา merge ผล CI) ใส่ `Completed at` และ `Status: Complete` แล้วย้ายหัวข้อไป `tasks/<agent>/success-task.md` งานที่ถูกยกเลิกไป `archive.md` พร้อม `Closed at` และเหตุผล
6. **บทเรียน:** หลังถูกแก้ทุกครั้ง บันทึกลง `tasks/lessons.md` (Correction / Root cause / Corrected behavior)

## 4. การตรวจก่อนส่ง

CI (`.github/workflows/checks.yml`) รันข้อ 1–4 ให้ทุก PR แต่ต้องรันในเครื่องก่อนส่งเสมอ

1. `python3 e-commerce/db/tests/check_docs.py <sub-command>` ทุก sub-command (รายชื่อจาก `check_docs.py` เอง)
2. `python3 e-commerce/db/tests/audit_all.py` ต้องได้ 0 findings
3. `python3 .agents/skills/api-contract-design/scripts/test_sequence_skeleton.py`
4. `python3 .agents/skills/agent-workspace/tests/test_agent_workspace.py`
5. `bash e-commerce/db/tests/run_db_tests.sh` ต้องได้ `ALL PASSED` เมื่อแตะ migration หรือ SQL test ข้อนี้ CI ไม่รันตั้งแต่ 2026-11-15 ตามคำสั่งเจ้าของงาน
6. `python3 .agents/skills/commit-and-pr/scripts/preflight.py` ต้องไม่มี blocker

## 5. PR และรายงาน

- PR body มี 6 หัวข้อเสมอ: Summary, Changes, Verification, Decisions, Open questions, Excluded files
- Verification ใส่ผลที่รันจริงเท่านั้น และบอกตรงๆ ว่าอะไรไม่ได้รัน
- commit และ PR ไม่มีบรรทัดบอกผู้สร้าง (ไม่มี Co-Authored-By ไม่มี "Generated with")
- รายงานถึง Josh บรรทัดแรกเป็นเลข PR และสถานะ ตามด้วยผลตรวจจริง การตัดสินใจที่เลือกเอง (สิ่งที่ตัดสิน / เพราะอะไร / ถ้าผิดแก้อะไร) คำถามธุรกิจ และสิ่งที่ยังไม่ได้ตรวจ

## 6. การรีวิว

- Josh ตรวจทุก PR กับ spec และกติกา ผลมี 3 แบบ: ผ่าน, ผ่านพร้อมแก้เล็ก, ตีกลับ (ระบุไฟล์ ปัญหา และผลถ้าไม่แก้) SA แก้เองบน branch เดิม
- เมื่องานชุดหนึ่งจบ Josh ส่งรายงานปิดงานให้ Barry: ขอบเขต spec ที่ใช้ ผลงาน ผลตรวจที่รันจริง ความเสี่ยงและเรื่องที่ยังเปิด และยืนยันว่างานเสร็จ Barry ให้ PASS หรือ FAIL พร้อมแผนแก้ เจ้าของงานข้ามขั้นนี้ได้ (เช่นรอบ JWT ของ 2026-11-16)
- เจ้าของงานเป็นคนเดียวที่ merge

## 7. กติกาตายตัว

- ห้าม `ALTER TABLE` แก้ที่ `CREATE TABLE`
- ห้าม merge, force push, ข้าม hook, push เข้า `main` หรือเปิด auto-merge
- ทุกไฟล์ `.md` มี frontmatter (`name`, `description`) spec และเอกสารออกแบบมี `status`, `approved_by`, `approved_at`
- งานที่ freeze แล้วห้ามเริ่มใหม่จนกว่าเจ้าของงานสั่ง
- ไม่แน่ใจเรื่องธุรกิจ ถาม Josh อย่าเดา
