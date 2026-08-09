# PHASE 0 — AI LEAD QUALIFICATION SYSTEM: DATA MODEL & SCHEMA DESIGN

Bản thiết kế Mô hình Dữ liệu (Data Model) và Cấu trúc Data Schemas cho module **AI Lead Qualification System** trong AIMOS.

---

## 📊 1. DANH SÁCH MÔ HÌNH DỮ LIỆU CỐT LÕI (CORE DATA MODELS)

### 1.1. `Lead` Model
Lưu trữ thông tin định danh và hồ sơ tiếp nhận ban đầu của Lead.
```json
{
  "lead_id": "lead_987654321",
  "phone_number": "+84901234567",
  "full_name": "Nguyen Van A",
  "email": "nguyenvana@example.com",
  "source": "FACEBOOK_ADS_LEAD_FORM",
  "campaign_id": "camp_2026_q3_bds",
  "consent_status": "GRANTED",
  "consent_timestamp": "2026-08-09T10:00:00Z",
  "eligibility_status": "ELIGIBLE",
  "created_at": "2026-08-09T10:05:00Z"
}
```

### 1.2. `Conversation` Model
Quản lý trạng thái và phiên đàm thoại thoại AI Outbound với khách hàng.
```json
{
  "conversation_id": "conv_123456789",
  "lead_id": "lead_987654321",
  "call_status": "COMPLETED",
  "start_time": "2026-08-09T10:15:00Z",
  "end_time": "2026-08-09T10:18:30Z",
  "duration_seconds": 210,
  "telephony_provider": "Twilio",
  "recording_url": "s3://aimos-recordings/2026/08/conv_123456789.mp3",
  "metadata": {
    "stt_provider": "Deepgram",
    "tts_provider": "ElevenLabs",
    "llm_provider": "OpenAI"
  }
}
```

### 1.3. `Transcript` Model
Ghi lại nội dung hội thoại từng câu (Turn-by-turn Speech Log) kèm mốc thời gian.
```json
{
  "transcript_id": "tr_555444333",
  "conversation_id": "conv_123456789",
  "turns": [
    {
      "speaker": "AI_AGENT",
      "text": "Dạ em chào anh A, em gọi từ AIMOS để hỗ trợ anh thông tin về căn hộ cao cấp ạ.",
      "timestamp_ms": 1200
    },
    {
      "speaker": "CUSTOMER",
      "text": "Chào em, anh đang tìm mua căn 2 phòng ngủ ngân sách tầm 4 tỷ.",
      "timestamp_ms": 5400
    }
  ]
}
```

### 1.4. `Qualification` Model
Trích xuất dữ liệu nhu cầu chi tiết của Lead theo các tiêu chí tiêu chuẩn.
```json
{
  "qualification_id": "qual_777888999",
  "lead_id": "lead_987654321",
  "conversation_id": "conv_123456789",
  "intent": "PURCHASE_HIGH_INTENT",
  "product_interest": "Căn hộ 2 Phòng Ngủ",
  "location": "Quận 7, TP.HCM",
  "budget": "4.000.000.000 VND",
  "timeline": "Trong vòng 1 tháng",
  "financing": "Cần vay ngân hàng 50%",
  "purpose": "Mua ở thực",
  "purchase_intent": "VERY_HIGH",
  "appointment_intent": "ACCEPTED",
  "extracted_at": "2026-08-09T10:19:00Z"
}
```

### 1.5. `LeadScore` Model
Khung điểm số được đánh giá tự động dựa trên các tiêu chí cấu hình.
```json
{
  "score_id": "score_11223344",
  "lead_id": "lead_987654321",
  "overall_score": 88.5,
  "segment": "HOT_LEAD",
  "score_breakdown": {
    "budget_match": 30.0,
    "timeline_urgency": 25.0,
    "intent_clarity": 20.0,
    "financing_readiness": 13.5
  },
  "evaluated_at": "2026-08-09T10:19:05Z"
}
```

### 1.6. `CallResult` Model
Kết quả cuộc gọi và tóm tắt thực thi (Executive Call Brief).
```json
{
  "call_result_id": "res_99887766",
  "conversation_id": "conv_123456789",
  "outcome": "QUALIFIED_HOT",
  "summary": "Khách hàng Nguyễn Văn A có nhu cầu mua ở thực căn hộ 2PN tại Q7, ngân sách 4 tỷ, chuẩn bị xuống tiền trong tháng này. Đã đồng ý lịch hẹn khảo sát nhà mẫu sáng T7.",
  "key_action_items": [
    "Gửi Brochure dự án qua Zalo/Email",
    "Đặt lịch hẹn Sale dẫn đi xem nhà mẫu 9h00 T7"
  ]
}
```

### 1.7. `SalesHandoff` Model
Lưu vết quá trình chuyển giao cho nhân viên Sales hoặc đặt lịch tự động.
```json
{
  "handoff_id": "ho_33445566",
  "lead_id": "lead_987654321",
  "assigned_sales_rep_id": "sales_emp_007",
  "assigned_sales_name": "Tran Van B",
  "status": "ASSIGNED",
  "appointment_time": "2026-08-11T09:00:00Z",
  "handoff_timestamp": "2026-08-09T10:20:00Z",
  "crm_sync_status": "SYNCED_SUCCESS"
}
```

---

## ⚙️ 2. CONFIGURABLE LEAD SCORING FRAMEWORK

Khung chấm điểm Lead động (Configurable Scoring Engine) cho phép định nghĩa các trọng số tính điểm khác nhau theo từng ngành hàng kinh doanh (Bất động sản, Ô tô, Giáo dục, SaaS, Tài chính):

```yaml
scoring_profile: "REAL_ESTATE_HIGH_VALUE"
max_score: 100
dimensions:
  budget_alignment:
    weight: 0.30
    rules:
      - condition: "budget >= 3000000000"
        score: 100
      - condition: "budget >= 2000000000"
        score: 70
  timeline_urgency:
    weight: 0.25
    rules:
      - condition: "timeline <= '1 month'"
        score: 100
      - condition: "timeline <= '3 months'"
        score: 60
  appointment_readiness:
    weight: 0.25
    rules:
      - condition: "appointment_intent == 'ACCEPTED'"
        score: 100
  location_fit:
    weight: 0.20
    rules:
      - condition: "location in target_zones"
        score: 100

segmentation_thresholds:
  HOT_LEAD: 80.0
  WARM_LEAD: 50.0
  COLD_LEAD: 0.0
```
