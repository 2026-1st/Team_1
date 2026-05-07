# 기계학습 기초 팀 프로젝트

기계학습 기초 1팀 프로젝트 레포입니다.
 
## 개발 환경
- Python Version: 3.11.x
- Dependency Management: requirements.txt

### 설치 및 설정
1. 저장소 복제:
   ```bash
   git clone https://github.com/2026-1st/Team_1.git
   cd Team_1
   ```
2. 가상환경 생성 (선택 사항):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. 라이브러리 설치:
   ```bash
   pip install -r requirements.txt
   ```

## 프로젝트 구조
```text
root/
├── data/                 # 데이터 저장소
│   ├── raw/              # 수집된 원본 데이터 (수정 금지)
│   └── processed/        # 전처리가 완료된 정제 데이터
├── notebooks/            # EDA 및 프로토타이핑 (Jupyter Notebook)
├── src/                  # 재사용 가능한 소스 코드 (Python Script)
│   ├── __init__.py
│   ├── crawler.py        # 데이터 수집 로직
│   ├── preprocessing.py  # 피처 엔지니어링 및 전처리 함수
│   └── models.py         # 모델 정의 및 학습 함수
├── models/               # 학습된 모델 파일 저장 (.pkl, .h5 등)
├── reports/              # 시각화 결과물 및 보고서
│   └── figures/          # 그래프 이미지 저장 경로
├── requirements.txt      # 프로젝트 의존성 목록
└── README.md             # 프로젝트 개요 및 가이드라인
```

## 주요 워크플로우
1. 데이터 수집: `src/crawler.py` 또는 `notebooks/01_data_crawling.ipynb`를 통해 데이터를 수집하여 `data/raw/`에 저장
2. 분석 및 전처리: `notebooks/02_eda_and_preprocessing.ipynb`에서 데이터 분석 후 전처리 로직을 확정하고, 결과를 `data/processed/`에 저장
3. 모델 학습: `notebooks/03_model_training.ipynb`에서 모델을 학습 및 검증
4. 모듈화: 검증된 코드는 `src/` 폴더 내의 파이썬 파일로 이관하여 관리
5. 모델 저장: 학습 완료된 모델은 `models/` 폴더에 버전별로 저장
6. 결과 정리: 주요 지표 및 시각화 자료는 `reports/` 폴더에 정리

