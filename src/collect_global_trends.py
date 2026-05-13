from pathlib import Path

import pandas as pd

import config
from trend_collector import GoogleTrendsCollector


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw" / "google_trends"
RAW_DIR.mkdir(parents=True, exist_ok=True)


GLOBAL_TREND_FILES = {
    "005930.KS": "samsung_global.csv",
    "000660.KS": "skhynix_global.csv",
    "035420.KS": "naver_global.csv",
    "012450.KS": "hanwha_global.csv",
    "066570.KS": "lg_global.csv",
    "005380.KS": "hyundai_global.csv",
}


def main():
    collector = GoogleTrendsCollector()
    original_geo = config.GOOGLE_TRENDS_GEO
    config.GOOGLE_TRENDS_GEO = ""

    try:
        for ticker, company_info in config.COMPANY_CONFIG.items():
            keyword = company_info["keywords"]["base"]
            company_name = company_info["company_name"]

            print("=" * 60)
            print(f"[글로벌 검색량 수집] {company_name} / {ticker} / geo=global")
            print("=" * 60)

            trend_df = collector.fetch_daily_trend_by_chunks(
                keyword=keyword,
                start_date=config.START_DATE,
                end_date=config.END_DATE,
                chunk_days=config.GOOGLE_TRENDS_CHUNK_DAYS,
                overlap_days=config.GOOGLE_TRENDS_OVERLAP_DAYS,
            )

            if trend_df is None or trend_df.empty:
                print(f"[스킵] 글로벌 검색량 없음: {company_name}")
                continue

            output_path = RAW_DIR / GLOBAL_TREND_FILES[ticker]
            trend_df.to_csv(output_path, index=False, encoding="utf-8-sig")
            print(f"[저장 완료] {output_path}")

        all_global = []
        for ticker, filename in GLOBAL_TREND_FILES.items():
            path = RAW_DIR / filename
            if not path.exists():
                continue

            df = pd.read_csv(path)
            df["ticker"] = ticker
            df["company_name"] = config.COMPANY_CONFIG[ticker]["company_name"]
            all_global.append(df)

        if all_global:
            output_path = RAW_DIR / "all_companies_global_trends.csv"
            pd.concat(all_global, ignore_index=True).to_csv(
                output_path,
                index=False,
                encoding="utf-8-sig",
            )
            print(f"[전체 글로벌 저장 완료] {output_path}")

    finally:
        config.GOOGLE_TRENDS_GEO = original_geo


if __name__ == "__main__":
    main()
