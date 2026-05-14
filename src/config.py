import os

# ==========================================
# 1. 기업 및 주식 설정 (Company & Stock)
# ==========================================

# yfinance 티커 기준: KOSPI (.KS), KOSDAQ (.KQ)
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
    "000660.KS": {
        "company_name": "SK하이닉스",
        "foreign_ratio": 0.53,
        "keywords": {
            "base": "SK하이닉스",
            "stock": "SK하이닉스 주가",
            "forecast": "SK하이닉스 전망",
            "earnings": "SK하이닉스 실적",
            "business_plan": "SK하이닉스 사업계획서",
        },
    },
    "035420.KS": {
        "company_name": "네이버",
        "foreign_ratio": 0.45,
        "keywords": {
            "base": "네이버",
            "stock": "네이버 주가",
            "forecast": "네이버 전망",
            "earnings": "네이버 실적",
            "business_plan": "네이버 사업계획서",
        },
    },
    "012450.KS": {
        "company_name": "한화에어로스페이스",
        "foreign_ratio": 0.32,
        "keywords": {
            "base": "한화에어로스페이스",
            "stock": "한화에어로스페이스 주가",
            "forecast": "한화에어로스페이스 전망",
            "earnings": "한화에어로스페이스 실적",
            "business_plan": "한화에어로스페이스 사업계획서",
        },
    },
    "066570.KS": {
        "company_name": "LG전자",
        "foreign_ratio": 0.36,
        "keywords": {
            "base": "LG전자",
            "stock": "LG전자 주가",
            "forecast": "LG전자 전망",
            "earnings": "LG전자 실적",
            "business_plan": "LG전자 사업계획서",
        },
    },
    "005380.KS": {
        "company_name": "현대차",
        "foreign_ratio": 0.40,
        "keywords": {
            "base": "현대차",
            "stock": "현대차 주가",
            "forecast": "현대차 전망",
            "earnings": "현대차 실적",
            "business_plan": "현대차 사업계획서",
        },
    },
}

# ==========================================
# 2. 데이터 수집 기간 (Date Range)
# ==========================================

START_DATE = "2025-05-12"
END_DATE = "2026-05-12"

# ==========================================
# 3. Google Trends 공통 설정
# ==========================================

GOOGLE_TRENDS_HL = "ko-KR"
GOOGLE_TRENDS_TZ = 540
GOOGLE_TRENDS_CAT = 0  # 0: 전체, 7: 금융

# pytrends 속도 제한 및 안정성 설정
PYTRENDS_RETRIES = 5
PYTRENDS_BACKOFF_FACTOR = 0.5
PYTRENDS_WAIT_TIME = 40  # API 호출 간 대기 시간 (초)

# 긴 기간 수집을 위한 청크 설정
GOOGLE_TRENDS_CHUNK_DAYS = 90
GOOGLE_TRENDS_OVERLAP_DAYS = 7

# ==========================================
# 4. 국내 및 글로벌 특정 설정 (Domestic & Global)
# ==========================================

# 국내(Domestic) 설정
GOOGLE_TRENDS_GEO_KR = "KR"

# 글로벌(Global) 설정
GOOGLE_TRENDS_GEO_GLOBAL = ""  # 공백은 전세계를 의미

# 결과 파일명 설정
ALL_COMPANIES_TRENDS_KR_FILE = "all_companies_google_trends_daily.csv"
ALL_COMPANIES_TRENDS_GLOBAL_FILE = "all_companies_global_trends.csv"

# 기업별 글로벌 트렌드 파일 매핑 (data/raw/google_trends 내 실제 파일명 준수)
GLOBAL_TREND_FILES = {
    "005930.KS": "samsung_global.csv",
    "000660.KS": "skhynix_global.csv",
    "035420.KS": "naver_global.csv",
    "012450.KS": "hanwha_global.csv",
    "066570.KS": "lg_global.csv",
    "005380.KS": "hyundai_global.csv",
}

# ==========================================
# 5. 경로 설정 (Path)
# ==========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
GOOGLE_TRENDS_RAW_DIR = os.path.join(RAW_DATA_DIR, "google_trends")
STOCK_RAW_DIR = os.path.join(RAW_DATA_DIR, "stock")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# 폴더 자동 생성
for path in [
    DATA_DIR,
    RAW_DATA_DIR,
    GOOGLE_TRENDS_RAW_DIR,
    STOCK_RAW_DIR,
    PROCESSED_DATA_DIR,
    MODELS_DIR,
    REPORTS_DIR,
]:
    if not os.path.exists(path):
        os.makedirs(path)
