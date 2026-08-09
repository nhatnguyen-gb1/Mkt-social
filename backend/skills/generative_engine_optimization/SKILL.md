name: generative_engine_optimization
version: 1.0.0
description: "Tối ưu hóa sự xuất hiện và trích dẫn thương hiệu trên các Công cụ Tìm kiếm AI (Generative Engine Optimization - GEO)."
purpose: "Đảm bảo các mô hình AI Search (ChatGPT, Gemini, Perplexity) khuyên dùng sản phẩm khi người dùng hỏi mua."
inputs:
  - "product_name: Tên sản phẩm"
outputs:
  - "geo_keywords: Bộ từ khóa hội thoại người dùng hỏi AI"
  - "citation_sources: Các kênh báo chí / forum AI thường trích dẫn"
  - "schema_markup_recommendations: Đề xuất cấu trúc dữ liệu Schema.org"
workflow:
  - "Step 1: Phân tích các câu hỏi người dùng thường hỏi AI Search."
  - "Step 2: Đưa ra danh sách kênh báo chí và dữ liệu cấu trúc Schema.org tối ưu trích dẫn."
constraints:
  - "Không cố tình tạo spam content ảo."
dependencies: []
# Source Attribution: Inspired by coreyhaines31/marketingskills (MIT License)
