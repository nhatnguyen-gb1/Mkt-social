# PHASE 0 — AI LEAD QUALIFICATION SYSTEM: IMPLEMENTATION ROADMAP & COST ESTIMATION

Lộ trình triển khai 7 Giai đoạn (Phase 1–7 Roadmap), Đánh giá Chi phí (Paid API vs Self-host) và Ước lượng Độ khó cho module **AI Lead Qualification System** trong AIMOS.

---

## 🗺️ 1. LỘ TRÌNH TRIỂN KHAI THỰC THI (PHASE 1 - 7 ROADMAP)

```text
PHASE 0 (Hiện tại) : Research, Security & Master Architecture Design
       ↓
PHASE 1            : Provider Interfaces & Data Schemas (Code Abstraction)
       ↓
PHASE 2            : Outbound Call Engine & WebSocket Streaming Server
       ↓
PHASE 3            : Conversation Engine, Prompt Engineering & Tool Calling
       ↓
PHASE 4            : Qualification & Dynamic Lead Scoring Engine
       ↓
PHASE 5            : CRM Integration Adapters & Telegram Notification Bot
       ↓
PHASE 6            : Telephony Trunking (SIP/Twilio) & E2E Testing with Mocks
       ↓
PHASE 7            : Real Provider Pilot & Production Readiness Verification
```

### Chi tiết nhiệm vụ từng Phase:

#### **Phase 1: Core Interfaces & Data Schemas**
- Đóng gói các class Abstraction Interface (`TelephonyProvider`, `SpeechToTextProvider`, `LanguageModelProvider`, `TextToSpeechProvider`, `CRMProvider`, `LeadScoringEngine`).
- Khai báo Pydantic Schemas cho `Lead`, `Conversation`, `Transcript`, `Qualification`, `LeadScore`, `CallResult`, `SalesHandoff`.

#### **Phase 2: Outbound Call Queue & Streaming Engine**
- Xây dựng hệ thống hàng chờ cuộc gọi (Call Queue) với cơ chế kiểm tra Eligibility/Consent Gate.
- Phát triển WebSocket Engine truyền nhận luồng âm thanh PCM 2 chiều (Full-Duplex Audio).

#### **Phase 3: Conversation Engine & Voice Pipeline Integration**
- Tích hợp STT $\rightarrow$ LLM $\rightarrow$ TTS Streaming Pipeline.
- Phát triển cơ chế xử lý ngắt lời (Barge-in / Interruption handling) và tự động nhận diện kết thúc câu nói (VAD & Endpointing).

#### **Phase 4: Qualification & Configurable Scoring Engine**
- Xây dựng module trích xuất tự động thông tin BANT (Budget, Authority, Need, Timeline).
- Phát triển Engine tính điểm LeadScore (0-100) theo tệp quy tắc động cấu hình qua YAML.

#### **Phase 5: CRM Sync & Instant Handoff Alert**
- Phát triển các CRM Adapters (HubSpot, ZOHO, Custom Webhook CRM).
- Tích hợp Telegram Notification Bot bắn thông báo tức thì cho Sales khi phát hiện Hot Lead.

#### **Phase 6: SIP Telephony Integration & Sandbox Testing**
- Nối mạng thử nghiệm với Twilio / SIP Trunk Sandbox.
- Tiến hành kiểm thử E2E end-to-end từ tiếp nhận Lead đến Handoff với dữ liệu giả lập (Mock).

#### **Phase 7: Pilot Launch & Production Hardening**
- Chạy thử nghiệm Pilot nhỏ (100 cuộc gọi/ngày).
- Tối ưu hóa độ trễ đàm thoại (< 800ms) và hoàn thiện hệ thống Audit Log & PII Security.

---

## 💰 2. BẢNG PHÂN TÍCH PAID API VS SELF-HOST

| Thành phần | Phương án API Trả phí (Paid SaaS API) | Phương án Self-Host (Tự vận hành) | Đề xuất tối ưu cho Production |
| :--- | :--- | :--- | :--- |
| **Telephony** | **Twilio / Telnyx / Plivo** ($0.013 - $0.02 / phút) | **FreePBX / Asterisk SIP Server** + Thẻ SIM/Trunk nội địa | **SIP Trunking Nội địa** (Tiết kiệm 70% cước gọi) |
| **Speech-to-Text (STT)** | **Deepgram Nova-2 / AssemblyAI** ($0.0043 / phút) | **Whisper-Live / Faster-Whisper** trên GPU (T4/A10G) | **Deepgram API** (Độ trễ thấp < 200ms, tự nâng cấp) |
| **Language Model (LLM)** | **OpenAI gpt-4o-mini** ($0.15 / 1M tokens) | **Ollama / vLLM** (Llama 3.3 70B / Qwen 2.5) | **OpenAI gpt-4o-mini** (Chi phí siêu rẻ, phản hồi nhanh) |
| **Text-to-Speech (TTS)** | **ElevenLabs / Cartesia** ($0.015 - $0.03 / phút) | **Piper TTS / Kokoro TTS** trên GPU | **Cartesia / ElevenLabs API** (Giọng nói Tiếng Việt tự nhiên) |
| **CRM** | **HubSpot / Salesforce API** | **PostgreSQL / Self-hosted CRM** | **CRM Adapter đa năng** (Tuộc nhu cầu doanh nghiệp) |

---

## 📊 3. ƯỚC LƯỢNG ĐỘ KHÓ VÀ THỜI GIAN THEO TỪNG PHASE

| Giai đoạn | Nội dung công việc chính | Độ khó (1 - 5 ⭐) | Thời gian ước tính |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Abstraction Interfaces & Schemas | ⭐⭐ (Trung bình) | 3 - 5 ngày |
| **Phase 2** | Call Queue & WebSocket Engine | ⭐⭐⭐⭐ (Khó) | 7 - 10 ngày |
| **Phase 3** | Streaming Voice Pipeline & Barge-in | ⭐⭐⭐⭐⭐ (Cực khó) | 10 - 14 ngày |
| **Phase 4** | Qualification & Scoring Engine | ⭐⭐⭐ (Trung bình) | 5 - 7 ngày |
| **Phase 5** | CRM Sync & Telegram Notification | ⭐⭐ (Dễ - Trung bình) | 3 - 5 ngày |
| **Phase 6** | SIP Trunking & Sandbox E2E Testing | ⭐⭐⭐⭐ (Khó) | 7 - 10 ngày |
| **Phase 7** | Pilot Launch & Performance Hardening | ⭐⭐⭐ (Trung bình) | 5 - 7 ngày |
