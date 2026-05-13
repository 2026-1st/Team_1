import os
from datetime import datetime, timedelta

# ==========================================
# 데이터 수집 설정
# ==========================================

# yfinance 기준:
# KOSPI: .KS
# KOSDAQ: .KQ
#
# keywords:
# base          : 기업명 기본 검색
# stock         : 주가 관심
# forecast      : 전망 관심
# earnings      : 실적 관심
# business_plan : 사업계획서 관심

COMPANY_CONFIG = {
    "005930.KS": {
        "company_name": "삼성전자",
        "foreign_ratio": 0.50,
        "keywords": {
            "base": "삼성전자",
            "stock": "삼성전자 주가",
            "forecast": "삼성전자 전망",
            "earnings": "삼성전자 실적",
            "business_plan": "삼성전자 사업계획서",
        },
    },
}

# ==========================================
# 데이터 수집 기간 설정
# ==========================================

# 약 250~300개 일간 데이터를 확보하기 위해 최근 365일 기준으로 설정
# 주식시장은 휴장일이 있어서 365일을 가져오면 실제 거래일은 약 250개 내외가 됨
DAYS_BACK = 30

START_DATE = "2025-04-01"
END_DATE = "2025-04-30"

# ==========================================
# Google Trends 설정
# ==========================================

GOOGLE_TRENDS_HL = "ko-KR"
GOOGLE_TRENDS_TZ = 540

# 한국 검색량 기준
GOOGLE_TRENDS_GEO = "KR"

# 전체 카테고리
# 금융 카테고리로 제한하려면 7 사용 가능
GOOGLE_TRENDS_CAT = 0

# pytrends 속도 제한 완화 설정
PYTRENDS_RETRIES = 5
PYTRENDS_BACKOFF_FACTOR = 0.5
PYTRENDS_WAIT_TIME = 40

# ==========================================
# 경로 설정
# ==========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# 폴더 자동 생성
for path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, REPORTS_DIR]:
    if not os.path.exists(path):
        os.makedirs(path)