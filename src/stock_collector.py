import pandas as pd
import yfinance as yf
from pathlib import Path
import config

class StockDataCollector:
    def __init__(self):
        self.raw_dir = Path(config.DATA_DIR) / "raw" / "stock"
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def fetch_stock_data(self, ticker, start_date, end_date):
        """Yahoo Finance에서 주가 데이터 수집"""
        print(f"[주가 수집 시작] {ticker} ({start_date} ~ {end_date})")

        stock = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
        )

        if stock.empty:
            print(f"[경고] 주가 데이터 없음: {ticker}")
            return pd.DataFrame()

        # MultiIndex 컬럼 처리 (yfinance 최신 버전 대응)
        if isinstance(stock.columns, pd.MultiIndex):
            stock.columns = stock.columns.get_level_values(0)

        stock = stock.reset_index()
        stock["Date"] = pd.to_datetime(stock["Date"])
        stock["ticker"] = ticker

        return stock

    def save_stock_data(self, df, ticker):
        """수집된 주가 데이터를 CSV로 저장"""
        if df.empty:
            return
        
        safe_ticker = ticker.replace(".", "_")
        save_path = self.raw_dir / f"{safe_ticker}_stock_raw.csv"
        df.to_csv(save_path, index=False, encoding="utf-8-sig")
        print(f"[주가 저장 완료] {save_path}")

    def run(self):
        """설정된 모든 기업의 주가 데이터 수집 및 저장"""
        all_stocks = []
        
        # 트렌드 데이터의 기간과 맞추기 위해 config의 날짜 사용
        # 다음날 수익률(target) 계산을 위해 종료일 +1일 처리
        start_date = config.START_DATE
        end_date = (pd.to_datetime(config.END_DATE) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

        for ticker in config.COMPANY_CONFIG.keys():
            df = self.fetch_stock_data(ticker, start_date, end_date)
            if not df.empty:
                self.save_stock_data(df, ticker)
                all_stocks.append(df)

        if all_stocks:
            final_df = pd.concat(all_stocks, ignore_index=True)
            combined_path = self.raw_dir / "all_companies_stock_raw.csv"
            final_df.to_csv(combined_path, index=False, encoding="utf-8-sig")
            print(f"\n[전체 주가 저장 완료] {combined_path}")

if __name__ == "__main__":
    collector = StockDataCollector()
    collector.run()
