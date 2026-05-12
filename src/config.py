import os
from datetime import datetime, timedelta

# ==========================================
# 데이터 수집 (Data Collection) 설정
# ==========================================

# 수집할 주식 종목 및 해당 키워드 맵핑
# TICKER: 주식 심볼 (yfinance 기준, KOSPI는 .KS / KOSDAQ은 .KQ)
# KEYWORD: Google Trends 검색어
TICKER_CONFIG = {
    "005930.KS": "삼성전자",
    "000660.KS": "SK하이닉스",
    "035420.KS": "네이버",
    "012450.KS": "한화에어로스페이스",
    "066570.KS": "LG전자"
}

# 데이터 수집 기간 설정
# 현재 날짜 기준 몇 일 전부터 데이터를 가져올지 설정
DAYS_BACK = 365
START_DATE = (datetime.now() - timedelta(days=DAYS_BACK)).strftime('%Y-%m-%d')
END_DATE = datetime.now().strftime('%Y-%m-%d')

# Google Trends 설정
GOOGLE_TRENDS_HL = 'ko-KR'  # 한국어 검색량 수집을 위해 ko-KR로 변경
GOOGLE_TRENDS_TZ = 540      # 한국 표준시 (KST, UTC+9)는 540분

# pytrends 속도 제한(429 Error) 완화를 위한 설정
PYTRENDS_RETRIES = 5
PYTRENDS_BACKOFF_FACTOR = 0.5
PYTRENDS_WAIT_TIME = 5  # API 요청 간 대기 시간 (초)

# ==========================================
# 경로 (Path) 설정
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# 폴더 자동 생성
for path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, REPORTS_DIR]:
    if not os.path.exists(path):
        os.makedirs(path)
