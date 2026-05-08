# 기계학습 기초 팀 프로젝트

기계학습 기초 1팀 프로젝트 레포입니다.
- Notion : https://www.notion.so/3598fc4dd92380e5a175fa80c98d8a7f?source=copy_link

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
├── models/               # 학습된 모델 파일 저장 (.pkl, .h5 등)
├── reports/              # 시각화 결과물 및 보고서
│   └── figures/          # 그래프 이미지 저장 경로
├── requirements.txt      # 프로젝트 의존성 목록
└── README.md             # 프로젝트 개요 및 가이드라인
```