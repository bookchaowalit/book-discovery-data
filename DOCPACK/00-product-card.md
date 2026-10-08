---
title: Book Discovery Data — Product Card
doc_id: CARD-book-discovery-data
doc_type: product-card
verdict: showcase
version: 0.1
date: 2026-10-08
status: ร่างเพื่อพิจารณา
owner: Product owner (Book Dev)
---

# Book Discovery Data — Product Card

## 1. สรุปคุณค่าในหนึ่งประโยค

นำ capture สาธารณะ 4 ตระกูลจาก `book-job-scraping` เข้า Bronze `discovery.v1` (technology signals) พร้อม lineage และให้ API อ่านอย่างเดียว

## 2. ปัญหาและผู้ใช้เป้าหมาย

- ปัญหา: ต้องการติดตามสัญญาณเทคโนโลยี (จากแหล่งเช่นที่ job scraper เก็บ) แบบตรวจย้อนได้
- ผู้ใช้: operator/agent ภายใน; ผู้ใช้ภายนอก **[ต้องยืนยัน]**

## 3. สิ่งที่ทำได้จริงตอนนี้

- `discovery_data.api` (:8110) อ่านเฉพาะ `technology_signals` และ history; ตอบ 503 แบบไม่รั่ว path เมื่อ lake ไม่พร้อม
- `POST /v1/refresh` ปิดโดยค่าเริ่มต้น และเมื่อเปิดจะ acknowledge เท่านั้น (`job_started: false`)
- `scripts/ingest.sh` / `task scraping:discovery:ingest` สำหรับ replay; config ตรวจค่าเข้มงวด
- README ระบุว่า repo ถูกสร้างใหม่จาก scaffold เพราะ checkout เดิมหายไป

## 4. หลักฐานสถานะ

| รายการ | ค่า (ตรวจจาก repository) |
|---|---|
| Stack | Python |
| Commits | 12 (แรก 2026-09-17 → ล่าสุด 2026-10-01) |
| Source | 9 ไฟล์ / 1,249 บรรทัด |
| Tests | 5 ไฟล์ |
| CI | 1 workflow |
| Deploy config | ไม่มี |
| Live URL | ไม่มี |
| README | 94 บรรทัด (`book-discovery-data`) |
| โครงสร้างซ้ำ (template family) | 1 repo ที่มี structure signature เดียวกัน |

## 5. คุณค่าและจุดต่าง

- เป็นตัวอย่าง read-only data API ที่ปลอดภัย (loopback, CORS จำกัด, constant-time token)
- คุณค่าทางธุรกิจยังไม่ชัด — ไม่มี consumer ที่ระบุ

## 6. ช่องว่างสำคัญ

- ต้องพึ่ง capture ของ `book-job-scraping` ซึ่งเป็น job-focused
- ไม่มีผู้ใช้หรือคำถามธุรกิจที่ข้อมูลนี้ตอบ **[ต้องยืนยัน]**
- ชื่อ "discovery" ชนกับกลุ่ม discovery portfolio (grant/benefit ฯลฯ) ทำให้สับสน

## 7. คำตัดสิน

**`showcase`** — เป็นหลักฐานงาน data API ที่ดี แต่ยังไม่มีเหตุผลเชิงผลิตภัณฑ์ จะเป็น `invest` เมื่อมี consumer ที่ใช้สัญญาณเทคโนโลยีตัดสินใจจริง (เช่น เลือก skill ที่จะเรียน) ถ้าไม่มีภายใน 2026-Q4 ให้พิจารณา `archive`

## 8. ขั้นต่อไป

1. ระบุ consumer และคำถามที่ข้อมูลนี้ตอบ
2. พิจารณาเปลี่ยนชื่อเพื่อไม่ชนกับ discovery portfolio

## การอนุมัติ

| บทบาท | สถานะ | วันที่ | ลงนาม |
|---|---|---|---|
| Product owner (Book Dev) | รอพิจารณา | — | ________ |

## แหล่งข้อมูล

- `README.md`
- `src/discovery_data/api.py`
- `src/discovery_data/store.py`
- `scripts/ingest.sh`
