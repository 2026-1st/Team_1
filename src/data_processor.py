import os
import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta
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

    def get_reference_trading_days(self, start_date, end_date):
        """KOSPI 지수를 기준으로 실제 개장일 리스트를 가져옴"""
        print(f"    [참조 데이터 로드] KOSPI 지수(^KS11) 기준 개장일 확인...")
        # yfinance end is exclusive
        yf_end = (pd.to_datetime(end_date) + timedelta(days=1)).strftime("%Y-%m-%d")
        kospi = yf.download("^KS11", start=start_date, end=yf_end, progress=False)
        return kospi.index

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
        
        # 주가 수익률 관련 피처
        df["return"] = df.groupby("ticker")["Close"].pct_change()
        df["return_lag1"] = df.groupby("ticker")["return"].shift(1)
        df["return_lag3_mean"] = df.groupby("ticker")["return"].transform(lambda x: x.rolling(3).mean())
        df["return_lag7_mean"] = df.groupby("ticker")["return"].transform(lambda x: x.rolling(7).mean())
        
        # 거래량 및 변동성
        df["volume_change"] = df.groupby("ticker")["Volume"].pct_change()
        df["volatility_7"] = df.groupby("ticker")["return"].transform(lambda x: x.rolling(7).std())
        
        # 이동평균 및 갭
        df["ma5"] = df.groupby("ticker")["Close"].transform(lambda x: x.rolling(5).mean())
        df["ma20"] = df.groupby("ticker")["Close"].transform(lambda x: x.rolling(20).mean())
        df["ma5_gap"] = (df["Close"] - df["ma5"]) / df["ma5"]
        df["ma20_gap"] = (df["Close"] - df["ma20"]) / df["ma20"]
        
        # 트렌드(검색량) 관련 피처
        df["trend_lag1"] = df.groupby("ticker")["weighted_trend"].shift(1)
        df["trend_lag3_mean"] = df.groupby("ticker")["weighted_trend"].transform(lambda x: x.rolling(3).mean())
        df["trend_lag7_mean"] = df.groupby("ticker")["weighted_trend"].transform(lambda x: x.rolling(7).mean())
        df["trend_change"] = df.groupby("ticker")["weighted_trend"].pct_change()
        
        # 티커 인코딩 (단순 팩토리얼 인코딩)
        df["ticker_encoded"] = df["ticker"].astype("category").cat.codes
        
        # 타겟 설정 (다음날 수익률이 양수이면 1, 아니면 0)
        df["next_return"] = df.groupby("ticker")["return"].shift(-1)
        df["target"] = (df["next_return"] > 0).astype(int)
        
        return df

    def run(self):
        print("--- 1단계: 트렌드 데이터 전처리 ---")
        kor_path = self.raw_trend_dir / config.ALL_COMPANIES_TRENDS_KR_FILE
        glb_path = self.raw_trend_dir / config.ALL_COMPANIES_TRENDS_GLOBAL_FILE
        
        if not kor_path.exists() or not glb_path.exists():
            print("[주의] 수집된 원본 트렌드 파일이 일부 없습니다. 기존 정제된 파일을 확인합니다.")
            if self.trend_path.exists():
                print(f"[정보] 기존 정제된 트렌드 파일을 사용합니다: {self.trend_path}")
                final_trend_df = pd.read_csv(self.trend_path)
            else:
                print("[에러] 정제된 트렌드 파일도 없습니다. 처리를 중단합니다.")
                return
        else:
            kor_all, glb_all = pd.read_csv(kor_path), pd.read_csv(glb_path)
            all_trends = []
            for ticker in config.COMPANY_CONFIG.keys():
                df = self.process_company_trends(ticker, kor_all, glb_all)
                if not df.empty:
                    all_trends.append(df)
                    # 개별 기업별 정제된 트렌드 저장
                    company_key = ticker.replace(".KS", "").replace(".KQ", "").lower()
                    if ticker == "000660.KS": company_key = "skhynix"
                    elif ticker == "012450.KS": company_key = "hanwha"
                    elif ticker == "066570.KS": company_key = "lg"
                    elif ticker == "035420.KS": company_key = "naver"
                    elif ticker == "005380.KS": company_key = "hyundai"
                    elif ticker == "005930.KS": company_key = "samsung"
                    
                    company_save_path = self.processed_dir / f"{company_key}_trend_cleaned.csv"
                    df.to_csv(company_save_path, index=False, encoding="utf-8-sig")
                    print(f"    [기업별 저장 완료] {company_save_path}")

            if not all_trends: 
                print("[에러] 처리된 트렌드 데이터가 없습니다.")
                return
            final_trend_df = pd.concat(all_trends, ignore_index=True)
            final_trend_df.to_csv(self.trend_path, index=False, encoding="utf-8-sig")

        print("--- 2단계: 주가 데이터 병합 및 피처 생성 ---")
        # 개별 주가 파일들을 모두 읽어서 합침
        stock_files = list(self.raw_stock_dir.glob("*_raw.csv"))
        # 통합 파일은 제외
        stock_files = [f for f in stock_files if f.name != "all_companies_stock_raw.csv"]
        
        if not stock_files:
            print("[에러] 주가 파일이 없습니다.")
            return

        all_stocks_list = []
        for f in stock_files:
            print(f"    [주가 로드] {f.name}")
            df = pd.read_csv(f)
            if df.empty:
                continue
            
            # ticker 컬럼이 없는 경우 파일명에서 추출
            if "ticker" not in df.columns:
                ticker = f.name.replace("_raw.csv", "").replace("_KS", ".KS").replace("_KQ", ".KQ").replace("_stock", "")
                df["ticker"] = ticker
            
            # 티커 표준화
            df["ticker"] = df["ticker"].str.replace("_KS", ".KS").str.replace("_KQ", ".KQ")
            
            # 기존에 trend 컬럼이 있다면 제거 (정제된 트렌드 데이터를 사용할 것이므로)
            if "trend" in df.columns:
                df = df.drop(columns=["trend"])
                
            all_stocks_list.append(df)
        
        stock_all_raw = pd.concat(all_stocks_list, ignore_index=True)
        stock_all_raw["Date"] = pd.to_datetime(stock_all_raw["Date"])

        # 영업일 기준 누락 데이터 보정 (KOSPI 지수 기준)
        ref_days = self.get_reference_trading_days(config.START_DATE, config.END_DATE)
        
        corrected_stocks = []
        for ticker in stock_all_raw["ticker"].unique():
            ticker_df = stock_all_raw[stock_all_raw["ticker"] == ticker].copy()
            ticker_df = ticker_df.set_index("Date").reindex(ref_days)
            
            # 누락된 값 채우기 (가격은 전날값(ffill), 거래량은 0)
            ticker_df["ticker"] = ticker_df["ticker"].fillna(ticker)
            ticker_df[["Close", "High", "Low", "Open"]] = ticker_df[["Close", "High", "Low", "Open"]].ffill().bfill()
            ticker_df["Volume"] = ticker_df["Volume"].fillna(0)
            
            corrected_stocks.append(ticker_df.reset_index().rename(columns={"index": "Date"}))
        
        stock_all = pd.concat(corrected_stocks, ignore_index=True)
        final_trend_df["Date"] = pd.to_datetime(final_trend_df["Date"])

        merged = pd.merge(final_trend_df, stock_all, on=["Date", "ticker"], how="inner")
        if merged.empty: 
            print("[에러] 트렌드와 주가 데이터 병합 결과가 비어있습니다.")
            return

        merged = self.make_features(merged).dropna()
        merged.to_csv(self.output_path, index=False, encoding="utf-8-sig")
        print(f"[최종 처리 완료] {self.output_path} (크기: {merged.shape})")

if __name__ == "__main__":
    processor = DataProcessor()
    processor.run()
