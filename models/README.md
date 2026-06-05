# 🤖 모델 디렉토리 (models/)

학습이 완료된 모델 객체들을 저장하는 공간입니다.

## 📁 구성
- **.joblib 파일**: Scikit-learn 및 XGBoost로 학습된 모델들이 바이너리 형태로 저장됩니다.
- 모델 파일명 규칙: `{model_type}_{ticker}_{timestamp}.joblib` (또는 프로젝트 설정에 따른 규칙)

## 🛠️ 사용 방법
저장된 모델은 `src/models/evaluator.py` 등에서 로드하여 백테스팅이나 실제 예측에 사용됩니다.
```python
import joblib
model = joblib.load('models/best_model.joblib')
```
