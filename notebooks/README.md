# 📓 실험용 노트북 (notebooks/)

데이터 분석, 가설 검증 및 초기 모델 실험을 위한 Jupyter Notebook 파일들을 보관합니다.

## 🧪 주요 파일
- `logistic_regression_lab.ipynb`: 로지스틱 회귀 기반 기초 실험
- `random_forest_lab.ipynb`: 랜덤 포레스트 성능 테스트
- `xgboost_lab.ipynb`: XGBoost 하이퍼파라미터 튜닝 실험
- `soft_voting_lab.ipynb`: 앙상블(Soft Voting) 전략 실험
- `model_comparison_lab.ipynb`: 모델별 성능 비교 및 분석

## ⚠️ 가이드라인
- 노트북은 **실험용**입니다. 검증된 로직은 반드시 `src/` 하위의 모듈로 옮겨서 관리하십시오.
- 실행 결과(Output)를 포함하여 저장하면 다른 팀원이 결과를 확인하기 좋습니다.
