from pathlib import Path

import pandas as pd

import config
from trend_collector import GoogleTrendsCollector


def print_collection_header(company_name: str, ticker: str):
    print("=" * 60)
    print(f"[글로벌 검색량 수집] {company_name} / {ticker} / geo=global")
    print("=" * 60)


def fetch_company_global_trend(
    collector: GoogleTrendsCollector,
    company_info: dict,
) -> pd.DataFrame | None:
    keyword = company_info["keywords"]["base"]

    return collector.fetch_daily_trend_by_chunks(
        keyword=keyword,
        start_date=config.START_DATE,
        end_date=config.END_DATE,
        chunk_days=config.GOOGLE_TRENDS_CHUNK_DAYS,
        overlap_days=config.GOOGLE_TRENDS_OVERLAP_DAYS,
    )


def save_company_global_trend(ticker: str, trend_df: pd.DataFrame):
    output_path = Path(config.GOOGLE_TRENDS_RAW_DIR) / config.GLOBAL_TREND_FILES[ticker]
    trend_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"[저장 완료] {output_path}")


def collect_all_company_global_trends(collector: GoogleTrendsCollector):
    for ticker, company_info in config.COMPANY_CONFIG.items():
        company_name = company_info["company_name"]
        print_collection_header(company_name, ticker)

        trend_df = fetch_company_global_trend(collector, company_info)

        if trend_df is None or trend_df.empty:
            print(f"[스킵] 글로벌 검색량 없음: {company_name}")
            continue

        save_company_global_trend(ticker, trend_df)


def load_company_global_trends() -> list[pd.DataFrame]:
    all_global = []

    for ticker, filename in config.GLOBAL_TREND_FILES.items():
        path = Path(config.GOOGLE_TRENDS_RAW_DIR) / filename
        if not path.exists():
            continue

        df = pd.read_csv(path)
        df["ticker"] = ticker
        df["company_name"] = config.COMPANY_CONFIG[ticker]["company_name"]
        all_global.append(df)

    return all_global


def save_all_company_global_trends(all_global: list[pd.DataFrame]):
    if not all_global:
        print("[경고] 통합 저장할 글로벌 검색량 데이터 없음")
        return

    output_path = Path(config.GOOGLE_TRENDS_RAW_DIR) / config.ALL_COMPANIES_GLOBAL_TRENDS_FILE
    pd.concat(all_global, ignore_index=True).to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )
    print(f"[전체 글로벌 저장 완료] {output_path}")


def run_with_global_geo():
    collector = GoogleTrendsCollector()
    original_geo = config.GOOGLE_TRENDS_GEO
    config.GOOGLE_TRENDS_GEO = ""

    try:
        collect_all_company_global_trends(collector)
        save_all_company_global_trends(load_company_global_trends())
    finally:
        config.GOOGLE_TRENDS_GEO = original_geo


def main():
    run_with_global_geo()


if __name__ == "__main__":
    main()
