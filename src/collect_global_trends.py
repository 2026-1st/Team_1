from pathlib import Path
import pandas as pd
import config
from trend_korea_collector import KoreaTrendsCollector

class GlobalTrendCollector:
    def __init__(self):
        self.collector = KoreaTrendsCollector()
        self.raw_dir = Path(config.GOOGLE_TRENDS_RAW_DIR)

    def _print_header(self, company_name: str, ticker: str):
        print("=" * 60)
        print(f"[글로벌 검색량 수집] {company_name} / {ticker} / geo=global")
        print("=" * 60)

    def collect_all_company_global_trends(self):
        # 글로벌 수집을 위해 임시로 geo 설정을 비움 (global)
        original_geo = config.GOOGLE_TRENDS_GEO_KR
        config.GOOGLE_TRENDS_GEO_KR = config.GOOGLE_TRENDS_GEO_GLOBAL
        
        try:
            for ticker, company_info in config.COMPANY_CONFIG.items():
                # ... (rest of code stays same, only geo changed)
                company_name = company_info["company_name"]
                self._print_header(company_name, ticker)

                keyword = company_info["keywords"]["base"]
                trend_df = self.collector.fetch_daily_trend_by_chunks(
                    keyword=keyword,
                    start_date=config.START_DATE,
                    end_date=config.END_DATE,
                    chunk_days=config.GOOGLE_TRENDS_CHUNK_DAYS,
                    overlap_days=config.GOOGLE_TRENDS_OVERLAP_DAYS,
                )

                if trend_df is None or trend_df.empty:
                    print(f"[스킵] 글로벌 검색량 없음: {company_name}")
                    continue

                output_path = self.raw_dir / config.GLOBAL_TREND_FILES[ticker]
                trend_df.to_csv(output_path, index=False, encoding="utf-8-sig")
                print(f"[저장 완료] {output_path}")
        finally:
            config.GOOGLE_TRENDS_GEO = original_geo

    def save_aggregated_global_trends(self):
        all_global = []
        for ticker, filename in config.GLOBAL_TREND_FILES.items():
            path = self.raw_dir / filename
            if not path.exists():
                continue

            df = pd.read_csv(path)
            df["ticker"] = ticker
            df["company_name"] = config.COMPANY_CONFIG[ticker]["company_name"]
            all_global.append(df)

        if not all_global:
            print("[경고] 통합 저장할 글로벌 검색량 데이터 없음")
            return

        output_path = self.raw_dir / config.ALL_COMPANIES_GLOBAL_TRENDS_FILE
        pd.concat(all_global, ignore_index=True).to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig",
        )
        print(f"[전체 글로벌 저장 완료] {output_path}")

    def run(self):
        self.collect_all_company_global_trends()
        self.save_aggregated_global_trends()

if __name__ == "__main__":
    collector = GlobalTrendCollector()
    collector.run()
