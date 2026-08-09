# PHASE 0 — AI LEAD QUALIFICATION SYSTEM: SECURITY & COMPLIANCE SPECIFICATION

Bản quy định Bảo mật (Security), Quản trị An toàn Dữ liệu (PII Protection) và Khung Tuân thủ Pháp lý (Compliance Framework) cho module **AI Lead Qualification System** trong AIMOS.

---

## 🛡️ 1. KHUNG QUẢN TRỊ BẢO MẬT HỆ THỐNG (SECURITY ARCHITECTURE)

### 1.1. Secret Management (Quản lý Khóa Bí mật)
- **Quy tắc**: Tuyệt đối không hard-code các API Key (Twilio, Deepgram, OpenAI, ElevenLabs) trong mã nguồn.
- **Giải pháp**: Tất cả các secret được nạp qua Environment Variables (`.env`) bảo vệ bởi Vault hoặc AWS Secrets Manager.

### 1.2. Role-Based Access Control (RBAC) & Permissions
- Phân quyền nghiêm ngặt giữa các vai trò:
  - `Admin`: Cấu hình hệ thống, quản lý Provider API Keys và Scoring Weights.
  - `Sales Supervisor`: Xem toàn bộ Transcript, nghe file ghi âm cuộc gọi, điều chỉnh Lead Score thủ công.
  - `Sales Rep`: Chỉ xem các Lead được giao (Assigned Leads) và bản tóm tắt cuộc gọi (Summary).
  - `System Agent`: Chỉ chạy lệnh qua Service Account với quyền hạn bị giới hạn.

### 1.3. Audit Logging (Nhật ký Giám sát)
- Mọi thao tác từ tạo cuộc gọi, thay đổi Consent status, xem bản ghi âm cuộc gọi đến xuất dữ liệu PII đều phải được ghi lại vào nhật ký Audit Log (`AuditLog` Model) bất biến (immutable).

---

## 🔒 2. BẢO VỆ DỮ LIỆU CÁ NHÂN (PII PROTECTION & RECORDING POLICY)

### 2.1. PII Encryption & Masking
- **Dữ liệu nhạy cảm**: Số điện thoại, Họ tên, Email, Địa chỉ nhà, Thông tin Tài chính.
- **Mã hóa**: Mã hóa dữ liệu lưu trữ (Data at Rest) bằng AES-256; Mã hóa đường truyền (Data in Transit) bằng TLS 1.3.
- **Che giấu (Masking)**: Số điện thoại hiển thị trên giao diện người dùng phải được che (Masking): `+8490****567`.

### 2.2. Audio Recording Policy & Retention
- **Ghi âm có điều kiện**: Chỉ tiến hành ghi âm cuộc gọi khi được sự đồng ý của khách hàng.
- **Thời hạn lưu trữ (Data Retention Policy)**:
  - File ghi âm gốc (`.mp3`): Tự động xóa hoặc đưa vào Cold Storage mã hóa sau 30 ngày.
  - Transcript đã che thông tin nhạy cảm: Lưu trữ 180 ngày để phục vụ huấn luyện và đánh giá chất lượng.

---

## ⚖️ 3. KHUNG TUÂN THỦ PHÁP LÝ & ĐẠO ĐỨC AI (COMPLIANCE FRAMEWORK)

### 3.1. Minh bạch Thông tin AI (AI Disclosure & Anti-Impersonation Gate)
- **Quy tắc cấm**: Tuyệt đối **KHÔNG** giả mạo là người thật hoặc đánh lừa khách hàng rằng họ đang nói chuyện với con người.
- **Lời chào bắt buộc (Mandatory Script)**: Ngay từ giây đầu tiên của cuộc gọi Outbound, AI bắt buộc phải công khai danh tính:
  > *"Em chào anh/chị, em là AI Trợ lý Tư vấn tự động gọi từ thương hiệu [Tên Công ty]..."*

### 3.2. Eligibility & Consent Gate (Cổng Kiểm duyệt Tính hợp pháp)
Trước khi đưa bất kỳ số điện thoại nào vào Hàng chờ Cuộc gọi (`Outbound Call Queue`), hệ thống phải thực thi 4 bước kiểm duyệt nghiêm ngặt:
1. **Consent Verification**: Kiểm tra Lead có cho phép gọi điện thoại hay không (Opt-in Consent).
2. **DNC List Check (Do-Not-Call)**: Kiểm tra số điện thoại có nằm trong Danh sách Từ chối Nhận Quảng cáo Quốc gia hoặc Danh sách Đen của công ty hay không.
3. **Time Window Policy**: Chỉ cho phép gọi Outbound trong khung giờ văn minh (Từ 8:30 đến 11:30 và 14:00 đến 17:30 các ngày làm việc; Cấm gọi buổi tối, cuối tuần và ngày lễ).
4. **Call Frequency Limit**: Tối đa 1 cuộc gọi/ngày và không quá 3 lần thử lại cho 1 Lead nếu không bắt máy.

### 3.3. Call Authorization & Human Approval Gate
- **Human-in-the-Loop**: Tất cả các cuộc gọi Outbound chiến dịch lớn (> 500 leads/ngày) bắt buộc phải có sự phê duyệt thủ công (Human Approval) của Trưởng phòng Marketing / Sales trước khi kích hoạt hàng chờ.
