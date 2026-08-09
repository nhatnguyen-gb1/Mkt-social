# PRODUCT AGENT: GITHUB OPEN SOURCE REVIEW & ADAPTATION REPORT

Báo cáo nghiên cứu, đối chiếu và đề xuất cải tiến cho **Product Agent V1** dựa trên các dự án nguồn mở hàng đầu trên GitHub:
1. `assimovt/productskills` (Bộ Agent Skills quản lý Chiến lược Sản phẩm & PRD Writing)
2. `playing-to-win-framework` (Khung thiết lập Rào chắn Cạnh tranh & Moats Kernel)
3. `shape-up-pitching` (Khung định hình giải pháp Appetite & Pitching)
4. `mom-test-interview-framework` (Khung thẩm định giả định bằng chứng thực tế Mom Test)

---

## 📌 1. EVALUATION OF GITHUB REPOSITORIES

| Repository | Đặc điểm nổi bật | License | Độ phù hợp với AIMOS |
| :--- | :--- | :--- | :--- |
| `assimovt/productskills` | Cung cấp các skill viết PRD, phân tích Moats và Value Proposition | MIT | **Rất cao** (Adapt thành `prd_document_generation` Skill) |
| `mom-test-interview-framework` | Thẩm định giả định sản phẩm qua câu hỏi Mom Test chống giả định ảo | MIT | **Rất cao** (Adapt thành `mom_test_validation` Skill) |
| `playing-to-win-framework` | Xây dựng rào chắn cạnh tranh (Defensible Moats) | Apache 2.0 | High (Phù hợp bổ sung Knowledge) |
| `shape-up-pitching` | Phân bổ phạm vi giải pháp (Appetite Shaping) | MIT | High (Phù hợp bổ sung Validation) |

---

## 💡 2. ADAPTED SKILLS & KNOWLEDGE INTO AIMOS-NATIVE

### A. Skill 1: `mom_test_validation` (Adapted từ `mom-test-interview-framework`, MIT License)
- **Mục tiêu**: Thẩm định giả định sản phẩm (Assumption Validation) bằng khung câu hỏi Mom Test (tập trung vào hành vi quá khứ, chi tiền thực tế thay vì lời hứa suông).
- **Tệp tạo**: `backend/skills/mom_test_validation/*` (`SKILL.md`, `RULES.md`, `EXAMPLES.md`, `EVALS.md`).

### B. Skill 2: `prd_document_generation` (Adapted từ `assimovt/productskills`, MIT License)
- **Mục tiêu**: Đóng gói Tài liệu Chiến lược Sản phẩm (Product Requirement Document - PRD) chuẩn hóa.
- **Tệp tạo**: `backend/skills/prd_document_generation/*` (`SKILL.md`, `RULES.md`, `EXAMPLES.md`, `EVALS.md`).

### C. Bổ sung Knowledge Module: `mom_test_framework.md`
- **Thư mục**: `backend/agents/product/KNOWLEDGE/mom_test_framework.md`.

---

## 🛡️ 3. LICENSING, SECURITY & ARCHITECTURE INTEGRITY
- **License Compliance**: Tất cả các mã nguồn/tri thức tham khảo đều thuộc giấy phép **MIT License** hoặc **Apache 2.0**.
- **Security Check**: Không đưa mã nguồn bên thứ 3 trực tiếp vào production; tự phát triển 100% Native AIMOS.
- **Architecture**: Bảo toàn 100% các API và test cases hiện tại.
