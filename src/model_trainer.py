import os
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
os.environ.setdefault("MPLCONFIGDIR", str(Path(os.getenv("TMPDIR", "/tmp")) / "team1_matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
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
            'ticker_encoded',
            # EDA Section 8 추가 피처
            'trend_shock', 'kor_glb_spread', 'trend_ma_interaction'
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
        if 'trend_kor' not in df.columns and 'trend_base' in df.columns:
            df['trend_kor'] = df['trend_base']
        
        # EDA Section 8: 피처 엔지니어링 고도화
        # 1. Trend Momentum (Shock): 검색량 200% 이상 급증 여부
        df['trend_shock'] = (df['trend_change'] > 2.0).astype(int)
        
        # 2. KOR-GLB Spread: 국내외 관심도 차이
        df['kor_glb_spread'] = df['trend_kor'] - df['trend_glb']
        
        # 3. Interaction: 검색량과 기술적 지표(과매도/과매수)의 결합
        df['trend_ma_interaction'] = df['weighted_trend'] * df['ma5_gap']
        
        # 무한대나 결측치 최종 처리
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.ffill().bfill().fillna(0)
        
        # 날짜와 티커 기준으로 정렬하여 일관성 유지
        return df.sort_values(['Date', 'ticker_encoded']).reset_index(drop=True)

    def cross_validate(self, model, X, y, n_splits=5):
        """TimeSeriesSplit을 이용한 교차 검증 (EDA Section 8 제언)"""
        tscv = TimeSeriesSplit(n_splits=n_splits)
        scores = []
        
        print(f"\n[TimeSeries Cross-Validation ({n_splits} splits)]")
        for i, (train_index, test_index) in enumerate(tscv.split(X)):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            scores.append(acc)
            print(f"  Split {i+1}: Accuracy = {acc:.4f}")
            
        print(f"  Average Accuracy: {np.mean(scores):.4f} (+/- {np.std(scores):.4f})")
        return scores

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
        plt.tight_layout()
        plt.savefig(self.reports_dir / f"{model_name}_confusion_matrix.png")
        plt.close()
        
        return y_pred

    def save_model(self, model, model_name):
        """학습된 모델 저장"""
        save_path = self.models_dir / f"{model_name}.joblib"
        joblib.dump(model, save_path)
        print(f"모델 저장 완료: {save_path}")

    def run(self):
        """기본 및 고성능 모델(EDA 제언) 학습 파이프라인 실행"""
        print("--- 모델 학습 파이프라인 실행 (EDA Section 8 반영) ---")
        (X_train, y_train), (X_val, y_val), (X_test, y_test) = self.get_prepared_data()
        
        # 1. Baseline: Logistic Regression
        print("\n[1. Baseline Model: Logistic Regression]")
        from sklearn.linear_model import LogisticRegression
        lr_model = LogisticRegression(max_iter=1000)
        lr_model.fit(X_train, y_train)
        self.evaluate_model(lr_model, X_test, y_test, "LogisticRegression_Baseline")
        self.save_model(lr_model, "baseline_logistic")

        # 2. Non-linear Model: Random Forest
        print("\n[2. Advanced Model: Random Forest]")
        from sklearn.ensemble import RandomForestClassifier
        rf_model = RandomForestClassifier(n_estimators=100, random_state=config.RANDOM_STATE if hasattr(config, 'RANDOM_STATE') else 42)
        
        # 교차 검증 수행
        X_combined = np.vstack([X_train, X_val])
        y_combined = pd.concat([y_train, y_val])
        self.cross_validate(rf_model, X_combined, y_combined)
        
        rf_model.fit(X_train, y_train)
        self.evaluate_model(rf_model, X_test, y_test, "RandomForest_Advanced")
        self.save_model(rf_model, "advanced_rf")

        # 3. Non-linear Model: XGBoost (EDA 제언)
        print("\n[3. Advanced Model: XGBoost]")
        try:
            from xgboost import XGBClassifier
            xgb_model = XGBClassifier(n_estimators=100, learning_rate=0.05, max_depth=6, random_state=42)
            xgb_model.fit(X_train, y_train)
            self.evaluate_model(xgb_model, X_test, y_test, "XGBoost_Advanced")
            self.save_model(xgb_model, "advanced_xgb")
        except ImportError:
            print("XGBoost가 설치되어 있지 않아 건너뜁니다.")

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.run()
