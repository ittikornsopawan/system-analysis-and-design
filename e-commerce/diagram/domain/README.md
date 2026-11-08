---
name: E-commerce Domain Diagram Package
description: สารบัญdomain modelจากฐานข้อมูล53ตาราง พร้อมภาพ คำอธิบาย source inventoryและวิธีสร้างซ้ำ อ่านเมื่อreviewหรือแก้ชุดDomain diagrams
---

# Domain diagrams

[กลับสารบัญ diagram ทั้งหมด](../README.md)

ชุดนี้แยกไว้ใน `e-commerce/diagram/domain/` ครบทั้งภาพ คำอธิบาย source generator และSQL inventory อ้างอิง **53ตาราง /11schemas /75FK** จาก [migrations](../../db/migrations/up/) และ [schema docs](../../doc/schema/README.md)

| ภาพแก้ไขได้ | คำอธิบาย | ขอบเขต |
| --- | --- | --- |
| [domain-model.drawio.png](domain-model.drawio.png) | [domain-model.md](domain-model.md) | ภาพรวม11กลุ่มแนวคิดและ7cross-schema references |
| [domain-identity-model.drawio.png](domain-identity-model.drawio.png) | [domain-identity-model.md](domain-identity-model.md) | Identity / Access / Consent / Key material:21ตาราง,23FK |
| [domain-merchandising-model.drawio.png](domain-merchandising-model.drawio.png) | [domain-merchandising-model.md](domain-merchandising-model.md) | Catalog / Shop / Stock:19ตาราง,25FK |
| [domain-commerce-model.drawio.png](domain-commerce-model.drawio.png) | [domain-commerce-model.md](domain-commerce-model.md) | Cart / Order / Payment / Shipping / Campaign:13ตาราง,27FK |

ทุกภาพมี `.drawio`, `.drawio.png`, `.html` และ `.md` ชื่อเดียวกัน ภาพรายละเอียดเลือก35associationsเพื่ออ่านได้ชัด ส่วนFKcatalogueในMarkdownเก็บครบ75รายการ Cardinalityเป็นข้อมูลทุกแถวในประวัติ จึงแยกpartialunique/live subsetจากunconditional1:1 กรอบschema/การอ่านไม่ใช่การประกาศDDDaggregateหรือmicroservice

## Source และการตรวจ

- [domain_model_content.py](domain_model_content.py): business names, selected attributes, native hierarchyและassociations
- [domain_model_notes.py](domain_model_notes.py): เหตุผลและข้อจำกัดที่ประกอบแต่ละภาพ
- [domain-source-inventory.json](domain-source-inventory.json): SQL/schema baselineและhashของ64source files
- [generate_domain_diagrams.py](generate_domain_diagrams.py): สร้างภาพ/คำอธิบายและตรวจcoverageกับsource
- [domain-model-verification.md](domain-model-verification.md): ผลตรวจภาพจริง, browser, extractionและnative round trips

ใช้คำสั่งต่อไปนี้จากrepository root Generatorใช้ shared rendering helpers ใน `../scripts/` โดยเก็บ model, inventory และ output ของชุดนี้ไว้ใน `domain/`

```sh
python3 -B e-commerce/diagram/domain/generate_domain_diagrams.py
python3 -B e-commerce/diagram/domain/generate_domain_diagrams.py --check
```

หากDBหรือmappingเปลี่ยน ให้reviewmodelก่อนใช้ `--refresh-inventory` แล้วสร้างภาพและตรวจใหม่ ส่งออกPNGด้วยdraw.io Desktopที่ติดตั้งไว้ ตัวอย่างภาพรวม (ทำเช่นเดียวกันกับอีกสามslug):

```sh
/Applications/draw.io.app/Contents/MacOS/draw.io \
  -x -f png --embed-diagram --size page -s 1.5 --theme light \
  --disable-update --timeout 45 \
  -o e-commerce/diagram/domain/domain-model.drawio.png \
  e-commerce/diagram/domain/domain-model.drawio

python3 -B e-commerce/diagram/domain/generate_domain_diagrams.py --finalize-pngs
```

A3landscape1584×1120และstyleอ่อน/แต้มส้มตามชุดเดิม NativePNG2378×1682ใช้Georgia/Arial/CourierNewfallbacksและcompressed editablemetadata; HTMLใช้webfontstacksเดิม ไม่ติดตั้งdependencies/fontsเพิ่ม ไม่มีbackend/API/schema implementationในpackageนี้ Business namingและrule candidatesยังรอreviewตามSDDก่อนimplementation
