import os
import time
from datetime import datetime, timedelta

import pandas as pd
from pytrends.request import TrendReq

import config


class GoogleTrendsCollector:
    def __init__(self):
        self.pytrends = TrendReq(
            hl=config.GOOGLE_TRENDS_HL,
            tz=config.GOOGLE_TRENDS_TZ,
            retries=config.PYTRENDS_RETRIES,
            backoff_factor=config.PYTRENDS_BACKOFF_FACTOR,
        )

    def fetch_daily_trend_by_chunks(self, keyword, start_date, end_date, chunk_days=7):
        """
        Google Trends 검색량을 30일 단위로 나눠 일간 데이터 형태로 수집
        """

        all_chunks = []

        current_start = pd.to_datetime(start_date)
        final_end = pd.to_datetime(end_date)

        while current_start < final_end:
            current_end = min(current_start + timedelta(days=chunk_days), final_end)

            timeframe = f"{current_start.strftime('%Y-%m-%d')} {current_end.strftime('%Y-%m-%d')}"

            print(f"    - {keyword} / {timeframe}")

            try:
                time.sleep(20)

                self.pytrends.build_payload(
                    kw_list=[keyword],
                    timeframe=timeframe,
                    geo=config.GOOGLE_TRENDS_GEO,
                    cat=config.GOOGLE_TRENDS_CAT,
                )

                df = self.pytrends.interest_over_time()

                if df is None or df.empty:
                    current_start = current_end
                    continue

                df = df.reset_index()

                if "isPartial" in df.columns:
                    df = df.drop(columns=["isPartial"])

                df = df.rename(
                    columns={
                        "date": "Date",
                        keyword: "trend",
                    }
                )

                df["Date"] = pd.to_datetime(df["Date"])
                all_chunks.append(df[["Date", "trend"]])

            except Exception as e:
                print(f"      [에러] {keyword}: {e}")

            current_start = current_end

        if not all_chunks:
            return None

        result = pd.concat(all_chunks, ignore_index=True)
        result = result.drop_duplicates(subset=["Date"])
        result = result.sort_values("Date")

        return result

    def collect_company_trends(self, ticker, company_info):
        company_name = company_info["company_name"]
        foreign_ratio = company_info["foreign_ratio"]
        keywords = company_info["keywords"]

        print("=" * 60)
        print(f"[수집 시작] {company_name} / {ticker}")
        print("=" * 60)

        company_df = None

        for keyword_type, keyword in keywords.items():
            trend_df = self.fetch_daily_trend_by_chunks(
                keyword=keyword,
                start_date=config.START_DATE,
                end_date=config.END_DATE,
                chunk_days=90,
            )

            if trend_df is None:
                print(f"    [스킵] {keyword} 데이터 없음")
                continue

            trend_col = f"trend_{keyword_type}"
            weighted_col = f"weighted_trend_{keyword_type}"

            trend_df = trend_df.rename(columns={"trend": trend_col})
            trend_df[weighted_col] = trend_df[trend_col] * foreign_ratio

            if company_df is None:
                company_df = trend_df
            else:
                company_df = pd.merge(
                    company_df,
                    trend_df,
                    on="Date",
                    how="outer",
                )

        if company_df is None:
            return None

        company_df["ticker"] = ticker
        company_df["company_name"] = company_name
        company_df["foreign_ratio"] = foreign_ratio

        company_df = company_df.sort_values("Date")

        return company_df

    def save_company_csv(self, df, ticker):
        safe_ticker = ticker.replace(".", "_")
        filename = f"{safe_ticker}_google_trends_daily.csv"
        save_path = os.path.join(config.RAW_DATA_DIR, filename)

        df.to_csv(save_path, index=False, encoding="utf-8-sig")

        print(f"[저장 완료] {save_path}")

    def save_all_csv(self, all_data):
        if not all_data:
            print("[경고] 저장할 데이터 없음")
            return

        final_df = pd.concat(all_data, ignore_index=True)

        save_path = os.path.join(
            config.RAW_DATA_DIR,
            "all_companies_google_trends_daily.csv",
        )

        final_df.to_csv(save_path, index=False, encoding="utf-8-sig")

        print(f"[전체 저장 완료] {save_path}")
        print(f"[전체 행 수] {len(final_df)}")

    def run(self):
        all_data = []

        for ticker, company_info in config.COMPANY_CONFIG.items():
            df = self.collect_company_trends(ticker, company_info)

            if df is not None:
                self.save_company_csv(df, ticker)
                all_data.append(df)

            print(f"다음 기업 수집 전 대기 중... {config.PYTRENDS_WAIT_TIME}초")
            time.sleep(config.PYTRENDS_WAIT_TIME)

        self.save_all_csv(all_data)


if __name__ == "__main__":
    collector = GoogleTrendsCollector()
    collector.run()