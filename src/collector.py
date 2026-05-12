import os
import time
import pandas as pd
import yfinance as yf
from pytrends.request import TrendReq
from datetime import datetime, timedelta

class DataCollector:
    """
    Yahoo Finance와 Google Trends로부터 데이터를 수집하는 클래스입니다.
    """
    def __init__(self, hl='en-US', tz=360):
        """
        DataCollector 초기화 메서드.
        
        Args:
            hl (str): Google Trends 검색 시 사용할 언어 설정 (기본값: 'en-US')
            tz (int): 타임존 설정 (기본값: 360, US Central Time 기준)
        """
        # pytrends 요청 객체 생성 (실패 시 재시도 횟수 및 백오프 설정 포함)
        self.pytrends = TrendReq(hl=hl, tz=tz, retries=2, backoff_factor=0.1)
        
    def fetch_financial_data(self, ticker, start_date, end_date):
        """
        Yahoo Finance로부터 특정 종목의 OHLCV(시가, 고가, 저가, 종가, 거래량) 데이터를 가져옵니다.
        
        Args:
            ticker (str): 주식 종목 코드 (예: 'AAPL', 'MSFT')
            start_date (str): 데이터 시작일 ('YYYY-MM-DD')
            end_date (str): 데이터 종료일 ('YYYY-MM-DD')
            
        Returns:
            pd.DataFrame: 수집된 주가 데이터 프레임 (실패 시 None 반환)
        """
        print(f"[{ticker}] 금융 데이터 수집 중...")
        try:
            # yfinance 라이브러리를 통해 데이터 다운로드
            df = yf.download(ticker, start=start_date, end=end_date)
            
            # 수집된 데이터가 비어있는지 확인
            if df.empty:
                print(f"경고: {ticker}에 대한 데이터가 존재하지 않습니다.")
                return None
            return df
        except Exception as e:
            print(f"에러 발생 (금융 데이터 수집): {e}")
            return None

    def fetch_search_trends(self, keyword, start_date, end_date):
        """
        Google Trends로부터 특정 키워드에 대한 검색 관심도 데이터를 수집합니다.
        
        Args:
            keyword (str): 검색어 (예: 'Apple', 'S&P 500')
            start_date (str): 검색 시작일 ('YYYY-MM-DD')
            end_date (str): 검색 종료일 ('YYYY-MM-DD')
            
        Returns:
            pd.DataFrame: 수집된 검색 트렌드 데이터 프레임 (실패 시 None 반환)
        """
        print(f"['{keyword}'] 검색 트렌드 데이터 수집 중...")
        try:
            # 기간 포맷 설정: 'YYYY-MM-DD YYYY-MM-DD'
            timeframe = f"{start_date} {end_date}"
            
            # Google Trends 페이로드 빌드
            self.pytrends.build_payload([keyword], timeframe=timeframe)
            
            # API 과부하 방지 및 '429 Too Many Requests' 에러 회피를 위한 대기 시간 추가
            time.sleep(2)
            
            # 시간 흐름에 따른 관심도 변화 데이터 추출
            df = self.pytrends.interest_over_time()
            
            if df.empty:
                print(f"경고: 키워드 '{keyword}'에 대한 트렌드 데이터가 없습니다.")
                return None
            
            # 'isPartial' 컬럼(데이터의 불완전성 여부 표시)이 있으면 제거하여 데이터 정제
            if 'isPartial' in df.columns:
                df = df.drop(columns=['isPartial'])
            return df
        except Exception as e:
            print(f"에러 발생 (검색 트렌드 수집): {e}")
            return None

    def collect_and_merge(self, ticker, keyword, start_date, end_date):
        """
        주가 데이터와 검색 트렌드 데이터를 각각 수집한 후, 날짜 인덱스를 기준으로 병합합니다.
        
        Args:
            ticker (str): 주식 종목 코드
            keyword (str): 검색어
            start_date (str): 수집 시작일
            end_date (str): 수집 종료일
            
        Returns:
            pd.DataFrame: 병합된 최종 데이터 프레임
        """
        # 1. 금융 데이터 수집
        fin_df = self.fetch_financial_data(ticker, start_date, end_date)
        
        # 2. 검색 트렌드 데이터 수집
        trend_df = self.fetch_search_trends(keyword, start_date, end_date)
        
        # 3. 데이터가 모두 성공적으로 수집되었을 경우 병합 진행
        if fin_df is not None and trend_df is not None:
            # 인덱스를 datetime 형식으로 변환하여 병합 준비
            fin_df.index = pd.to_datetime(fin_df.index)
            trend_df.index = pd.to_datetime(trend_df.index)
            
            # 내부 조인(Inner Join) 방식을 통해 두 데이터가 공통적으로 존재하는 날짜만 남김
            merged_df = pd.merge(fin_df, trend_df, left_index=True, right_index=True, how='inner')
            print(f"데이터 병합 완료. 총 {len(merged_df)}행의 데이터가 생성되었습니다.")
            return merged_df
            
        print("데이터 병합 실패: 한쪽 이상의 데이터를 가져오지 못했습니다.")
        return None

if __name__ == "__main__":
    # 클래스 기능 확인을 위한 샘플 테스트 코드
    collector = DataCollector()
    
    # 파라미터 예시
    TICKER = "AAPL"
    KEYWORD = "Apple"
    # 현재 날짜로부터 30일 전까지의 데이터 수집 예시
    START = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    END = datetime.now().strftime('%Y-%m-%d')
    
    # 테스트를 원할 경우 아래 주석을 해제하세요.
    # data = collector.collect_and_merge(TICKER, KEYWORD, START, END)
    # if data is not None:
    #     print(data.head())
    
    print("DataCollector 베이스 코드 준비 완료.")
