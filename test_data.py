import pandas as pd
import yfinance as yf
from pytrends.request import TrendReq
from datetime import datetime, timedelta

# Mocking config for a quick check
START_DATE = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
END_DATE = datetime.now().strftime('%Y-%m-%d')
TICKER = "005930.KS"
KEYWORD = "삼성전자"

print(f"Fetching data for {TICKER} and {KEYWORD} from {START_DATE} to {END_DATE}")

# Fetch financial data
fin_df = yf.download(TICKER, start=START_DATE, end=END_DATE)
print("\nFinancial Data (first 5 rows):")
print(fin_df.head())
print(f"Financial Data Index Type: {type(fin_df.index)}")
print(f"Financial Data Index Name: {fin_df.index.name}")

# Fetch trend data
pytrends = TrendReq(hl='ko-KR', tz=540)
timeframe = f"{START_DATE} {END_DATE}"
pytrends.build_payload([KEYWORD], timeframe=timeframe)
trend_df = pytrends.interest_over_time()
print("\nTrend Data (first 5 rows):")
print(trend_df.head())
print(f"Trend Data Index Type: {type(trend_df.index)}")
print(f"Trend Data Index Name: {trend_df.index.name}")

if not trend_df.empty:
    # Try merging
    fin_df.index = pd.to_datetime(fin_df.index)
    trend_df.index = pd.to_datetime(trend_df.index)
    
    # Normalize index to date only
    fin_df.index = fin_df.index.normalize()
    trend_df.index = trend_df.index.normalize()
    
    merged_df = pd.merge(fin_df, trend_df, left_index=True, right_index=True, how='inner')
    print("\nMerged Data (first 5 rows):")
    print(merged_df.head())
    print(f"Merged Data Rows: {len(merged_df)}")
else:
    print("\nTrend Data is empty.")
