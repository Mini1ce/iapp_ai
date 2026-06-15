"""Offline mock tests for the newly added and remaining SDK methods."""

import json
import io
from iapp_ai import api


def test_llm_chat(mock_sdk_request):
    client = api("TEST_KEY")
    
    # 1. Default model chinda-qwen3-4b
    resp = client.llm_chat(prompt="Hello", system_prompt="Be polite")
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.iapp.co.th/v3/llm/chinda-thaillm-4b/chat/completions"
    assert call["apikey"] == "TEST_KEY"
    body = json.loads(call["json_body"] or call["data"])
    assert body["model"] == "chinda-qwen3-4b"
    assert body["messages"] == [
        {"role": "system", "content": "Be polite"},
        {"role": "user", "content": "Hello"}
    ]
    
    # 2. Model deepseek-chat
    resp = client.llm_chat(prompt="Hi", model="deepseek-chat")
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["url"] == "https://api.iapp.co.th/v3/llm/deepseek-3p2/chat/completions"


def test_thanoy_legal_qa(mock_sdk_request):
    client = api("TEST_KEY")
    resp = client.thanoy_legal_qa(query="Legal question")
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.iapp.co.th/thanoy"
    body = json.loads(call["json_body"] or call["data"])
    assert body["query"] == "Legal question"


def test_image_generation(mock_sdk_request):
    client = api("TEST_KEY")
    # Default model
    resp = client.image_generation(prompt="A beautiful cat")
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.iapp.co.th/v3/image/generation/google/nanobanana/generate"
    body = json.loads(call["json_body"] or call["data"])
    assert body["contents"][0]["parts"][0]["text"] == "A beautiful cat"

    # Model nanobanana-pro
    resp = client.image_generation(prompt="A beautiful dog", model="nanobanana-pro")
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["url"] == "https://api.iapp.co.th/v3/image/generation/google/nanobananapro/generate"


def test_seedance_video_flow(mock_sdk_request):
    client = api("TEST_KEY")
    
    # 1. Submit
    resp = client.seedance_video_submit(prompt="A flowing river", model="seedance-fast")
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.iapp.co.th/v3/store/video/seedance/tasks"
    body = json.loads(call["json_body"] or call["data"])
    assert body["model"] == "dreamina-seedance-2-0-fast-260128"
    assert body["content"][0]["text"] == "A flowing river"
    
    # 2. Status
    resp_status = client.seedance_video_status(task_id="video-task-123")
    assert resp_status.status_code == 200
    call_status = mock_sdk_request["calls"][-1]
    assert call_status["method"] == "GET"
    assert call_status["url"] == "https://api.iapp.co.th/v3/store/video/seedance/tasks/video-task-123"


def test_ocr_new_endpoints(mock_sdk_request, tmp_path):
    client = api("TEST_KEY")
    f = tmp_path / "doc.pdf"
    f.write_bytes(b"pdf_content")
    
    # 1. Receipt OCR
    resp = client.receipt_ocr(str(f), return_ocr=True)
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.iapp.co.th/v3/store/ocr/receipt"
    assert call["data"]["return_ocr"] == "true"
    assert call["files"][0][0] == "file"
    assert call["files"][0][1][0] == "doc.pdf"
    
    # 2. Credit Card Statement OCR
    resp = client.credit_card_statement_ocr(str(f))
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["url"] == "https://api.iapp.co.th/v3/store/ocr/creditcard-statement"
    assert "return_ocr" not in call["data"]
    
    # 3. Tax Deduction Certificate OCR
    resp = client.tax_deduction_certificate_ocr(str(f), return_ocr=True)
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["url"] == "https://api.iapp.co.th/v3/store/ocr/tax-deduction-certificate"
    
    # 4. Civil Registration OCR
    resp = client.civil_registration_ocr(str(f))
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["url"] == "https://api.iapp.co.th/v3/store/ocr/civil-registeration-certificate"
    
    # 5. Resume OCR
    resp = client.resume_ocr(str(f))
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["url"] == "https://api.iapp.co.th/v3/store/ocr/curriculum-vitae"
    
    # 6. Job Description OCR
    resp = client.job_description_ocr(str(f))
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["url"] == "https://api.iapp.co.th/v3/store/ocr/job-description"


def test_speech_to_text(mock_sdk_request, tmp_path):
    client = api("TEST_KEY")
    f = tmp_path / "voice.wav"
    f.write_bytes(b"audio")
    
    # th / base
    resp = client.speech_to_text(str(f), language="th", quality="base", chunk_size=30)
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.iapp.co.th/v3/store/speech/speech-to-text/base"
    assert call["data"]["chunk_size"] == "30"
    
    # en / pro
    resp = client.speech_to_text(str(f), language="en", quality="pro")
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["url"] == "https://api.iapp.co.th/v3/store/speech/speech-to-text/pro/en"
    assert "chunk_size" not in call["data"]


def test_voice_clone_tts(mock_sdk_request, tmp_path):
    client = api("TEST_KEY")
    f = tmp_path / "ref.wav"
    f.write_bytes(b"audio")
    
    resp = client.voice_clone_tts(text="Hello world", ref_audio_path=str(f), ref_text="reference text", speed=1.2)
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.iapp.co.th/v3/store/audio/tts/clone"
    assert call["data"]["text"] == "Hello world"
    assert call["data"]["ref_text"] == "reference text"
    assert call["data"]["speed"] == "1.2"
    assert call["files"][0][0] == "ref_audio"


def test_ai_audio_detection(mock_sdk_request, tmp_path):
    client = api("TEST_KEY")
    f = tmp_path / "test.wav"
    f.write_bytes(b"audio")
    
    resp = client.ai_audio_detection(audio_path=str(f))
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.iapp.co.th/v3/store/audio/tts/detect"
    assert call["files"][0][0] == "audio"


def test_sentiment_and_toxicity(mock_sdk_request):
    client = api("TEST_KEY")
    
    # Sentiment
    resp_sent = client.sentiment_analysis(text="วันนี้มีความสุขมาก")
    assert resp_sent.status_code == 200
    call_sent = mock_sdk_request["calls"][-1]
    assert call_sent["method"] == "POST"
    assert call_sent["url"] == "https://api.iapp.co.th/v3/store/nlp/sentiment-analysis"
    assert call_sent["params"]["text"] == "วันนี้มีความสุขมาก"
    
    # Toxicity
    resp_tox = client.toxicity_classification(text="เกลียดแกจริง")
    assert resp_tox.status_code == 200
    call_tox = mock_sdk_request["calls"][-1]
    assert call_tox["method"] == "POST"
    assert call_tox["url"] == "https://api.iapp.co.th/v3/store/nlp/toxicity-classification"
    assert call_tox["params"]["text"] == "เกลียดแกจริง"


def test_thai_holidays(mock_sdk_request):
    client = api("TEST_KEY")
    
    # 1. By year
    resp1 = client.thai_holidays(year=2026)
    assert resp1.status_code == 200
    call1 = mock_sdk_request["calls"][-1]
    assert call1["method"] == "GET"
    assert call1["url"] == "https://api.iapp.co.th/v3/store/data/thai-holiday/year/2026"
    assert call1["params"]["holiday_type"] == "public"
    
    # 2. By range
    resp2 = client.thai_holidays(start_date="2026-01-01", end_date="2026-01-31", holiday_type="public")
    assert resp2.status_code == 200
    call2 = mock_sdk_request["calls"][-1]
    assert call2["url"] == "https://api.iapp.co.th/v3/store/data/thai-holiday/range"
    assert call2["params"]["start_date"] == "2026-01-01"
    assert call2["params"]["end_date"] == "2026-01-31"
    
    # 3. Public holiday around today
    resp3 = client.thai_holidays(days_after=15)
    assert resp3.status_code == 200
    call3 = mock_sdk_request["calls"][-1]
    assert call3["url"] == "https://api.iapp.co.th/v3/store/data/thai-holiday"
    assert call3["params"]["days_after"] == "15"


def test_idcard_back(mock_sdk_request, tmp_path):
    client = api("TEST_KEY")
    f = tmp_path / "back.jpg"
    f.write_bytes(b"back_content")
    
    resp = client.idcard_back(str(f))
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.iapp.co.th/thai-national-id-card/v3.5/back"
    assert call["files"][0][0] == "file"
    assert call["files"][0][1][2] == "image/jpg"


def test_license_plate(mock_sdk_request, tmp_path):
    client = api("TEST_KEY")
    f = tmp_path / "plate.jpg"
    f.write_bytes(b"plate")
    
    # 1. OCR File
    resp = client.license_plate_ocr(str(f))
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.iapp.co.th/license-plate-recognition/file"
    assert call["files"][0][0] == "file"
    assert call["files"][0][1][2] == "image/jpg"
    
    # 2. Base64
    resp_b64 = client.license_plate_base64(data_payload="base64string")
    assert resp_b64.status_code == 200
    call_b64 = mock_sdk_request["calls"][-1]
    assert call_b64["method"] == "POST"
    assert call_b64["url"] == "https://api.iapp.co.th/iapp_license_plate_recognition_v1_base64"
    body = json.loads(call_b64["json_body"] or call_b64["data"])
    assert body["image"] == "base64string"


def test_book_bank_api(mock_sdk_request, tmp_path):
    client = api("TEST_KEY")
    f = tmp_path / "bankbook.jpg"
    f.write_bytes(b"book")
    
    resp = client.book_bank_api(str(f))
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.iapp.co.th/book-bank-ocr/file"
    assert call["files"][0][0] == "file"
    assert call["files"][0][1][2] == "image/jpg"


def test_document_ocr_remaining(mock_sdk_request, tmp_path):
    client = api("TEST_KEY")
    f = tmp_path / "doc.pdf"
    f.write_bytes(b"content")
    
    # Plaintext
    resp1 = client.document_ocr_plaintext(str(f))
    assert resp1.status_code == 200
    call1 = mock_sdk_request["calls"][-1]
    assert call1["method"] == "POST"
    assert call1["url"] == "https://api.iapp.co.th/v3/store/ocr/document/ocr"
    
    # Layout
    resp2 = client.document_ocr_json_layout(str(f))
    assert resp2.status_code == 200
    call2 = mock_sdk_request["calls"][-1]
    assert call2["method"] == "POST"
    assert call2["url"] == "https://api.iapp.co.th/v3/store/ocr/document/layout"
    
    # Docx
    resp3 = client.document_ocr_docx(str(f))
    assert resp3.status_code == 200
    call3 = mock_sdk_request["calls"][-1]
    assert call3["method"] == "POST"
    assert call3["url"] == "https://api.iapp.co.th/v3/store/ocr/document/docx"


def test_water_meter(mock_sdk_request, tmp_path):
    client = api("TEST_KEY")
    f = tmp_path / "meter.jpg"
    f.write_bytes(b"meter")
    
    # Binary
    resp1 = client.water_meter_binary(str(f))
    assert resp1.status_code == 200
    call1 = mock_sdk_request["calls"][-1]
    assert call1["method"] == "POST"
    assert call1["url"] == "https://api.iapp.co.th/meter-number-ocr/file"
    
    # Base64
    resp2 = client.water_meter_base64(data_payload="meter_b64")
    assert resp2.status_code == 200
    call2 = mock_sdk_request["calls"][-1]
    assert call2["method"] == "POST"
    assert call2["url"] == "https://api.iapp.co.th/meter-number-ocr/base64"
    body = json.loads(call2["json_body"] or call2["data"])
    assert body["image"] == "meter_b64"


def test_driver_card_ocr(mock_sdk_request, tmp_path):
    client = api("TEST_KEY")
    f = tmp_path / "driver.jpg"
    f.write_bytes(b"driver")
    
    resp = client.driver_card_ocr(str(f))
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.iapp.co.th/thai-driver-license-ocr"
    assert call["files"][0][0] == "file"
    assert call["files"][0][1][2] == "image/jpg"


def test_thai_thaitts(mock_sdk_request, monkeypatch):
    client = api("TEST_KEY")
    
    written_files = {}
    
    # We monkeypatch builtins.open to catch writes to media/ directory
    original_open = open
    def mock_open(file, mode='r', *args, **kwargs):
        if "media/" in str(file):
            bio = io.BytesIO()
            # Intercept close to store the content in written_files
            original_close = bio.close
            def tracking_close():
                written_files[str(file)] = bio.getvalue()
                return original_close()
            bio.close = tracking_close
            return bio
        return original_open(file, mode, *args, **kwargs)
        
    monkeypatch.setattr("builtins.open", mock_open)
    
    # Set the return content of mock_sdk_request to simulated wave file data
    mock_sdk_request["response_data"]["json_payload"] = {}
    
    # Kaitom
    resp_kaitom = client.thai_thaitts_kaitom(text="สวัสดี")
    assert resp_kaitom.status_code == 200
    call_kaitom = mock_sdk_request["calls"][-1]
    assert call_kaitom["method"] == "GET"
    assert call_kaitom["url"] == "https://api.iapp.co.th/thai-tts-kaitom/tts?text=สวัสดี"
    assert "media/kaitom.wav" in written_files
    
    # Cee
    resp_cee = client.thai_thaitts_cee(text="สวัสดีค่ะ")
    assert resp_cee.status_code == 200
    call_cee = mock_sdk_request["calls"][-1]
    assert call_cee["method"] == "GET"
    assert call_cee["url"] == "https://api.iapp.co.th/thai-tts-cee/tts?text=สวัสดีค่ะ"
    assert "media/cee.wav" in written_files
