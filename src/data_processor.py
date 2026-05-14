import os
import pandas as pd
from pathlib import Path
import config

class DataProcessor:
    def __init__(self):
        # 경로 설정
        self.raw_trend_dir = Path(config.GOOGLE_TRENDS_RAW_DIR)
        self.raw_stock_dir = Path(config.DATA_DIR) / "raw" / "stock"
        self.processed_dir = Path(config.PROCESSED_DATA_DIR)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        self.trend_path = self.processed_dir / "all_companies_trends_cleaned.csv"
        self.output_path = self.processed_dir / "all_companies_model_data.csv"

    def normalize_to_100(self, series: pd.Series) -> pd.Series:
        """검색량 지표를 0~100 범위로 재정규화"""
        series = pd.to_numeric(series, errors="coerce")
        max_value = series.max()
        if pd.isna(max_value) or max_value <= 0:
            return series.fillna(0)
        return (series / max_value * 100).clip(lower=0, upper=100)

    def long_flat_mask(self, series: pd.Series, min_run: int = 14) -> pd.Series:
        """반복 구간 마스크 생성"""
        values = series.reset_index(drop=True)
        groups = values.ne(values.shift()).cumsum()
        run_lengths = values.groupby(groups).transform("size")
        return run_lengths >= min_run

    def build_scaled_fallback(self, source: pd.Series, target: pd.Series) -> pd.Series:
        """보조 데이터를 활용한 대체값 생성"""
        source_norm = self.normalize_to_100(source)
        target_valid = target.dropna()
        if target_valid.empty:
            return source_norm
        target_min, target_max = target_valid.min(), target_valid.max()
        if target_max <= target_min:
            return source_norm
        return target_min + (source_norm / 100) * (target_max - target_min)

    def clean_global_trend(self, company_df: pd.DataFrame) -> pd.DataFrame:
        """글로벌 검색량 품질 보정"""
        df = company_df.copy()
        kor_col = "trend_kor" if "trend_kor" in df.columns else "trend_base"
        
        df[kor_col] = self.normalize_to_100(df[kor_col])
        df["trend_glb"] = self.normalize_to_100(df["trend_glb"])

        flat_mask = self.long_flat_mask(df["trend_glb"])
        fallback = self.build_scaled_fallback(df[kor_col], df["trend_glb"].mask(flat_mask))

        df.loc[flat_mask, "trend_glb"] = fallback.loc[flat_mask]
        df["trend_glb"] = df["trend_glb"].interpolate(method="linear").ffill().bfill()
        df["trend_glb"] = self.normalize_to_100(df["trend_glb"])
        return df

    def process_company_trends(self, ticker, kor_trend_all, glb_trend_all):
        """기업별 트렌드 병합 및 가중치 계산"""
        info = config.COMPANY_CONFIG[ticker]
        
        kor_df = kor_trend_all[kor_trend_all["ticker"] == ticker].copy()
        if kor_df.empty:
            return pd.DataFrame()

        glb_df = glb_trend_all[glb_trend_all["ticker"] == ticker].copy()
        if glb_df.empty:
            glb_df = kor_df[["Date", "trend_base"]].rename(columns={"trend_base": "trend_glb"})
        else:
            glb_df = glb_df[["Date", "trend"]].rename(columns={"trend": "trend_glb"})

        kor_df["Date"] = pd.to_datetime(kor_df["Date"])
        glb_df["Date"] = pd.to_datetime(glb_df["Date"])
        
        company_df = pd.merge(kor_df, glb_df, on="Date", how="left")
        company_df["trend_glb"] = company_df["trend_glb"].interpolate(method="linear").ffill().bfill()
        company_df = self.clean_global_trend(company_df)

        kor_col = "trend_kor" if "trend_kor" in company_df.columns else "trend_base"
        company_df["weighted_trend"] = (
            company_df["foreign_ratio"] * company_df["trend_glb"]
            + (1 - company_df["foreign_ratio"]) * company_df[kor_col]
        )
        return company_df

    def make_features(self, df):
        """머신러닝 피처 생성"""
        df = df.sort_values(["ticker", "Date"]).copy()
        df["return"] = df.groupby("ticker")["Close"].pct_change()
        df["return_lag1"] = df.groupby("ticker")["return"].shift(1)
        df["return_lag3_mean"] = df.groupby("ticker")["return"].transform(lambda x: x.rolling(3).mean())
        df["return_lag7_mean"] = df.groupby("ticker")["return"].transform(lambda x: x.rolling(7).mean())
        df["volume_change"] = df.groupby("ticker")["Volume"].pct_change()
        df["ma5"] = df.groupby("ticker")["Close"].transform(lambda x: x.rolling(5).mean())
        df["ma20"] = df.groupby("ticker")["Close"].transform(lambda x: x.rolling(20).mean())
        df["ma5_gap"] = (df["Close"] - df["ma5"]) / df["ma5"]
        df["ma20_gap"] = (df["Close"] - df["ma20"]) / df["ma20"]
        df["volatility_7"] = df.groupby("ticker")["return"].transform(lambda x: x.rolling(7).std())
        df["next_return"] = df.groupby("ticker")["return"].shift(-1)
        df["target"] = (df["next_return"] > 0).astype(int)
        return df

    def run(self):
        print("--- 1단계: 트렌드 데이터 전처리 ---")
        kor_path = self.raw_trend_dir / config.ALL_COMPANIES_TRENDS_KR_FILE
        glb_path = self.raw_trend_dir / config.ALL_COMPANIES_TRENDS_GLOBAL_FILE
        
        if not kor_path.exists() or not glb_path.exists():
            print("[에러] 수집된 트렌드 파일이 없습니다.")
            return

        kor_all, glb_all = pd.read_csv(kor_path), pd.read_csv(glb_path)
        all_trends = []
        for ticker in config.COMPANY_CONFIG.keys():
            df = self.process_company_trends(ticker, kor_all, glb_all)
            if not df.empty:
                all_trends.append(df)
                # 개별 기업별 정제된 트렌드 저장
                company_key = ticker.replace(".KS", "").replace(".KQ", "").lower()
                # config에서 가져온 티커 매핑을 활용하거나 단순 변환
                # 기존 파일명이 skhynix_trend_cleaned.csv 인 경우 등을 고려
                if ticker == "000660.KS": company_key = "skhynix"
                elif ticker == "012450.KS": company_key = "hanwha"
                elif ticker == "066570.KS": company_key = "lg"
                elif ticker == "035420.KS": company_key = "naver"
                elif ticker == "005380.KS": company_key = "hyundai"
                elif ticker == "005930.KS": company_key = "samsung"
                
                company_save_path = self.processed_dir / f"{company_key}_trend_cleaned.csv"
                df.to_csv(company_save_path, index=False, encoding="utf-8-sig")
                print(f"    [기업별 저장 완료] {company_save_path}")

        if not all_trends: return
        final_trend_df = pd.concat(all_trends, ignore_index=True)
        final_trend_df.to_csv(self.trend_path, index=False, encoding="utf-8-sig")

        print("--- 2단계: 주가 데이터 병합 및 피처 생성 ---")
        stock_path = self.raw_stock_dir / "all_companies_stock_raw.csv"
        if not stock_path.exists():
            print("[에러] 주가 파일이 없습니다.")
            return

        stock_all = pd.read_csv(stock_path)
        stock_all["Date"] = pd.to_datetime(stock_all["Date"])
        final_trend_df["Date"] = pd.to_datetime(final_trend_df["Date"])

        merged = pd.merge(final_trend_df, stock_all, on=["Date", "ticker"], how="inner")
        if merged.empty: return

        merged = self.make_features(merged).dropna()
        merged.to_csv(self.output_path, index=False, encoding="utf-8-sig")
        print(f"[최종 처리 완료] {self.output_path} (크기: {merged.shape})")

if __name__ == "__main__":
    processor = DataProcessor()
    processor.run()
