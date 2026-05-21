# src

주가 방향 예측 프로젝트의 데이터 수집과 전처리 코드를 관리합니다.

## 주요 파일

### `config.py`

공통 설정 파일입니다.

- 분석 대상 기업, 티커, 검색 키워드, 외국인 비율을 관리합니다.
- Google Trends 수집 기간, 지역, 카테고리, 요청 간격을 설정합니다.
- 글로벌 검색량 CSV 파일명과 저장 경로를 관리합니다.

### `trend_collector.py`

Google Trends 일간 검색량을 수집하는 공통 수집기입니다.

- 긴 기간을 90일 이하 구간으로 나눠 일간 데이터를 수집합니다.
- 구간별 0~100 정규화 차이를 줄이기 위해 겹치는 날짜를 기준으로 스케일을 보정합니다.
- 수집 후 전체 날짜를 1일 단위로 맞추고, 결측값은 선형 보간과 앞뒤 채움으로 처리합니다.
- 최종 검색량은 0~100 범위로 재정규화합니다.

### `collect_global_trends.py`

6개 기업의 글로벌 Google Trends 검색량을 수집합니다.

실행 시 `config.GOOGLE_TRENDS_GEO`를 임시로 빈 문자열(`""`)로 바꿔 글로벌 기준 검색량을 요청하고, 작업이 끝나면 원래 설정값으로 복구합니다.

처리 흐름:

1. `GoogleTrendsCollector`를 생성합니다.
2. `config.COMPANY_CONFIG`에 등록된 기업을 순회합니다.
3. 각 기업의 기본 검색어(`keywords["base"]`)로 글로벌 검색량을 수집합니다.
4. 기업별 글로벌 검색량 CSV를 `data/raw/google_trends`에 저장합니다.
5. 기업별 CSV를 다시 읽어 `all_companies_global_trends.csv`로 통합 저장합니다.

생성 파일:

```text
data/raw/google_trends/samsung_global.csv
data/raw/google_trends/skhynix_global.csv
data/raw/google_trends/naver_global.csv
data/raw/google_trends/hanwha_global.csv
data/raw/google_trends/lg_global.csv
data/raw/google_trends/hyundai_global.csv
data/raw/google_trends/all_companies_global_trends.csv
```

실행:

```bash
python collect_global_trends.py
```

### `data_processor.py`

한국 검색량, 글로벌 검색량, 주가 데이터를 모델 학습용 데이터로 병합합니다.

- 한국 검색량 raw CSV를 `trend_kor`로 정리합니다.
- 글로벌 검색량 raw CSV를 `trend_glb`로 정리합니다.
- `trend_glb`가 100을 넘지 않도록 재정규화합니다.
- 긴 동일값 반복 구간은 수집 실패 가능성이 큰 구간으로 보고 보완합니다.
- `weighted_trend`를 아래 식으로 계산합니다.

```text
weighted_trend = foreign_ratio * trend_glb + (1 - foreign_ratio) * trend_kor
```

- Yahoo Finance 주가 데이터를 수집해 검색량 데이터와 병합합니다.
- 수익률, 이동평균, 변동성, 다음날 상승 여부(`target`)를 생성합니다.

실행:

```bash
python data_processor.py
```

## 출력 데이터

```text
data/processed/*_trend_cleaned.csv
data/processed/all_companies_trends_cleaned.csv
data/processed/all_companies_model_data.csv
```

`all_companies_trends_cleaned.csv` 주요 컬럼:

```text
Date
trend_kor
trend_glb
ticker
company_name
foreign_ratio
weighted_trend
```
### `collector.py`
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


## 주의 사항

- Google Trends는 요청 제한이 있어 `429 too many requests`가 발생할 수 있습니다.
- 수집 실패 구간은 전처리 단계에서 보간 또는 보완될 수 있습니다.
- CSV 파일이 Excel이나 IDE에서 열려 있으면 Windows에서 덮어쓰기가 실패할 수 있습니다.
