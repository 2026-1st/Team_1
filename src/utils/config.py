import os
from pathlib import Path

# Project Root
ROOT_DIR = Path(__file__).parent.parent.parent

# Data Paths
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"

# Sub-directories for raw data
STOCK_RAW_DIR = DATA_RAW_DIR / "stock"
TREND_RAW_DIR = DATA_RAW_DIR / "google_trends"

# Model & Report Paths
MODEL_DIR = ROOT_DIR / "models"
REPORT_DIR = ROOT_DIR / "reports"

# Tickers & Settings
TICKERS = ['삼성전자', 'SK하이닉스', '현대차', 'LG전자', 'NAVER', '한화에어로스페이스']
TICKER_MAP = {
    '삼성전자': '005930.KS',
    'SK하이닉스': '000660.KS',
    '현대차': '005380.KS',
    'LG전자': '066570.KS',
    'NAVER': '035420.KS',
    '한화에어로스페이스': '012450.KS'
}

# Training Settings
RANDOM_SEED = 42
TS_SPLITS = 5
FEATURE_COUNT = 20  # Minimum target features

# Ensure directories exist
for d in [DATA_PROCESSED_DIR, MODEL_DIR, REPORT_DIR]:
    d.mkdir(parents=True, exist_ok=True)
