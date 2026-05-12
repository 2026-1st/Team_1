import os
import time
import pandas as pd
import yfinance as yf
from pytrends.request import TrendReq
from datetime import datetime, timedelta
import src.config as config

class DataCollector:
    """
    Yahoo Finance와 Google Trends로부터 데이터를 수집하는 클래스입니다.
    src/config.py의 설정을 기반으로 동작하며, API 속도 제한(429 Error)을 고려하여 설계되었습니다.
    """
    def __init__(self, hl=config.GOOGLE_TRENDS_HL, tz=config.GOOGLE_TRENDS_TZ):
        """
        DataCollector 초기화 메서드.
        
        Args:
            hl (str): Google Trends 검색 시 사용할 언어 설정 (config.py에서 로드)
            tz (int): 타임존 설정 (config.py에서 로드)
        """
        # pytrends 요청 객체 생성 
        # config에 정의된 retries와 backoff_factor를 사용하여 429 에러 발생 시 자동 재시도
        self.pytrends = TrendReq(
            hl=hl, 
            tz=tz, 
            retries=config.PYTRENDS_RETRIES, 
            backoff_factor=config.PYTRENDS_BACKOFF_FACTOR
        )
        
    def fetch_financial_data(self, ticker, start_date, end_date):
        """
        Yahoo Finance로부터 특정 종목의 OHLCV 데이터를 수집합니다.
        
        Args:
            ticker (str): 주식 종목 코드
            start_date (str): 데이터 시작일
            end_date (str): 데이터 종료일
            
        Returns:
            pd.DataFrame: 수집된 주가 데이터 프레임
        """
        print(f"[{ticker}] 금융 데이터 수집 중...")
        try:
            # yfinance를 통해 데이터 다운로드
            df = yf.download(ticker, start=start_date, end=end_date)
            
            if df is None or df.empty:
                print(f"경고: {ticker}에 대한 데이터가 존재하지 않습니다.")
                return None
            
            # yfinance 최신 버전의 MultiIndex 컬럼 구조 단순화
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            return df
        except Exception as e:
            print(f"에러 발생 (금융 데이터 수집): {e}")
            return None

    def fetch_search_trends(self, keyword, start_date, end_date):
        """
        Google Trends로부터 키워드 검색 관심도 데이터를 수집합니다.
        속도 제한을 피하기 위해 요청 전/후로 대기 시간을 가집니다.
        
        Args:
            keyword (str): 검색어
            start_date (str): 검색 시작일
            end_date (str): 검색 종료일
            
        Returns:
            pd.DataFrame: 수집된 검색 트렌드 데이터 프레임
        """
        print(f"['{keyword}'] 검색 트렌드 데이터 수집 중...")
        try:
            # 기간 포맷: 'YYYY-MM-DD YYYY-MM-DD'
            timeframe = f"{start_date} {end_date}"
            
            # API 요청 전 대기 (속도 제한 회피)
            time.sleep(config.PYTRENDS_WAIT_TIME)
            
            # Google Trends 페이로드 빌드 및 데이터 수집
            self.pytrends.build_payload([keyword], timeframe=timeframe)
            df = self.pytrends.interest_over_time()
            
            if df is None or df.empty:
                print(f"경고: 키워드 '{keyword}'에 대한 트렌드 데이터가 없습니다.")
                # 트렌드 데이터가 없을 경우 0으로 채워진 데이터프레임 반환을 고려할 수 있으나,
                # 여기서는 None을 반환하여 수집 실패를 알림
                return None
            
            # 불필요한 isPartial 컬럼 제거
            if 'isPartial' in df.columns:
                df = df.drop(columns=['isPartial'])
            
            # 검색량 컬럼명을 'trend'로 통일 (여러 키워드 처리 시 유용)
            df = df.rename(columns={keyword: 'trend'})
            
            return df
        except Exception as e:
            print(f"에러 발생 (검색 트렌드 수집): {e}")
            return None

    def collect_and_merge(self, ticker, keyword, start_date, end_date):
        """
        금융 데이터와 검색 트렌드 데이터를 수집하여 날짜 기준으로 병합합니다.
        
        Returns:
            pd.DataFrame: 병합된 최종 데이터 프레임
        """
        fin_df = self.fetch_financial_data(ticker, start_date, end_date)
        trend_df = self.fetch_search_trends(keyword, start_date, end_date)
        
        if fin_df is not None and trend_df is not None:
            # 인덱스를 datetime으로 통일
            fin_df.index = pd.to_datetime(fin_df.index)
            trend_df.index = pd.to_datetime(trend_df.index)
            
            # 교집합(inner) 기준으로 병합
            merged_df = pd.merge(fin_df, trend_df, left_index=True, right_index=True, how='inner')
            print(f"데이터 병합 성공: {ticker} ({len(merged_df)} rows)")
            return merged_df
            
        print("데이터 병합 실패: 데이터 수집 단계를 확인하세요.")
        return None

    def save_data(self, df, ticker):
        """
        수집된 데이터를 CSV 파일로 저장합니다.
        """
        if df is not None:
            filename = f"{ticker}_raw.csv"
            save_path = os.path.join(config.RAW_DATA_DIR, filename)
            df.to_csv(save_path)
            print(f"데이터가 저장되었습니다: {save_path}")

if __name__ == "__main__":
    # 설정값 로드
    collector = DataCollector()
    
    # config.py에 정의된 모든 종목에 대해 수집 실행
    for ticker, keyword in config.TICKER_CONFIG.items():
        data = collector.collect_and_merge(
            ticker, 
            keyword, 
            config.START_DATE, 
            config.END_DATE
        )
        
        if data is not None:
            collector.save_data(data, ticker)
            print(data.head())
        
        # 종목 간 수집 시에도 충분한 대기 시간 부여
        print(f"다음 종목 수집 전 대기 중... ({config.PYTRENDS_WAIT_TIME}s)")
        time.sleep(config.PYTRENDS_WAIT_TIME)

