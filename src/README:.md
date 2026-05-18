# 소스 코드 (`src/`)

이 디렉토리는 주가 방향 예측 프로젝트의 실행 가능한 소스 코드를 포함합니다.

## 주요 모듈

### 1. `collector.py`
외부 API를 통해 데이터를 수집하는 역할을 담당합니다.
- **`DataCollector` 클래스**:
    - `fetch_financial_data(ticker, start_date, end_date)`: `yfinance`를 사용하여 Yahoo Finance로부터 OHLCV(시가, 고가, 저가, 종가, 거래량) 데이터를 다운로드합니다.
    - `fetch_search_trends(keyword, start_date, end_date)`: `pytrends`를 사용하여 Google Trends의 검색 관심도 데이터를 가져옵니다. API 속도 제한(Rate Limiting)을 방지하기 위한 지연 시간이 포함되어 있습니다.
    - `collect_and_merge(ticker, keyword, start_date, end_date)`: 주가 데이터와 검색 트렌드 데이터를 모두 수집한 후, 날짜 인덱스를 기준으로 병합(Inner Join)합니다.

## 사용 예시

```python
from src.collector import DataCollector

# 수집기 초기화
collector = DataCollector()

# Apple(AAPL) 주가 데이터 및 "Apple" 검색 트렌드 수집 및 병합
df = collector.collect_and_merge(
    ticker="AAPL", 
    keyword="Apple", 
    start_date="2023-01-01", 
    end_date="2023-12-31"
)

if df is not None:
    print(df.info())
    # 수집된 데이터를 raw 디렉토리에 저장
    df.to_csv("data/raw/aapl_data.csv")
```

## 개발 표준
- 모든 파이썬 코드는 PEP 8 표준을 따릅니다.
- API 호출 함수는 반드시 예외 처리(Error Handling)와 속도 제한 고려 사항을 포함해야 합니다.
- 새로운 함수나 클래스를 추가할 경우, 상세한 Docstring을 작성하여 문서화합니다.
