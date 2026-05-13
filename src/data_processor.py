from pathlib import Path
import pandas as pd
import yfinance as yf

# 경로 설정
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw" / "google_trends"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# 설정
START_DATE = "2025-05-12"
END_DATE = "2026-05-12"
TREND_PATH = PROCESSED_DIR / "all_companies_trends_cleaned.csv"
OUTPUT_PATH = PROCESSED_DIR / "all_companies_model_data.csv"

COMPANY_CONFIG = {
    "samsung": {
        "files": ["삼성_1.csv", "삼성_2.csv", "삼성_3.csv", "삼성_4.csv"],
        "ticker": "005930.KS",
        "company_name": "삼성전자",
        "foreign_ratio": 0.50,
    },
    "skhynix": {
        "files": ["sk_1.csv", "sk_2.csv", "sk_3.csv", "sk_4.csv"],
        "ticker": "000660.KS",
        "company_name": "SK하이닉스",
        "foreign_ratio": 0.53,
    },
    "naver": {
        "files": ["네이버_1.csv", "네이버_2.csv", "네이버_3.csv", "네이버_4.csv"],
        "ticker": "035420.KS",
        "company_name": "네이버",
        "foreign_ratio": 0.45,
    },
    "hanwha": {
        "files": ["한화_1.csv", "한화_2.csv", "한화_3.csv", "한화_4.csv"],
        "ticker": "012450.KS",
        "company_name": "한화에어로스페이스",
        "foreign_ratio": 0.32,
    },
    "lg": {
        "files": ["엘지_1.csv", "엘지_2.csv", "엘지_3.csv", "엘지_4.csv"],
        "ticker": "066570.KS",
        "company_name": "LG전자",
        "foreign_ratio": 0.36,
    },
    "hyundai": {
        "files": ["현대차_1.csv", "현대차_2.csv", "현대차_3.csv", "현대차_4.csv"],
        "ticker": "005380.KS",
        "company_name": "현대차",
        "foreign_ratio": 0.40,
    },
}

# --- 1. 구글 트렌드 데이터 전처리 함수 (기존 merge_all_trends.py 로직) ---

def read_trend_csv(file_path: Path) -> pd.DataFrame:
    """트렌드 CSV 파일을 읽어서 날짜와 트렌드 컬럼을 정제함"""
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

    df = df.iloc[:, :2]
    df.columns = ["Date", "trend"]

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["trend"] = pd.to_numeric(df["trend"], errors="coerce")

    df = df.dropna(subset=["Date"])
    df = df.dropna(subset=["trend"])

    return df

def merge_company_files(company_key: str, info: dict) -> pd.DataFrame:
    """개별 기업의 여러 트렌드 파일을 하나로 병합하고 결측치를 보간함"""
    dfs = []

    for filename in info["files"]:
        file_path = RAW_DIR / filename

        if not file_path.exists():
            print(f"[파일 없음] {file_path}")
            continue

        print(f"[읽는 중] {info['company_name']} - {filename}")
        df = read_trend_csv(file_path)
        dfs.append(df)

    if not dfs:
        print(f"[스킵] {info['company_name']} 데이터 없음")
        return pd.DataFrame()

    company_df = pd.concat(dfs, ignore_index=True)

    # 겹치는 날짜는 평균 처리
    company_df = (
        company_df
        .groupby("Date", as_index=False)["trend"]
        .mean()
    )

    # 전체 일간 날짜 생성
    full_dates = pd.DataFrame({
        "Date": pd.date_range(
            start=START_DATE,
            end=END_DATE,
            freq="D"
        )
    })

    company_df = pd.merge(
        full_dates,
        company_df,
        on="Date",
        how="left"
    )

    # 핵심: 주간 데이터로 인해 생긴 중간 결측은 선형 보간
    company_df["trend"] = company_df["trend"].interpolate(method="linear")

    # 앞뒤 끝부분 결측이 남으면 가까운 값으로 채움
    company_df["trend"] = company_df["trend"].ffill().bfill()

    company_df["ticker"] = info["ticker"]
    company_df["company_name"] = info["company_name"]
    company_df["foreign_ratio"] = info["foreign_ratio"]
    company_df["weighted_trend"] = company_df["trend"] * company_df["foreign_ratio"]

    output_path = PROCESSED_DIR / f"{company_key}_trend_cleaned.csv"

    company_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"[기업 저장 완료] {output_path}")
    return company_df

# --- 2. 주가 데이터 수집 및 피처 생성 함수 (기존 merge_stock_data.py 로직) ---

def fetch_stock_data(ticker, start_date, end_date):
    """Yahoo Finance에서 주가 데이터 수집"""
    print(f"[주가 수집] {ticker}")

    stock = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        progress=False,
    )

    if stock.empty:
        print(f"[경고] 주가 데이터 없음: {ticker}")
        return pd.DataFrame()

    # MultiIndex 컬럼 처리
    if isinstance(stock.columns, pd.MultiIndex):
        stock.columns = stock.columns.get_level_values(0)

    stock = stock.reset_index()
    stock["Date"] = pd.to_datetime(stock["Date"])
    stock["ticker"] = ticker

    return stock

def make_features(df):
    """머신러닝 학습용 파생 변수 생성"""
    df = df.sort_values(["ticker", "Date"]).copy()

    # 수익률 및 지연 변수
    df["return"] = df.groupby("ticker")["Close"].pct_change()
    df["return_lag1"] = df.groupby("ticker")["return"].shift(1)
    
    # 이동 평균 수익률
    df["return_lag3_mean"] = df.groupby("ticker")["return"].transform(lambda x: x.rolling(3).mean())
    df["return_lag7_mean"] = df.groupby("ticker")["return"].transform(lambda x: x.rolling(7).mean())

    # 거래량 및 이동평균
    df["volume_change"] = df.groupby("ticker")["Volume"].pct_change()
    df["ma5"] = df.groupby("ticker")["Close"].transform(lambda x: x.rolling(5).mean())
    df["ma20"] = df.groupby("ticker")["Close"].transform(lambda x: x.rolling(20).mean())

    # 이동평균 괴리율
    df["ma5_gap"] = (df["Close"] - df["ma5"]) / df["ma5"]
    df["ma20_gap"] = (df["Close"] - df["ma20"]) / df["ma20"]

    # 변동성 및 타겟 설정
    df["volatility_7"] = df.groupby("ticker")["return"].transform(lambda x: x.rolling(7).std())
    df["next_return"] = df.groupby("ticker")["return"].shift(-1)
    df["target"] = (df["next_return"] > 0).astype(int)

    return df

# --- 3. 통합 실행 메인 함수 ---

def main():
    # 단계 1: 구글 트렌드 데이터 병합 및 정제
    print("--- 1단계: 트렌드 데이터 처리 시작 ---")
    all_trend_data = []
    for company_key, info in COMPANY_CONFIG.items():
        df = merge_company_files(company_key, info)
        if not df.empty:
            all_trend_data.append(df)

    if not all_trend_data:
        print("[에러] 처리된 트렌드 데이터가 없습니다.")
        return

    final_trend_df = pd.concat(all_trend_data, ignore_index=True)
    final_trend_df.to_csv(TREND_PATH, index=False, encoding="utf-8-sig")
    print(f"[트렌드 병합 완료] {TREND_PATH}")

    # 단계 2: 주가 데이터 병합 및 피처 생성
    print("\n--- 2단계: 주가 데이터 병합 및 피처 생성 시작 ---")
    tickers = final_trend_df["ticker"].unique()
    start_date = final_trend_df["Date"].min().strftime("%Y-%m-%d")
    # 마지막 날의 다음날 데이터까지 가져와야 다음날 수익률 계산 가능
    end_date = (final_trend_df["Date"].max() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    stock_list = []
    for ticker in tickers:
        stock_df = fetch_stock_data(ticker, start_date, end_date)
        if not stock_df.empty:
            stock_list.append(stock_df)

    if not stock_list:
        print("[에러] 수집된 주가 데이터가 없습니다.")
        return

    stock_all = pd.concat(stock_list, ignore_index=True)

    # 트렌드와 주가 데이터 병합
    merged = pd.merge(
        final_trend_df,
        stock_all,
        on=["Date", "ticker"],
        how="inner",
    )

    # 피처 생성 및 결측치 제거
    merged = make_features(merged)
    merged = merged.dropna()

    # 최종 데이터 저장
    merged.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("\n[최종 처리 완료]")
    print(f"결과 파일: {OUTPUT_PATH}")
    print(f"최종 데이터 크기: {merged.shape}")
    print(merged.head())

if __name__ == "__main__":
    main()
