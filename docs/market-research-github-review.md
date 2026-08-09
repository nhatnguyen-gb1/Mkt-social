# MARKET RESEARCH AGENT: GITHUB OPEN SOURCE REVIEW & ADAPTATION REPORT

Báo cáo nghiên cứu, đối chiếu và đề xuất cải tiến cho **Market Research Agent V1** dựa trên các dự án nguồn mở hàng đầu trên GitHub:
1. `BayramAnnakov/synthetic-market-research` (Khung khảo sát giả lập Synthetic Market Surveys & Price Testing)
2. `VoltAgent/awesome-agent-skills` (Kho 1,000+ Agent Skills bao gồm Competitor Profiling & Battlecards)
3. `ramamoorthy07/Multi-Agent-Market-Research` (CrewAI/LangGraph Orchestrated Market Intelligence)
4. `ferdinandobons/startup-skill` (Tri thức thẩm định ý tưởng khởi nghiệp & PMF Validation)

---

## 📌 1. EVALUATION OF GITHUB REPOSITORIES

| Repository | Đặc điểm nổi bật | License | Độ phù hợp với AIMOS |
| :--- | :--- | :--- | :--- |
| `BayramAnnakov/synthetic-market-research` | Giả lập khảo sát người tiêu dùng bằng AI để đo độ co giãn của giá (Willingness to Pay) | MIT | **Rất cao** (Adapt thành `synthetic_consumer_survey` Skill) |
| `VoltAgent/awesome-agent-skills` | Thư viện Competitor Profiling & Battlecards chuẩn hóa | MIT | **Rất cao** (Adapt thành `competitor_battlecard` Skill) |
| `ramamoorthy07/Multi-Agent-Market-Research` | Luồng thu thập dữ liệu tin tức & phân tích xu hướng ngành | Apache 2.0 | High (Phù hợp bổ sung Knowledge) |
| `ferdinandobons/startup-skill` | Bộ tiêu chuẩn thẩm định tính khả thi dự án (Validation Checklist) | MIT | High (Phù hợp bổ sung Validation) |

---

## 💡 2. ADAPTED SKILLS & KNOWLEDGE INTO AIMOS-NATIVE

### A. Skill 1: `synthetic_consumer_survey` (Adapted từ `BayramAnnakov/synthetic-market-research`, MIT License)
- **Mục tiêu**: Giả lập khảo sát tâm lý tiêu dùng của 100 khách hàng mục tiêu đại diện (Synthetic Persona Panel) để đo lường mức độ sẵn sàng chi trả (Willingness to Pay) và mức giá trần/sàn.
- **Tệp tạo**: `backend/skills/synthetic_consumer_survey/*` (`SKILL.md`, `RULES.md`, `EXAMPLES.md`, `EVALS.md`).

### B. Skill 2: `competitor_battlecard` (Adapted từ `VoltAgent/awesome-agent-skills`, MIT License)
- **Mục tiêu**: Đóng gói Hồ sơ Cạnh tranh (Competitor Battlecard) trực diện so sánh tính năng, điểm yếu và cách chiến thắng đối thủ (How to Win Against Competitor X).
- **Tệp tạo**: `backend/skills/competitor_battlecard/*` (`SKILL.md`, `RULES.md`, `EXAMPLES.md`, `EVALS.md`).

### C. Bổ sung Knowledge Module: `synthetic_survey_methodology.md`
- **Thư mục**: `backend/agents/market_research/KNOWLEDGE/synthetic_survey_methodology.md`.

---

## 🛡️ 3. LICENSING, SECURITY & ARCHITECTURE INTEGRITY
- **License Compliance**: Tất cả các mã nguồn/tri thức tham khảo đều thuộc giấy phép **MIT License** hoặc **Apache 2.0**.
- **Security Check**: Không đưa mã nguồn bên thứ 3 trực tiếp vào production; chỉ học hỏi tư duy framework và tự phát triển AIMOS-native 100%.
- **Architecture**: Không làm vỡ bất kỳ API hay test case hiện tại nào.
