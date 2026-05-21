import os
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import config

class ModelTrainer:
    """
    데이터 로드, 전처리, 스케일링 및 평가를 통합 관리하는 클래스입니다.
    모든 모델 노트북에서 이 클래스를 활용하여 동일한 데이터 환경을 유지합니다.
    """
    def __init__(self):
        self.data_path = Path(config.PROCESSED_DATA_DIR) / "all_companies_model_data.csv"
        self.models_dir = Path(config.MODELS_DIR)
        self.reports_dir = Path(config.REPORTS_DIR)
        
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.features = [
            'trend_kor', 'trend_glb', 'foreign_ratio', 'weighted_trend', 
            'Close', 'High', 'Low', 'Open', 'Volume', 'return', 
            'return_lag1', 'return_lag3_mean', 'return_lag7_mean', 
            'volume_change', 'volatility_7', 'ma5', 'ma20', 'ma5_gap', 'ma20_gap', 
            'trend_lag1', 'trend_lag3_mean', 'trend_lag7_mean', 'trend_change', 
            'ticker_encoded'
        ]
        self.target = 'target'
        self.scaler = StandardScaler()

    def get_prepared_data(self):
        """데이터 로드, 정렬, 분할 및 스케일링을 한 번에 수행"""
        df = self._load_and_preprocess()
        train_df, val_df, test_df = self._split_data(df)
        
        X_train, y_train = train_df[self.features], train_df[self.target]
        X_val, y_val = val_df[self.features], val_df[self.target]
        X_test, y_test = test_df[self.features], test_df[self.target]
        
        # 스케일링 적용
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 스케일러 저장 (기본값)
        joblib.dump(self.scaler, self.models_dir / "scaler_latest.joblib")
        
        return (X_train_scaled, y_train), (X_val_scaled, y_val), (X_test_scaled, y_test)

    def _load_and_preprocess(self):
        if not self.data_path.exists():
            raise FileNotFoundError(f"데이터 파일이 없습니다: {self.data_path}")
        
        df = pd.read_csv(self.data_path)
        df['Date'] = pd.to_datetime(df['Date'])
        # 무한대나 결측치 최종 처리
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
        
        # 날짜와 티커 기준으로 정렬하여 일관성 유지
        return df.sort_values(['Date', 'ticker_encoded']).reset_index(drop=True)

    def _split_data(self, df):
        """70% Train, 15% Val, 15% Test 순차 분할"""
        n = len(df)
        train_end = int(n * 0.7)
        val_end = int(n * 0.85)
        return df.iloc[:train_end], df.iloc[train_end:val_end], df.iloc[val_end:]

    def evaluate_model(self, model, X_test, y_test, model_name="Model"):
        """모델 성능 평가 및 결과 출력"""
        y_pred = model.predict(X_test)
        
        print(f"\n[{model_name} Test Set 성능 평가]")
        print(classification_report(y_test, y_pred))
        
        # 혼동 행렬 시각화
        plt.figure(figsize=(6, 5))
        sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues')
        plt.title(f"Confusion Matrix - {model_name}")
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.show()
        
        return y_pred

    def save_model(self, model, model_name):
        """학습된 모델 저장"""
        save_path = self.models_dir / f"{model_name}.joblib"
        joblib.dump(model, save_path)
        print(f"모델 저장 완료: {save_path}")

    def run(self):
        """main.py에서 호출할 때의 기본 동작 (기본 로지스틱 회귀 예시)"""
        print("--- 기본 학습 파이프라인 실행 ---")
        (X_train, y_train), (X_val, y_val), (X_test, y_test) = self.get_prepared_data()
        
        from sklearn.linear_model import LogisticRegression
        model = LogisticRegression(max_iter=1000)
        model.fit(X_train, y_train)
        
        self.evaluate_model(model, X_test, y_test, "LogisticRegression_Baseline")
        self.save_model(model, "baseline_logistic")

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.run()
