"""
AIMOS Phase 2 Mock Lead Qualification Dataset (100 Scenarios).
Distribution:
- 20 HOT Leads
- 20 WARM Leads
- 20 COLD Leads
- 20 INVALID Leads
- 20 UNKNOWN / AMBIGUOUS Leads
"""

MOCK_DATASET_100 = []

# 1. 20 HOT LEADS
for i in range(1, 21):
    MOCK_DATASET_100.append({
        "id": f"hot_{i:03d}",
        "lead": {"source": "Facebook Ads", "phone": f"+84901000{i:03d}"},
        "conversation": [
            {"speaker": "CUSTOMER", "text": f"Anh đang tìm căn hộ 2 phòng ngủ khoảng {3+i*0.1:.1f} tỷ, muốn mua ngay trong tuần này tại Quận 7."}
        ],
        "expected_classification": "HOT",
        "expected_intent": "BUY",
        "has_contradiction": False,
    })

# 2. 20 WARM LEADS
for i in range(1, 21):
    MOCK_DATASET_100.append({
        "id": f"warm_{i:03d}",
        "lead": {"source": "Google Search Ads", "phone": f"+84902000{i:03d}"},
        "conversation": [
            {"speaker": "CUSTOMER", "text": "Anh đang xem thông tin dự án, ngân sách tầm 2.5 tỷ nhưng chưa vội mua."}
        ],
        "expected_classification": "WARM",
        "expected_intent": "BUY",
        "has_contradiction": False,
    })

# 3. 20 COLD LEADS
for i in range(1, 21):
    MOCK_DATASET_100.append({
        "id": f"cold_{i:03d}",
        "lead": {"source": "TikTok Ads", "phone": f"+84903000{i:03d}"},
        "conversation": [
            {"speaker": "CUSTOMER", "text": "Anh chỉ xem cho biết thôi chứ chưa có ý định mua gì hết."}
        ],
        "expected_classification": "COLD",
        "expected_intent": "BROWSING",
        "has_contradiction": False,
    })

# 4. 20 INVALID LEADS
for i in range(1, 21):
    MOCK_DATASET_100.append({
        "id": f"invalid_{i:03d}",
        "lead": {"source": "Web Form", "phone": f"+84904000{i:03d}"},
        "conversation": [
            {"speaker": "CUSTOMER", "text": "Tôi nhầm số rồi, không phải tôi đăng ký, đừng gọi nữa."}
        ],
        "expected_classification": "INVALID",
        "expected_intent": "REJECT",
        "has_contradiction": False,
    })

# 5. 20 UNKNOWN / AMBIGUOUS LEADS (Contradictions, Slang, Missing Info)
for i in range(1, 21):
    if i % 2 == 1:
        # Contradiction scenario
        MOCK_DATASET_100.append({
            "id": f"unknown_{i:03d}",
            "lead": {"source": "Zalo Ads", "phone": f"+84905000{i:03d}"},
            "conversation": [
                {"speaker": "CUSTOMER", "text": "Anh có ngân sách 3 tỷ."},
                {"speaker": "CUSTOMER", "text": "Thực ra anh chỉ có khoảng 1.5 tỷ thôi."}
            ],
            "expected_classification": "UNKNOWN",
            "expected_intent": "BUY",
            "has_contradiction": True,
        })
    else:
        # Busy / Missing Info scenario
        MOCK_DATASET_100.append({
            "id": f"unknown_{i:03d}",
            "lead": {"source": "Referral", "phone": f"+84905000{i:03d}"},
            "conversation": [
                {"speaker": "CUSTOMER", "text": "Anh đang bận họp, lúc khác gọi lại."}
            ],
            "expected_classification": "WARM",
            "expected_intent": "BUSY",
            "has_contradiction": False,
        })
