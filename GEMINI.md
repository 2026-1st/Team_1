# 🧬 [PROJECT BIBLE] 검색 관심도 기반 주가 방향 예측 시스템

> **CORE DIRECTIVE:** `data/raw/` 내의 원본 데이터를 기점으로 전체 파이프라인을 무(無)에서 재구축한다. 본 문서는 프로젝트의 유일한 진실(Source of Truth)이며, 모든 코드 구현의 기준이 된다.

---

## 1. 🏗️ 시스템 아키텍처 (New Architecture)

모든 소스 코드는 `src/` 하위에 모듈화되어야 하며, 상호 의존성을 최소화한다.

```text
Team_1/
├── data/
│   ├── raw/                  # [PERMANENT] 원본 주가 및 트렌드 데이터
│   └── processed/            # [GENERATED] 전처리/피처셋/정규화 데이터
├── src/
│   ├── utils/
│   │   ├── config.py         # 하이퍼파라미터, 티커, 경로 전역 설정
│   │   └── helpers.py        # 보조 수식 (RSI, MACD, 벡터 연산 등)
│   ├── processing/
│   │   ├── processor.py      # 데이터 병합, 100+ 피처 생성, [Mandatory] 정규화
│   │   └── selector.py       # XGBoost 중요도 기반 변수 선택 (Top 20-25)
│   ├── models/
│   │   ├── classifier.py     # RF, XGBoost, LR 앙상블 학습 엔진
│   │   └── evaluator.py      # TimeSeriesSplit 기반 검증 및 다각적 분석
│   └── main.py               # 오케스트레이션 (End-to-End 실행)
├── models/                   # 학습 완료된 모델 바이너리 (.joblib)
├── reports/                  # 분석 결과물 (Figures, Multi-metric CSV)
└── GEMINI.md                 # [본 파일] 프로젝트 마스터 가이드
```

---

## 2. 🛡️ 전처리 필수 수칙 (Critical Guardrails)

데이터의 신뢰성과 모델 성능을 보장하기 위해 전처리 시 아래 사항을 **반드시** 준수해야 합니다.

### A. [Mandatory] 정규화 및 스케일링 (Normalization)
- **방법:** `StandardScaler` (Z-score) 또는 `RobustScaler` (이상치 강한 경우) 적용.
- **원칙:** **Fit on Train, Transform on Test.** 테스트 데이터의 정보가 학습 과정에 유출(Data Leakage)되지 않도록 엄격히 관리.
- **대상:** 모든 수치형 피처. 종목별(Ticker-wise)로 스케일링할지, 전체 데이터를 한꺼번에 할지 실험 시 명시.

### B. 이상치 및 결측치 처리 (Outliers & Missing Values)
- **결측치(NaN):** 기술적 지표 계산 초기 단계의 NaN은 `ffill()` 후 `bfill()` 처리하거나 제거.
- **무한대(Inf):** 변화율 계산 시 발생하는 `Inf` 값은 `NaN`으로 치환 후 처리.
- **이상치(Outliers):** 수익률이나 검색량의 극단값은 **Winsorizing** (상하위 1% 클리핑)을 통해 모델의 왜곡 방지.

### C. 시계열 무결성 (Temporal Integrity)
- **Look-ahead Bias 금지:** 피처 생성 시 현재 시점(T)의 정보만 사용하고, 미래(T+1)의 정보를 참조하지 않도록 시차(Lag) 적용 확인.
- **데이터 정렬:** 병합 전 반드시 `Date`와 `Ticker`를 기준으로 오름차순 정렬.
- **휴장일 처리:** 주식 시장 휴장일과 검색량 데이터 사이의 날짜 불일치는 주가 데이터(영업일)를 기준으로 Inner Join 처리.

### D. 데이터 스테이셔너리 (Stationarity)
- 가격 데이터(Close, High, Low)는 직접 사용하지 않고, 반드시 **수익률(Return)**이나 **이평선과의 괴리율(Gap)** 형태로 변환하여 추세 성분을 제거하고 정상성을 확보.

---

## 3. 🧪 피처 엔지니어링 명세 (The Golden 20+)

- **기술적 모멘텀:** `rsi_14`, `macd_hist`, `bb_high_gap`, `ma5_gap`, `volatility_7` 등
- **검색 트렌드:** `weighted_trend`, `trend_lag1~3`, `trend_shock`, `kor_glb_spread` 등
- **시장 역학:** `return_lag1~3`, `volume_change`, `date_trend_rank`, `date_return_rank` 등
- **상호작용 및 수급:** `trend_ma_interaction`, `foreign_ratio`, `ticker_encoded`

---

## 4. 📊 직관적 분석 및 다각적 리포팅

- **시각화:** Feature Importance, Cumulative Return Curve, Confusion Matrix, PR Curve.
- **수치 보고:** 종목별 Accuracy/F1 테이블, 예측 확신도별 적중률(Hit Ratio), Fold별 성능 편차.

---

## 5. 🛠️ 리빌드 프로세스 프로토콜
1.  **Stage 1 (Config):** 경로 및 상수 설정.
2.  **Stage 2 (Preprocess):** 병합 → 피처 생성 → **[필수] 결측치/이상치 처리** → **[필수] 정규화** → 저장.
3.  **Stage 3 (Selection):** 중요도 기반 Top 20-25 변수 확정.
4.  **Stage 4 (Training):** 앙상블 학습 및 검증.
5.  **Stage 5 (Evaluation):** 다각적 분석 결과물 생성.

- **표준:** Pandas 벡터 연산, `random_seed=42`, 상세 로깅 필수.
