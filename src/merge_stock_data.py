from pathlib import Path

import pandas as pd
import yfinance as yf


BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

TREND_PATH = PROCESSED_DIR / "all_companies_trends_cleaned.csv"
OUTPUT_PATH = PROCESSED_DIR / "all_companies_model_data.csv"


def fetch_stock_data(ticker, start_date, end_date):
    """
    Yahoo Finance에서 주가 데이터 수집
    """

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

    # yfinance 버전에 따라 MultiIndex 컬럼이 생기는 경우 처리
    if isinstance(stock.columns, pd.MultiIndex):
        stock.columns = stock.columns.get_level_values(0)

    stock = stock.reset_index()
    stock["Date"] = pd.to_datetime(stock["Date"])
    stock["ticker"] = ticker

    return stock


def make_features(df):
    """
    머신러닝 학습용 파생 변수 생성
    """

    df = df.sort_values(["ticker", "Date"]).copy()

    # 수익률
    df["return"] = df.groupby("ticker")["Close"].pct_change()

    # 이전 수익률
    df["return_lag1"] = df.groupby("ticker")["return"].shift(1)

    # 최근 평균 수익률
    df["return_lag3_mean"] = (
        df.groupby("ticker")["return"]
        .transform(lambda x: x.rolling(3).mean())
    )

    df["return_lag7_mean"] = (
        df.groupby("ticker")["return"]
        .transform(lambda x: x.rolling(7).mean())
    )

    # 거래량 변화율
    df["volume_change"] = df.groupby("ticker")["Volume"].pct_change()

    # 이동평균
    df["ma5"] = (
        df.groupby("ticker")["Close"]
        .transform(lambda x: x.rolling(5).mean())
    )

    df["ma20"] = (
        df.groupby("ticker")["Close"]
        .transform(lambda x: x.rolling(20).mean())
    )

    # 이동평균 대비 현재 종가 차이
    df["ma5_gap"] = (df["Close"] - df["ma5"]) / df["ma5"]
    df["ma20_gap"] = (df["Close"] - df["ma20"]) / df["ma20"]

    # 최근 7일 변동성
    df["volatility_7"] = (
        df.groupby("ticker")["return"]
        .transform(lambda x: x.rolling(7).std())
    )

    # 다음날 수익률
    df["next_return"] = df.groupby("ticker")["return"].shift(-1)

    # target: 다음날 상승 여부
    df["target"] = (df["next_return"] > 0).astype(int)

    return df


def main():
    if not TREND_PATH.exists():
        print(f"[에러] 검색량 파일 없음: {TREND_PATH}")
        return

    trend_df = pd.read_csv(TREND_PATH)
    trend_df["Date"] = pd.to_datetime(trend_df["Date"])

    tickers = trend_df["ticker"].unique()

    start_date = trend_df["Date"].min().strftime("%Y-%m-%d")
    end_date = (trend_df["Date"].max() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"[검색량 데이터] {TREND_PATH}")
    print(f"[수집 기간] {start_date} ~ {end_date}")
    print(f"[종목 수] {len(tickers)}개")
    print(tickers)

    stock_list = []

    for ticker in tickers:
        stock_df = fetch_stock_data(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
        )

        if not stock_df.empty:
            stock_list.append(stock_df)

    if not stock_list:
        print("[에러] 수집된 주가 데이터가 없습니다.")
        return

    stock_all = pd.concat(stock_list, ignore_index=True)

    merged = pd.merge(
        trend_df,
        stock_all,
        on=["Date", "ticker"],
        how="inner",
    )

    print(f"[병합 후 데이터 크기] {merged.shape}")

    merged = make_features(merged)

    # 파생 변수 생성으로 생긴 결측치 제거
    merged = merged.dropna()

    merged.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print("[저장 완료]")
    print(OUTPUT_PATH)
    print(f"[최종 데이터 크기] {merged.shape}")
    print(merged.head())


if __name__ == "__main__":
    main()