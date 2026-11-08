---
name: Database-grounded domain model verification
description: ผลตรวจdomain modelทั้ง4ภาพกับSQLและschema docs พร้อมcoverage ภาพจริงและeditability อ่านก่อนรับงานหรือสร้างภาพซ้ำ
---

# Domain model verification — 2026-11-08

[สารบัญ](README.md) · [ภาพรวมและเหตุผล](domain-model.md) · [source inventory](domain-source-inventory.json)

## แหล่งข้อมูลและขอบเขต

อ่านmigrationทั้ง10ไฟล์และschema docsของ53ตาราง พร้อมschema index เป็น64source files มี11schemasและ75FK columns การแบ่งdetail pagesเป็น21/19/13ตารางไม่ซ้ำกัน ชื่อธุรกิจและกรอบการอ่านเป็นinterpretationที่รอreview ไม่ใช่การพิสูจน์DDDaggregate, service boundary หรือclass implementationจากSQL

## ผลตรวจที่รันจริง

```text
python3 -B e-commerce/db/tests/audit_all.py
53 tables audited, 0 findings

python3 -B e-commerce/diagram/domain/generate_domain_diagrams.py --check
PASS domain source coverage: 53/53 tables; 75/75 FK columns; schema documentation comparison 0 findings
```

- Source inventoryเทียบcolumn, type/nullability/reference, constraints, indexesและfile hashes ผ่าน ไม่มีการแก้DBเพื่อให้ภาพตรง
- Entity coverageครบ53ตาราง กล่องdetailทุกentityเป็นnative childของschema frame; nativeIDsไม่ซ้ำ parentอ้างถึงcellที่มีอยู่
- Detail associations35เส้นมีFKหลักฐานและall-row cardinalityตรงsource เพิ่มoverview references7เส้นซึ่งเชื่อมกลุ่มconceptจึงไม่ใส่entity multiplicity
- ExtractจากFKcatalogueที่เผยแพร่ในMarkdownแล้วเทียบSQLโดยตรง:75/75referencesและparent cardinalitiesตรงกัน ครบ7nullable FK; partialuniqueไม่ถูกแปลเป็นunconditional1:1
- Geometry/text capacity/containment/ports/orthogonal routes/cardinality masksผ่าน ไม่มีเส้นทับกันหรือผ่านentityที่ไม่ใช่ปลายทาง
- Packaged `self_check.py`ผ่าน4/4HTML และ `export_svg.py`ส่งออก4/4ภาพไปtemporary QA directory
- Browserที่390×844: localSVG scroller1584px ไม่มีwhole-page overflowหรือข้อความในentity/container/cardinalityล้นกรอบ หลังแก้ชื่อยอดเงินในOrderตรวจbrowserซ้ำไม่พบoverflow
- ดูnativePNGจริงครบ4ภาพ ภาพoverviewหลังเพิ่มcross-schema referencesตรวจซ้ำแล้ว Nativefontfallbacksเป็นGeorgia/Arial/CourierNewตามREADME ไม่ติดตั้งfontsหรือdependencies
- PNGทุกไฟล์2378×1682 ต่ำกว่า1MiB CRCถูกต้อง NativeembeddedsourceและpackagedextractorIRตรง`.drawio`
- เปิดPNGกลับในdraw.ioแล้วexportใหม่ครบ4ภาพ: IDATตรงทุกbyteและembeddedXMLตรงsourceทุกภาพ
- Hashของภาพ/source/HTML45ไฟล์จากชุดเดิม15viewsไม่เปลี่ยน และoldrenderer source checkยังผ่าน

| ภาพ | Concept boxes | Selected lines | PNG bytes |
| --- | ---: | ---: | ---: |
| `domain-model` | 11 | 7 | 512,077 |
| `domain-identity-model` | 21 | 12 | 432,439 |
| `domain-merchandising-model` | 19 | 12 | 403,835 |
| `domain-commerce-model` | 13 | 11 | 516,697 |

## ผลทบทวนและข้อจำกัด

Focused evidence reviewยืนยันcounts, nullableFK, partialunique, shipment split, order snapshotและFK consistency gaps การทบทวนรอบถัดมาพบชื่อยอดเงินย่อที่ดูเหมือนcolumnจริงและคำว่าimmutableที่DDLไม่ได้รับรอง แก้เป็นtotal_discount/total_taxและstored snapshotsแล้ว Follow-up reviewอิสระหยุดเพราะusage limitก่อนออกผลสุดท้าย จึงไม่อ้างว่าผ่านการรับรองอิสระครบทั้งชุด Primaryagentตรวจภาพครบและรันsource/Markdown/cardinality parityทั้งหมดข้างต้น

ไม่ได้รันbackend build, SQL mutation/concurrency tests, live DB queries, provider callsหรือload/restore tests เพราะงานนี้สร้างconceptual diagramsจากDDLและเอกสาร ไม่มีschema/API/backend implementation Taxformula, rounding, aggregate boundariesและsharedDomainservice contractsยังต้องใช้approvedspecก่อนimplementation

งานอยู่บนbranch`docs/jinny-domain-model` ในmanagedJinnyclone ขอบเขต`e-commerce/diagram`และtask recordsเท่านั้น PR61เดิมmergeและparkแล้วก่อนเริ่มงานนี้ ช่วงสร้างภาพยังไม่มีcommit/push/PR; ต่อมาเจ้าของงานสั่งแยกfolderและส่งPRสำหรับpackageนี้ Previewserver/tab/viewportoverrideปิดเมื่อจบQA และediting-sessionlockปล่อยเมื่อhandoff

Source baseline commit: `7007015ba770973daab0460f850b01bb789a4989`; inventory157320bytes, SHA-256ของsourceทั้ง64ไฟล์ใช้ตรวจdriftในครั้งถัดไป

Final packaging checks:7 authored/modifiedMarkdown frontmattersผ่าน,311local linksมีปลายทางจริง,23changedpathsอยู่ในassignment scopeและwhitespace checksผ่าน ไม่มีcache/build artifacts

## Folder separation and PR delivery

เจ้าของงานสั่งแยกfolderและเปิดPR จึงย้ายทั้ง21ไฟล์ของpackageเดิมไป `e-commerce/diagram/domain/` และเพิ่มREADMEเฉพาะfolder แก้relative links, generator import/root pathsและคำสั่งสร้างซ้ำ SharedPNGfinalizerรับoutput directoryได้ โดยdefaultของชุดเดิมยังใช้pathเดิม

ตรวจหลังย้าย: PNGทั้ง4, draw.io sourceทั้ง4และSQLinventoryมีSHA-256ตรงกับก่อนย้ายทุกbyte ภาพที่ตรวจไว้จึงไม่เปลี่ยน Package generator/sourcecheck, finalizerจากfolderใหม่, HTML/SVG4ภาพ, PNGextraction/IRและsavednative roundtripsผ่าน FKcatalogueยังตรง75/75รายการ ภาพ/source/HTML45ไฟล์จากชุดเดิม15viewsไม่เปลี่ยน

Packagingล่าสุด:8Markdown frontmattersและ328local linksผ่าน รวม25pathsในassignment scope Preflightยืนยันdirectowner delivery grantและไม่พบblocker StaticDBaudit:53tables audited,0findings ไม่มีbackend/API/schema filesเปลี่ยน การส่งงานใช้สถานะGit/GitHub; directPRgrantไม่เพิ่มสิทธิ์mergeหรืออนุมัติimplementation
