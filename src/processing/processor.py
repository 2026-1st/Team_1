import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
from sklearn.preprocessing import StandardScaler

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import config, helpers

class DataProcessor:
    def __init__(self):
        self.raw_stock_path = config.STOCK_RAW_DIR / "all_companies_stock_raw.csv"
        self.raw_trend_path = config.TREND_RAW_DIR / "all_companies_google_trends_daily.csv"
        self.raw_global_path = config.TREND_RAW_DIR / "all_companies_global_trends.csv"
        self.scaler = StandardScaler()

    def load_data(self):
        print("--- [1/5] 데이터 로드 중 ---")
        stock_df = pd.read_csv(self.raw_stock_path)
        trend_df = pd.read_csv(self.raw_trend_path)
        global_df = pd.read_csv(self.raw_global_path)

        # Date 변환
        for df in [stock_df, trend_df, global_df]:
            df['Date'] = pd.to_datetime(df['Date'])
            df.sort_values(['Date', 'ticker'], inplace=True)

        return stock_df, trend_df, global_df

    def merge_data(self, stock_df, trend_df, global_df):
        print("--- [2/5] 데이터 병합 중 ---")
        # Global trend column rename to avoid conflict
        global_df = global_df.rename(columns={'trend': 'trend_glb'})
        
        # Merge local trend and global trend
        trends = pd.merge(trend_df, global_df[['Date', 'ticker', 'trend_glb']], on=['Date', 'ticker'], how='left')
        
        # Merge with stock data
        df = pd.merge(stock_df, trends, on=['Date', 'ticker'], how='inner')
        return df

    def engineer_features(self, df):
        print("--- [3/5] 피처 엔지니어링 중 (100+ 후보 생성) ---")
        df = df.sort_values(['ticker', 'Date'])
        
        # 1. Price Features
        df['return'] = df.groupby('ticker')['Close'].pct_change()
        df['volatility_7'] = df.groupby('ticker')['return'].transform(lambda x: x.rolling(7).std())
        df['rolling_std_5'] = df.groupby('ticker')['Close'].transform(lambda x: x.rolling(5).std())
        
        for window in [5, 20]:
            ma = df.groupby('ticker')['Close'].transform(lambda x: x.rolling(window).mean())
            df[f'ma{window}_gap'] = (df['Close'] - ma) / ma

        # 2. Technical Indicators
        df['rsi_5'] = df.groupby('ticker')['Close'].transform(lambda x: helpers.calculate_rsi(x, 5))
        df['rsi_14'] = df.groupby('ticker')['Close'].transform(lambda x: helpers.calculate_rsi(x, 14))
        df['macd_hist'] = df.groupby('ticker')['Close'].transform(lambda x: helpers.calculate_macd(x))
        
        bb_upper, bb_lower = helpers.calculate_bollinger_bands(df['Close'])
        df['bb_high_gap'] = (df['Close'] - bb_upper) / bb_upper
        df['bb_low_gap'] = (df['Close'] - bb_lower) / bb_lower

        # 3. Trend Features
        # Weighted trend: trend_base(0.4) + trend_stock(0.3) + trend_forecast(0.3)
        df['weighted_trend'] = (df['trend_base'] * 0.4 + 
                                df['trend_stock'] * 0.3 + 
                                df['trend_forecast'] * 0.3)
        
        for i in range(1, 4):
            df[f'trend_lag{i}'] = df.groupby('ticker')['weighted_trend'].shift(i)
            df[f'return_lag{i}'] = df.groupby('ticker')['return'].shift(i)
            
        df['trend_lag3_mean'] = df.groupby('ticker')['weighted_trend'].transform(lambda x: x.rolling(3).mean())
        df['trend_lag7_mean'] = df.groupby('ticker')['weighted_trend'].transform(lambda x: x.rolling(7).mean())
        df['trend_change'] = df.groupby('ticker')['weighted_trend'].pct_change()
        
        # Trend Shock
        ma7_trend = df.groupby('ticker')['weighted_trend'].transform(lambda x: x.rolling(7).mean())
        df['trend_shock'] = (df['weighted_trend'] > ma7_trend * 2.0).astype(int)
        
        # Geo-Spread
        df['kor_glb_spread'] = df['weighted_trend'] - df['trend_glb']
        
        # Interaction
        df['trend_ma_interaction'] = df['weighted_trend'] * df['ma5_gap']

        # 4. Market Dynamics & Rank
        df['volume_change'] = df.groupby('ticker')['Volume'].pct_change()
        df['date_trend_rank'] = df.groupby('Date')['weighted_trend'].rank(pct=True)
        df['date_return_rank'] = df.groupby('Date')['return'].rank(pct=True)

        # 5. Entity Identity
        df['ticker_encoded'] = pd.factorize(df['ticker'])[0]

        # 6. Target Labeling
        df['next_return'] = df.groupby('ticker')['Close'].shift(-1).pct_change(fill_method=None) # Correct next day return
        # Actually next_return should be (Close(t+1) - Close(t)) / Close(t)
        df['next_return'] = df.groupby('ticker')['Close'].shift(-1) / df['Close'] - 1
        df['target'] = (df['next_return'] > 0).astype(int)
        df['target_lag1'] = df.groupby('ticker')['target'].shift(1)

        # Handle Inf and Missing
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.ffill(inplace=True)
        df.bfill(inplace=True)
        df.dropna(inplace=True)

        return df

    def normalize_and_save(self, df):
        print("--- [4/5] 정규화 및 이상치 처리 중 ---")
        
        # Features to normalize (exclude non-numeric and targets)
        exclude = ['Date', 'ticker', 'company_name', 'next_return', 'target']
        features = [c for c in df.columns if c not in exclude]
        
        # Outlier Clipping
        for col in features:
            if df[col].dtype in [np.float64, np.int64]:
                df[col] = helpers.winsorize_series(df[col])

        # Mandatory Normalization (StandardScaler)
        df[features] = self.scaler.fit_transform(df[features])
        
        print("--- [5/5] 최종 데이터 저장 중 ---")
        save_path = config.DATA_PROCESSED_DIR / "processed_model_data.csv"
        df.to_csv(save_path, index=False)
        print(f"저장 완료: {save_path}")
        return df

    def run(self):
        stock_df, trend_df, global_df = self.load_data()
        df = self.merge_data(stock_df, trend_df, global_df)
        df = self.engineer_features(df)
        df = self.normalize_and_save(df)
        return df

if __name__ == "__main__":
    processor = DataProcessor()
    processor.run()
