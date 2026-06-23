# คู่มือการพัฒนาโปรแกรม SDK: Face & eKYC Domain (หมวด C-1 ถึง C-6)
**iApp Technology Co., Ltd.** · 16 มิถุนายน 2569  
*อ้างอิงเอกสารการตรวจสอบระบบและความก้าวหน้าของ SDK ล่าสุด*

---

## 📌 บทนำและภาพรวมการอัปเกรด (C-1 ถึง C-6)
เอกสารนี้จัดทำขึ้นเพื่อใช้เป็นคู่มือสำหรับนักพัฒนาในการใช้งาน Python SDK (`iapp-ai`) เฉพาะในกลุ่ม **Face & eKYC Domain** จำนวน 19 เมธอด ซึ่งได้รับการอัปเกรดประสิทธิภาพและความเสถียรภายใต้รหัสแผนงาน **C-1 ถึง C-6** ดังนี้:
* **C-1 (Liveness Fix)**: แก้ไขบั๊กตัวแปร `taskGuid` ใน `face_liveness` ให้สามารถดึง ID จริงไปตรวจสอบสถานะต่อได้โดยไม่เกิดข้อผิดพลาด
* **C-2 (Score Configuration Refactoring)**: ยุบและจัดกลุ่ม Logic การปรับตั้งค่าคะแนนความคล้ายคลึง โดยเรียกใช้ฟังก์ชันกลางเพื่อความสม่ำเสมอในการเชื่อมต่อ
* **C-3 (Resource Leak Prevention)**: บังคับใช้ Context Manager ปิดไฟล์ภาพอัตโนมัติ ป้องกันปัญหา Memory/File Leak
* **C-4 (Dynamic Output Path)**: เมธอดลบพื้นหลังภาพรองรับการตั้งชื่อและตำแหน่งบันทึกไฟล์ปลายทางแบบยืดหยุ่นผ่าน `output_path`
* **C-5 (Type Hints & Mutable Defaults)**: ป้องกันปัญหาการเก็บข้อมูลซ้ำใน Signature ฟังก์ชัน โดยใช้ `None` เป็นค่าเริ่มต้น และใส่ระบบระบุชนิดข้อมูลอย่างครบถ้วน
* **C-6 (Offline Mock Tests)**: เพิ่ม Coverage การทดสอบมากกว่า 80% เพื่อยืนยันพฤติกรรมการทำงาน

---

## 📊 ตารางสรุป 19 เมธอดกลุ่ม Face & eKYC (Quick Reference)

| ลำดับ | ชื่อเมธอด (Method Name) | คำอธิบายสั้น ๆ | Endpoint ปลายทาง |
| :---: | :--- | :--- | :--- |
| 1 | `face_liveness` | ตรวจสอบภาพใบหน้าว่าเป็นคนจริงหรือภาพลอกเลียน (Spoof) | `POST /v3/store/ekyc/face-passive-liveness` |
| 2 | `info_face_liveness` | ดึงผลการตรวจสอบ Liveness แบบ Asynchronous ด้วย Task GUID | `GET /v3/store/ekyc/face-passive-liveness/{taskGuid}` |
| 3 | `face_verification` | เปรียบเทียบใบหน้า 2 ภาพ (1:1 Verification) ด้วยเงื่อนไขเฉพาะ | `POST /v3/store/ekyc/face-verification` |
| 4 | `face_ver2` | เปรียบเทียบใบหน้า 2 ภาพ (1:1 Verification v2) | `POST /v3/store/ekyc/face-verification` |
| 5 | `face_detect_single` | ตรวจจับใบหน้าเดี่ยวและตัดภาพส่วนใบหน้าออกมา | `POST /v3/store/ekyc/face-detection/single` |
| 6 | `face_detect_multi` | ตรวจจับใบหน้าหลายคนในหนึ่งภาพ | `POST /v3/store/ekyc/face-detection/multi` |
| 7 | `face_recog_add` | ลงทะเบียนใบหน้าเข้าสู่ฐานข้อมูลใบหน้าของบริษัท | `POST /v3/store/ekyc/face-recognition/add` |
| 8 | `face_recog_remove` | ลบข้อมูลใบหน้าจากฐานข้อมูลใบหน้าของบริษัท | `POST /v3/store/ekyc/face-recognition/remove` |
| 9 | `face_recog_check` | ตรวจสอบสถิติจำนวนใบหน้าที่บันทึกไว้ในฐานข้อมูล | `POST /v3/store/ekyc/face-recognition/check` |
| 10 | `face_recog_export` | ส่งออกข้อมูล Feature Vectors ของใบหน้าทั้งหมดเป็น CSV | `POST /v3/store/ekyc/face-recognition/export` |
| 11 | `face_recog_import` | นำเข้าข้อมูลใบหน้าจำนวนมากผ่านไฟล์ CSV | `POST /v3/store/ekyc/face-recognition/import` |
| 12 | `face_recog_single` | ค้นหาและระบุตัวตนใบหน้าเดี่ยวเปรียบเทียบกับฐานข้อมูล (1:N) | `POST /v3/store/ekyc/face-recognition/single` |
| 13 | `face_recog_multi` | ค้นหาและระบุตัวตนใบหน้ากลุ่มเปรียบเทียบกับฐานข้อมูล | `POST /v3/store/ekyc/face-recognition/multi` |
| 14 | `face_recog_facecrop` | ครอบภาพและค้นหาใบหน้ากับฐานข้อมูลแบบรวดเร็ว | `POST /v3/store/ekyc/face-recognition/facecrop` |
| 15 | `face_ver_config_score` | ตั้งค่าคะแนนขั้นต่ำ (Threshold) สำหรับการเปรียบเทียบใบหน้า | `POST /face_config_score` |
| 16 | `face_detect_config_score` | ตั้งค่าคะแนนขั้นต่ำ (Threshold) สำหรับการตรวจจับใบหน้า | `POST /face_config_score` |
| 17 | `face_recog_config_score` | ตั้งค่าคะแนนขั้นต่ำ (Threshold) สำหรับการระบุตัวตนใบหน้า | `POST /face_config_score` |
| 18 | `img_bg_removal_file` | ลบภาพพื้นหลังของรูปใบหน้าหรือสิ่งของ (Background Removal) | `POST /v3/store/smart-city/remove-background` |
| 19 | `face_id_card_verification` | ตรวจสอบเปรียบเทียบรูป Selfie กับรูปบนบัตรประชาชน (eKYC) | `POST /v3/store/ekyc/face-and-id-card-verification` |

---

## 🛠️ โครงสร้างการเริ่มต้นใช้งานทั่วไป

```python
from iapp_ai import api

# กำหนด API Key ที่ได้จาก iApp Marketplace
client = api("YOUR_API_KEY")
```

---

## 📖 คู่มือเจาะลึก 19 เมธอด (C1 - C6)

### 1. `face_liveness`
ใช้สำหรับตรวจสอบรูปภาพใบหน้าว่าเป็นบุคคลจริงที่อยู่หน้ากล้อง (Real Live Person) หรือรูปภาพลอกเลียนแบบ เช่น ภาพถ่ายบนกระดาษ/หน้าจอมือถือ (Spoof)
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-passive-liveness`
* **การยืนยันตัวตน**: ส่ง API Key ผ่าน HTTP header: `apikey: <YOUR_API_KEY>`
* **ค่าใช้จ่าย**: 1 IC ต่อการเรียกใช้งาน

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `file_path` | `str` | ใช่ | — | พาธของไฟล์รูปภาพใบหน้า (แนะนำขนาดไม่เกิน 10MB รูปแบบ JPG/PNG) |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers เพิ่มเติมที่ต้องการส่งพ่วง |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | พารามิเตอร์ฟอร์มข้อมูล (form-data) เพิ่มเติม |
| `files` | `List[Any]` | ไม่ | `None` | อาร์เรย์ของไฟล์เพิ่มเติมที่ต้องการอัปโหลด |

#### ผลลัพธ์กลับคืน (JSON Response Body)
ส่งคืนค่าสถานะและผลคะแนนการวิเคราะห์ใบหน้า โดยระบบจะบันทึกรหัสของภารกิจตรวจสอบเข้าตัวแปรส่วนกลาง `iapp_ai.module_api.taskGuid` สำหรับใช้ทำ Polling ต่อกรณีที่ฝั่งเซิร์ฟเวอร์รันแบบ Asynchronous
* **ตัวอย่างผลลัพธ์ (HTTP 200)**:
  ```json
  {
    "filename": "selfie.jpg",
    "predict": "SPOOF",
    "score": 0.6110675235589345,
    "darkness": 0,
    "data": {
      "SPOOF": 0.7199686169624329,
      "REAL": 0.28003135323524475
    },
    "normalized": {
      "SPOOF": 0.6110675235589345,
      "REAL": 0.3889324764410655
    },
    "taskGuid": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
  }
  ```

#### ตัวอย่างการใช้งาน
```python
from iapp_ai import api
import iapp_ai.module_api as module_api

client = api("YOUR_API_KEY")
response = client.face_liveness("img/selfie.jpg")
print("Prediction:", response.json().get("predict"))
print("Current Task GUID:", module_api.taskGuid)
```

> [!NOTE]
> **การแก้ไขในแผน C-1:** ก่อนหน้านี้มีบั๊กเก็บ HTTP Response ทั้งก้อนลงใน `taskGuid` ทำให้ไม่สามารถนำไอดีนี้ไปเรียกตรวจสอบต่อได้ ในรุ่นปัจจุบันได้รับการแก้ไขให้ดึงเฉพาะค่า String ของคีย์ `"taskGuid"` เรียบร้อยแล้ว

---

### 2. `info_face_liveness`
ดึงผลการตรวจสอบ Liveness แบบ Asynchronous โดยใช้รหัสอ้างอิง `taskGuid` จากขั้นตอนแรก
* **หมวดหมู่**: eKYC
* **Endpoint**: `GET /v3/store/ekyc/face-passive-liveness/{taskGuid}`
* **ค่าใช้จ่าย**: ฟรี (ไม่หักเครดิตสำหรับการดึงข้อมูลผลลัพธ์)

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `taskGuid` | `str` | ใช่ | `""` | รหัสภารกิจที่ได้จากการเรียกใช้ `face_liveness` |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers เพิ่มเติม |
| `url` | `List[Any]` | ไม่ | `None` | ตัวแปรแบบเก่า (Legacy) ที่ไม่ใช้งานแล้ว |

#### ตัวอย่างผลลัพธ์ (HTTP 200)
```json
{
  "status": "completed",
  "result": {
    "predict": "REAL",
    "score": 0.985
  }
}
```

#### ตัวอย่างการใช้งาน
```python
response = client.info_face_liveness(taskGuid="f81d4fae-7dec-11d0-a765-00a0c91e6bf6")
if response.status_code == 200:
    print(response.json())
```

---

### 3. `face_verification`
เปรียบเทียบรูปภาพใบหน้า 2 รูปแบบแบบ 1:1 เพื่อดูว่าเป็นบุคคลคนเดียวกันหรือไม่
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-verification`
* **ค่าใช้จ่าย**: 1 IC ต่อการเรียกใช้งาน

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `file_path1` | `str` | ใช่ | — | พาธของรูปใบหน้าที่ 1 |
| `file_path2` | `str` | ใช่ | — | พาธของรูปใบหน้าที่ 2 |
| `company_name` | `str` | ใช่ | — | ชื่อบริษัท/โดเมนจำลอง เพื่อระบุสิทธิ์ใช้งาน |
| `min_score` | `float` | ใช่ | — | คะแนนขั้นต่ำสุดในการยืนยันตัวตน (ช่วง 0-100) |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers เพิ่มเติม |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | พารามิเตอร์ฟอร์มเพิ่มเติม |
| `files` | `List[Any]` | ไม่ | `None` | อาร์เรย์ของไฟล์เพิ่มเติม |

#### ตัวอย่างผลลัพธ์ (HTTP 200)
```json
{
  "duration": 0.171,
  "matched": false,
  "message": "file2: face size is too small.",
  "score": 0.0,
  "threshold": 80,
  "api_status_code": "E424",
  "status_code": 200
}
```

#### ตัวอย่างการใช้งาน
```python
response = client.face_verification(
    file_path1="img/avatar_id.jpg",
    file_path2="img/selfie_real.jpg",
    company_name="my_company",
    min_score=80.0
)
print("Matched:", response.json().get("matched"))
```

> [!IMPORTANT]
> **การแก้ไขในแผน C-3:** ฟังก์ชันนี้จัดการเปิดไฟล์พร้อมกัน 2 รูปภาพเดิมเสี่ยงต่อปัญหารั่วไหลของหน่วยความจำ ปัจจุบันได้รับการหุ้มด้วยระบบปิดอัตโนมัติสมบูรณ์แล้ว

---

### 4. `face_ver2`
เปรียบเทียบรูปภาพใบหน้า 2 รูปแบบ v2 เพื่อความรวดเร็วและใช้ความกว้างขวางของ AI โมเดลใหม่ โดยลดการส่งค่าพารามิเตอร์ทางพาธภายนอก
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-verification`
* **ค่าใช้จ่าย**: 1 IC ต่อการเรียกใช้งาน

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `file_path1` | `str` | ใช่ | — | พาธของรูปใบหน้าที่ 1 |
| `file_path2` | `str` | ใช่ | — | พาธของรูปใบหน้าที่ 2 |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers เพิ่มเติม |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | พารามิเตอร์ส่งเสริมอื่น ๆ เช่นการทดสอบ threshold |
| `files` | `List[Any]` | ไม่ | `None` | ไฟล์เพิ่มเติม |

#### ตัวอย่างการใช้งาน
```python
response = client.face_ver2("img/face1.jpg", "img/face2.jpg")
print(response.json())
```

---

### 5. `face_detect_single`
ตรวจจับใบหน้าเดี่ยวในรูปภาพ คืนค่ากรอบครอบใบหน้า (Bounding Box) และอัตราความเชื่อมั่น
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-detection/single`
* **ค่าใช้จ่าย**: 0.2 IC ต่อการเรียกใช้งาน

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `file_path` | `str` | ใช่ | — | พาธของรูปใบหน้าที่ต้องการส่งตรวจ |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | ข้อมูล payload เสริม |
| `files` | `List[Any]` | ไม่ | `None` | ไฟล์เพิ่มเติม |

#### ตัวอย่างผลลัพธ์ (HTTP 200)
```json
{
  "bbox": {
    "xmax": 1185.966064453125,
    "xmin": 822.673583984375,
    "ymax": 682.4447631835938,
    "ymin": 187.18467712402344
  },
  "detection_score": 0.9998989105224609,
  "face": "data:image/png;base64,iVBORw0KG..."
}
```

#### ตัวอย่างการใช้งาน
```python
response = client.face_detect_single("img/photo.jpg")
print("Confidence score:", response.json().get("detection_score"))
```

---

### 6. `face_detect_multi`
ตรวจจับและระบุพิกัดใบหน้าหลายรายบุคคลพร้อมกันภายในรูปภาพภาพเดียว
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-detection/multi`
* **ค่าใช้จ่าย**: 0.5 IC ต่อการเรียกใช้งาน

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `file_path` | `str` | ใช่ | — | พาธของรูปภาพเป้าหมาย |
| `company_name` | `str` | ใช่ | — | โดเมน/โดเมนจำลองของบริษัท |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | พารามิเตอร์ฟอร์มเสริม |
| `files` | `List[Any]` | ไม่ | `None` | ไฟล์เพิ่มเติม |

#### ตัวอย่างผลลัพธ์ (HTTP 200)
```json
{
  "message": "successfully performed",
  "process_time": 0.757,
  "result": [
    {
      "bbox": {"xmax": 1185, "xmin": 822, "ymax": 682, "ymin": 187},
      "detection_score": 0.999
    }
  ]
}
```

#### ตัวอย่างการใช้งาน
```python
response = client.face_detect_multi("img/group_photo.jpg", company_name="my_company")
print("Number of faces detected:", len(response.json().get("result", [])))
```

---

### 7. `face_recog_add`
เพิ่ม/ลงทะเบียนข้อมูลภาพใบหน้าใหม่ลงในระบบฐานข้อมูลใบหน้า เพื่อนำไปค้นหาระบุตัวตน (1:N) ในอนาคต
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-recognition/add`
* **ค่าใช้จ่าย**: 1 IC ต่อการลงทะเบียนภาพใหม่

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `file_path` | `str` | ใช่ | — | พาธของรูปใบหน้าบุคคลใหม่ |
| `company_name` | `str` | ใช่ | — | โดเมนฐานข้อมูลบริษัทที่ต้องการจัดเก็บ |
| `name` | `str` | ใช่ | — | ชื่อของบุคคลเจ้าของใบหน้า |
| `password` | `str` | ใช่ | — | รหัสผ่านสำหรับการบันทึกเข้าฐานข้อมูล |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | ข้อมูลฟอร์มเพิ่มเติม |
| `files` | `List[Any]` | ไม่ | `None` | ไฟล์อื่นเพิ่มเติม |

#### ตัวอย่างผลลัพธ์ (HTTP 200)
```json
{
  "company": "my_company",
  "face_id": "260616-1",
  "message": "successfully added"
}
```

#### ตัวอย่างการใช้งาน
```python
response = client.face_recog_add(
    file_path="img/employee_john.jpg",
    company_name="my_company",
    name="john_doe",
    password="secure_password"
)
print("Enroll Status:", response.json().get("message"))
```

---

### 8. `face_recog_remove`
ลบข้อมูลประวัติใบหน้าของบุคคลออกจากระบบฐานข้อมูลเปรียบเทียบ
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-recognition/remove`
* **ค่าใช้จ่าย**: 0.1 IC ต่อการเรียกใช้งาน

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `company_name` | `str` | ใช่ | — | โดเมนของฐานข้อมูลบริษัท |
| `name` | `str` | ใช่ | — | ชื่อบุคคลที่ต้องการนำออก |
| `company_password` | `str` | ใช่ | — | รหัสผ่านประจำฐานข้อมูล |
| `date` | `str` | ใช่ | — | วันที่ทำการลงทะเบียนครั้งแรก (รูปแบบ YYYY-MM-DD) |
| `face_id` | `str` | ใช่ | — | รหัสไอดีประจำรูปใบหน้า (Face ID) |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | พารามิเตอร์เพิ่มเติม |

#### ตัวอย่างผลลัพธ์ (HTTP 200)
```json
{
  "message": "successfully removed"
}
```

#### ตัวอย่างการใช้งาน
```python
response = client.face_recog_remove(
    company_name="my_company",
    name="john_doe",
    company_password="secure_password",
    date="2026-06-16",
    face_id="260616-1"
)
print("Remove Result:", response.json().get("message"))
```

---

### 9. `face_recog_check`
ตรวจสอบสถิติ จำนวนข้อมูลใบหน้าและรายชื่อทั้งหมดที่มีอยู่ภายใต้ฐานข้อมูลบริษัทของตนเอง
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-recognition/check`
* **ค่าใช้จ่าย**: 0.2 IC ต่อการตรวจ

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `company_name` | `str` | ใช่ | — | ชื่อของโดเมนบริษัทที่ลงทะเบียนไว้ |
| `company_password` | `str` | ใช่ | — | รหัสผ่านสำหรับตรวจสอบสิทธิ์ |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | พารามิเตอร์เพย์โหลดเพิ่มเติม |

#### ตัวอย่างผลลัพธ์ (HTTP 200)
```json
{
  "company": "my_company",
  "feature_count": 12,
  "message": "successfully performed",
  "name": {
    "john_doe": 1,
    "jane_smith": 2
  },
  "name_count": 2
}
```

#### ตัวอย่างการใช้งาน
```python
response = client.face_recog_check("my_company", "secure_password")
print("Total Features:", response.json().get("feature_count"))
```

---

### 10. `face_recog_export`
ดึงข้อมูล Feature Vectors ทั้งหมดที่มีเก็บไว้ในรูปแบบข้อมูล CSV ออกมาสำรองข้อมูล
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-recognition/export`
* **ค่าใช้จ่าย**: 2 IC ต่อการส่งออก

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `company_name` | `str` | ใช่ | — | ชื่อโดเมนบริษัท |
| `company_password` | `str` | ใช่ | — | รหัสผ่านเข้าถึง |
| `type_file` | `str` | ใช่ | — | รูปแบบไฟล์ส่งออก (แนะนำ `"csv"`) |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | พารามิเตอร์เพย์โหลดเสริม |

#### ตัวอย่างผลลัพธ์ (HTTP 200)
ผลลัพธ์ที่ได้รับจะเป็นข้อความในลักษณะไฟล์ CSV คั่นด้วยเครื่องหมายจุลภาค:
```csv
company,name,face_id,feature
my_company,john_doe,260616-1,0.051097 -0.02256 0.07414 ...
```

#### ตัวอย่างการใช้งาน
```python
response = client.face_recog_export("my_company", "secure_password", "csv")
csv_data = response.text
print(csv_data[:200])
```

---

### 11. `face_recog_import`
นำเข้ารายการข้อมูลใบหน้าจำนวนมากพร้อมกันผ่านไฟล์ประเภท CSV
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-recognition/import`
* **ค่าใช้จ่าย**: 5 IC ต่อการเรียกนำเข้าไฟล์

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `file_path` | `str` | ใช่ | — | พาธของไฟล์ CSV นำเข้าข้อมูล |
| `company_name` | `str` | ใช่ | — | ชื่อโดเมนบริษัท |
| `password` | `str` | ใช่ | — | รหัสผ่านประจำฐานข้อมูล |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | เพย์โหลดเพิ่มเติม |
| `files` | `List[Any]` | ไม่ | `None` | ไฟล์เพิ่มเติม |

#### ตัวอย่างการใช้งาน
```python
response = client.face_recog_import(
    file_path="exports/import_faces.csv",
    company_name="my_company",
    password="secure_password"
)
print("Import Status:", response.json().get("message"))
```

---

### 12. `face_recog_single`
ระบุตัวตนใบหน้าเดี่ยว (1:N Search) เพื่อเปรียบเทียบภาพใบหน้ากับคลังรูปภาพในฐานข้อมูลทั้งหมดของบริษัทว่าคือใคร
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-recognition/single`
* **ค่าใช้จ่าย**: 1.5 IC ต่อการตรวจค้นหา

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `file_path` | `str` | ใช่ | — | พาธของรูปเปรียบเทียบเป้าหมาย |
| `company_name` | `str` | ใช่ | — | โดเมนบริษัทที่ใช้คนหาใบหน้า |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | เพย์โหลดเสริม |
| `files` | `List[Any]` | ไม่ | `None` | ไฟล์อัปโหลดเพิ่ม |

#### ตัวอย่างผลลัพธ์ (HTTP 200)
```json
{
  "bbox": {
    "xmax": 1185.966,
    "xmin": 822.673,
    "ymax": 682.444,
    "ymin": 187.184
  },
  "company": "my_company",
  "detection_score": 0.999,
  "message": "successfully performed",
  "name": "john_doe",
  "recognition_score": 0.9567
}
```

#### ตัวอย่างการใช้งาน
```python
response = client.face_recog_single("img/who_is_this.jpg", "my_company")
result = response.json()
if result.get("name") != "unknown":
    print(f"Identified as: {result['name']} (Score: {result['recognition_score']})")
```

---

### 13. `face_recog_multi`
ตรวจสอบและค้นหาระบุตัวตนของทุกคนที่ปรากฏอยู่ภายในภาพ (Many-to-N) เปรียบเทียบกับฐานข้อมูล
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-recognition/multi`
* **ค่าใช้จ่าย**: 2 IC ต่อการตรวจค้นหา

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `file_path` | `str` | ใช่ | — | พาธของไฟล์รูปภาพกลุ่มคน |
| `company_name` | `str` | ใช่ | — | โดเมนของบริษัทที่ใช้ตรวจ |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | เพย์โหลดส่งเสริม |
| `files` | `List[Any]` | ไม่ | `None` | ไฟล์เพิ่มเติม |

#### ตัวอย่างการใช้งาน
```python
response = client.face_recog_multi("img/staff_meeting.jpg", "my_company")
for person in response.json().get("result", []):
    print(f"Name: {person.get('name')}, BBox: {person.get('bbox')}")
```

---

### 14. `face_recog_facecrop`
ตัดครอบภาพใบหน้าและระบุตัวตนใบหน้าเปรียบเทียบในขั้นตอนเดียวกันด้วยความแม่นยำสูง
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-recognition/facecrop`
* **ค่าใช้จ่าย**: 1.5 IC ต่อการเรียกใช้งาน

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `file_path` | `str` | ใช่ | — | พาธรูปภาพเป้าหมาย |
| `company_name` | `str` | ใช่ | — | โดเมนระบบบริษัท |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | ข้อมูลเพิ่มเติม |
| `files` | `List[Any]` | ไม่ | `None` | ไฟล์เพิ่มเติม |

#### ตัวอย่างการใช้งาน
```python
response = client.face_recog_facecrop("img/snapshot.jpg", "my_company")
print("Recognition Result:", response.json())
```

---

### 15. `face_ver_config_score`
ตั้งค่าเกณฑ์คะแนนขั้นต่ำ (Threshold) สำหรับการตรวจสอบและเปรียบเทียบใบหน้าแบบ 1:1 ของบริษัท
* **หมวดหมู่**: eKYC (Score Config)
* **Endpoint**: `POST /face_config_score`
* **ค่าใช้จ่าย**: ฟรี (จัดการการกำหนดค่าระบบ)

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `detect_value` | `float` | ใช่ | — | ระดับเกณฑ์ตรวจจับใบหน้าต่ำสุด (0.0 ถึง 1.0) |
| `compare_value` | `float` | ใช่ | — | ระดับเกณฑ์เปรียบเทียบใบหน้าเหมือนสูงสุด (0.0 ถึง 1.0) |
| `company_name` | `str` | ใช่ | — | โดเมนบริษัทที่ประสงค์จะตั้งค่า |
| `company_password` | `str` | ใช่ | — | รหัสผ่านประจำระบบฐานข้อมูลบริษัท |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | เพย์โหลดเพิ่มเติม |

#### ตัวอย่างการใช้งาน
```python
response = client.face_ver_config_score(
    detect_value=0.5,
    compare_value=0.7,
    company_name="my_company",
    company_password="secure_password"
)
print("Config status code:", response.status_code)
```

> [!NOTE]
> **การแก้ไขในแผน C-2:** สำหรับกลุ่มตั้งค่าคะแนนความคล้ายคลึง (`face_ver_*`, `face_detect_*`, `face_recog_*`) ได้ปรับลดโค้ดส่วนเกินโดยเรียกใช้ตัวกลางส่วนตัว `_face_config_score` ทำให้ไม่สูญเสียความปลอดภัยและลดโอกาสเกิดข้อผิดพลาดในการอัปเกรด URL ในอนาคต

---

### 16. `face_detect_config_score`
ปรับระดับคะแนนเกณฑ์ขั้นต่ำของการแยกแยะ/ตรวจจับใบหน้าในภาพทั่วไป
* **หมวดหมู่**: eKYC (Score Config)
* **Endpoint**: `POST /face_config_score`
* **ค่าใช้จ่าย**: ฟรี

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `detect_value` | `float` | ใช่ | — | เกณฑ์การตรวจจับใบหน้าต่ำสุด (0.0 ถึง 1.0) |
| `company_name` | `str` | ใช่ | — | โดเมนบริษัท |
| `company_password` | `str` | ใช่ | — | รหัสผ่าน |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | เพย์โหลดเสริม |

#### ตัวอย่างการใช้งาน
```python
response = client.face_detect_config_score(0.6, "my_company", "secure_password")
```

---

### 17. `face_recog_config_score`
ตั้งค่าเกณฑ์คะแนนตรวจจับและเกณฑ์เปรียบเทียบในส่วนของการระบุตัวตนใบหน้าแบบ 1:N
* **หมวดหมู่**: eKYC (Score Config)
* **Endpoint**: `POST /face_config_score`
* **ค่าใช้จ่าย**: ฟรี

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `detect_value` | `float` | ใช่ | — | คะแนนตรวจจับใบหน้าต่ำสุด (0.0 ถึง 1.0) |
| `recog_value` | `float` | ใช่ | — | คะแนนวิเคราะห์เปรียบเทียบต่ำสุด (0.0 ถึง 1.0) |
| `company_name` | `str` | ใช่ | — | โดเมนบริษัท |
| `company_password` | `str` | ใช่ | — | รหัสผ่าน |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | เพย์โหลดเสริม |

#### ตัวอย่างการใช้งาน
```python
response = client.face_recog_config_score(0.5, 0.75, "my_company", "secure_password")
```

---

### 18. `img_bg_removal_file`
ประมวลผลลบภาพพื้นหลังของรูปภาพเพื่อแยกองค์ประกอบหลัก (เช่น ภาพถ่ายหน้าตรงฉากหลังสีฟ้า หรือภาพเซลฟี่) โดยแปลงเป็นไฟล์ภาพที่โปร่งใสหรือมีฉากหลังที่กำหนด
* **หมวดหมู่**: Smart City / Image Processing
* **Endpoint**: `POST /v3/store/smart-city/remove-background`
* **ค่าใช้จ่าย**: 1 IC ต่อการเรียกใช้งาน

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `file_path` | `str` | ใช่ | — | พาธของรูปภาพดั้งเดิม |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | เพย์โหลดเพิ่มเติม |
| `files` | `List[Any]` | ไม่ | `None` | อาร์เรย์ของไฟล์เพิ่มเติม |
| `output_path` | `str` | ไม่ | `None` | พาธปลายทางที่ต้องการให้บันทึกไฟล์ภาพผลลัพธ์ลงเครื่องคอมพิวเตอร์ |

#### ผลลัพธ์กลับคืน (Response)
ส่งคืนค่าอ็อบเจกต์ `requests.Response` โดยบันทึกไฟล์ภาพฉากหลังโปร่งใสรูปแบบ PNG/JPG ไปยังพาธที่กำหนดในตัวแปร `output_path` (หากส่งค่า `None` ระบบจะทำการแปลงปลายทางตามชุดคำสั่งสภาพแวดล้อมมาตรฐาน)

#### ตัวอย่างการใช้งาน
```python
response = client.img_bg_removal_file(
    file_path="img/avatar.jpg",
    output_path="img/avatar_no_bg.png"
)
print("Saved image size:", len(response.content), "bytes")
```

> [!NOTE]
> **การแก้ไขในแผน C-4:** ได้รับการยกเลิกการเขียนบันทึกไฟล์แบบตายตัว (Hardcoded) ที่ปลายทางโฟลเดอร์ `"media/img_bg_removal_file.jpg"` เสมอในรุ่นก่อน ปัจจุบันใช้ระบบสร้างและค้นหาพาธปลายทาง `build_output_path` ที่ยืดหยุ่นกว่าเดิม

---

### 19. `face_id_card_verification`
เปรียบเทียบตรวจสอบใบหน้า Selfie กับภาพหน้าตรงที่อยู่บนบัตรประชาชนไทย (eKYC) เพื่อระบุตัวตนและยืนยันการทำธุรกรรมทางการเงินและออนไลน์
* **หมวดหมู่**: eKYC
* **Endpoint**: `POST /v3/store/ekyc/face-and-id-card-verification`
* **ค่าใช้จ่าย**: 1 IC ต่อการตรวจทาน

#### พารามิเตอร์
| พารามิเตอร์ | ชนิดข้อมูล | จำเป็น | ค่าเริ่มต้น | คำอธิบาย |
| :--- | :---: | :---: | :---: | :--- |
| `id_card_path` | `str` | ใช่ | — | พาธไฟล์ภาพบัตรประชาชนไทย (ขนาดควรไม่น้อยกว่า 600x400 พิกเซล) |
| `selfie_path` | `str` | ใช่ | — | พาธไฟล์ภาพถ่าย Selfie หน้าตรงของบุคคลนั้น |
| `headers` | `Dict[str, str]` | ไม่ | `None` | HTTP headers |
| `data_payload` | `Dict[str, Any]` | ไม่ | `None` | เพย์โหลดฟอร์มอื่น ๆ |
| `files` | `List[Any]` | ไม่ | `None` | ไฟล์เพิ่มเติม |

#### ตัวอย่างผลลัพธ์ (HTTP 200)
```json
{
  "isSamePerson": true,
  "confidence": 0.982345
}
```

#### ตัวอย่างการใช้งาน
```python
# สำคัญ: ให้อ้างอิงวิธีแก้ปัญหาการสลับตำแหน่งอาร์กิวเมนต์ด้านล่างนี้
response = client.face_id_card_verification(
    id_card_path="img/selfie_image.jpg",  # ส่งภาพ Selfie เป็นอาร์กิวเมนต์ตัวแรก
    selfie_path="img/id_card_front.jpg"   # ส่งภาพบัตรประชาชนเป็นอาร์กิวเมนต์ตัวที่สอง
)
print("Is same person:", response.json().get("isSamePerson"))
```

> [!WARNING]
> **ข้อควรทราบและจุดผิดพลาดสำคัญ (Critical Bug in SDK):**
> ภายในตัว SDK รุ่นปัจจุบันมีข้อจำกัดเรื่องลำดับพารามิเตอร์: ตัวแปร `id_card_path` จะถูกแมปข้อมูลเข้าไปที่ช่อง `file0` ของ Multipart Request และ `selfie_path` จะถูกแมปเข้าช่อง `file1` แต่ระบบหลังบ้านของ iApp (Live API) กำหนดให้ช่อง `file0` ต้องส่งข้อมูลเป็นภาพ Selfie และช่อง `file1` ต้องส่งเป็นภาพบัตรประชาชน
> 
> **วิธีการแก้ไข:** นักพัฒนาจำเป็นต้องทำการ **สลับอาร์กิวเมนต์ยามเรียกใช้งาน (Parameter Swap)** เพื่อความถูกต้องในระบบจริง โดยส่งพาธภาพ Selfie เข้าที่พารามิเตอร์ `id_card_path` และส่งพาธภาพบัตรประชาชนไปที่ `selfie_path` ตามตัวอย่างด้านบน

---

## 🚫 ข้อความแสดงข้อผิดพลาดและแนวทางแก้ไข (HTTP Status Codes)

| HTTP Status | ความหมายของการทำงานผิดพลาด | แนวทางการแก้ไขเบื้องต้น |
| :---: | :--- | :--- |
| **400** | รูปภาพไม่ได้สัดส่วน/ส่งข้อมูลผิดรูปแบบ | ตรวจสอบชนิดไฟล์ (รองรับ JPG/PNG) และขนาดพิกเซลขั้นต่ำ |
| **401** | API Key ผิดพลาด | ตรวจสอบรหัส Key ประจำโดเมนของตนเอง |
| **402** | เครดิต (IC) ไม่พอใช้งาน | ทำการเติม iApp Credit ในระบบจัดการก่อนเรียกซ้ำ |
| **421** | ชื่อบริษัท (Company) หรือรหัสผ่านไม่ถูกต้อง | ตรวจสอบความถูกต้องของชื่อ namespace ฐานข้อมูลและรหัสผ่าน |
| **422** | การตรวจสอบล้มเหลว (Validation Error) | ตรวจสอบว่าได้กรอกพารามิเตอร์ที่จำเป็นครบถ้วนแล้วหรือไม่ |
| **424** | ขนาดใบหน้ามีขนาดเล็กเกินไปในขั้นตอนประมวลผล | แนะนำให้ใช้รูปถ่ายหน้าตรงที่ไม่มีการบดบังและใกล้กล้องมากขึ้น |
| **500** | ข้อผิดพลาดภายในของเซิร์ฟเวอร์หลังบ้าน | รอระยะเวลาหนึ่งก่อนทดลองเรียกใหม่ หรือตรวจสอบรูปแบบและขนาดของไฟล์ที่ส่ง |

---
