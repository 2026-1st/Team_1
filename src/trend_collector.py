import os
import time
from datetime import timedelta

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

    def _request_trend(self, keyword, start_date, end_date):
        """
        Google Trends에서 한 구간의 일간 검색 관심도를 요청
        """

        timeframe = f"{start_date.strftime('%Y-%m-%d')} {end_date.strftime('%Y-%m-%d')}"
        print(f"    - {keyword} / {timeframe}")

        time.sleep(config.PYTRENDS_WAIT_TIME)

        self.pytrends.build_payload(
            kw_list=[keyword],
            timeframe=timeframe,
            geo=config.GOOGLE_TRENDS_GEO,
            cat=config.GOOGLE_TRENDS_CAT,
        )

        df = self.pytrends.interest_over_time()

        if df is None or df.empty:
            return pd.DataFrame(columns=["Date", "trend"])

        df = df.reset_index()

        if "isPartial" in df.columns:
            df = df.drop(columns=["isPartial"])

        df = df.rename(
            columns={
                "date": "Date",
                keyword: "trend",
            }
        )

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["trend"] = pd.to_numeric(df["trend"], errors="coerce")
        df = df.dropna(subset=["Date", "trend"])

        return df[["Date", "trend"]]

    def _align_chunk_scale(self, previous_df, current_df):
        """
        Google Trends는 요청 구간마다 0~100으로 다시 정규화되므로,
        겹치는 날짜의 평균 비율로 다음 구간을 이전 구간 기준에 맞춤
        """

        overlap = pd.merge(
            previous_df,
            current_df,
            on="Date",
            how="inner",
            suffixes=("_prev", "_curr"),
        )

        overlap = overlap[
            (overlap["trend_prev"] > 0) &
            (overlap["trend_curr"] > 0)
        ]

        if overlap.empty:
            return current_df

        scale = (overlap["trend_prev"] / overlap["trend_curr"]).median()
        current_df = current_df.copy()
        current_df["trend"] = current_df["trend"] * scale

        return current_df

    def _complete_daily_dates(self, df, start_date, end_date):
        """
        전체 기간을 1일 단위로 맞추고 중간 결측은 선형 보간으로 채움
        """

        full_dates = pd.DataFrame({
            "Date": pd.date_range(start=start_date, end=end_date, freq="D")
        })

        if df.empty:
            full_dates["trend"] = pd.NA
            return full_dates

        df = (
            df
            .groupby("Date", as_index=False)["trend"]
            .mean()
            .sort_values("Date")
        )

        df = pd.merge(full_dates, df, on="Date", how="left")
        df["trend"] = df["trend"].interpolate(method="linear")
        df["trend"] = df["trend"].ffill().bfill()

        return df

    def fetch_daily_trend_by_chunks(
        self,
        keyword,
        start_date,
        end_date,
        chunk_days=None,
        overlap_days=None,
    ):
        """
        Google Trends 검색량을 90일 이하 구간으로 나눠 1일 단위로 수집.
        구간별 겹치는 날짜를 이용해 정규화 기준을 보정한 뒤,
        최종적으로 전체 날짜를 일 단위로 맞추고 결측값을 보간함.
        """

        all_chunks = []

        current_start = pd.to_datetime(start_date)
        final_end = pd.to_datetime(end_date)
        chunk_days = chunk_days or config.GOOGLE_TRENDS_CHUNK_DAYS
        overlap_days = overlap_days or config.GOOGLE_TRENDS_OVERLAP_DAYS

        if overlap_days >= chunk_days:
            raise ValueError("overlap_days must be smaller than chunk_days")

        while current_start <= final_end:
            current_end = min(current_start + timedelta(days=chunk_days), final_end)

            try:
                df = self._request_trend(keyword, current_start, current_end)

                if not df.empty and all_chunks:
                    previous_df = pd.concat(all_chunks, ignore_index=True)
                    df = self._align_chunk_scale(previous_df, df)

                if not df.empty:
                    all_chunks.append(df)

            except Exception as e:
                print(f"      [에러] {keyword}: {e}")

            if current_end >= final_end:
                break

            current_start = current_end - timedelta(days=overlap_days)

        if not all_chunks:
            return None

        result = pd.concat(all_chunks, ignore_index=True)
        result = self._complete_daily_dates(result, start_date, end_date)

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
                chunk_days=config.GOOGLE_TRENDS_CHUNK_DAYS,
                overlap_days=config.GOOGLE_TRENDS_OVERLAP_DAYS,
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
        save_path = os.path.join(config.GOOGLE_TRENDS_RAW_DIR, filename)

        df.to_csv(save_path, index=False, encoding="utf-8-sig")

        print(f"[저장 완료] {save_path}")

    def save_all_csv(self, all_data):
        if not all_data:
            print("[경고] 저장할 데이터 없음")
            return

        final_df = pd.concat(all_data, ignore_index=True)

        save_path = os.path.join(
            config.GOOGLE_TRENDS_RAW_DIR,
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
