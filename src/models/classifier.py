import pandas as pd
import numpy as np
import os
import sys
import joblib
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV, PredefinedSplit
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import config

class ModelTrainer:
    def __init__(self):
        self.data_path = config.DATA_PROCESSED_DIR / "selected_features_data.csv"
        # Baseline: Logistic Regression (tuned later)
        # Main Models: Random Forest, XGBoost
        self.models = {
            'lr': LogisticRegression(random_state=config.RANDOM_SEED, max_iter=5000),
            'rf': RandomForestClassifier(n_estimators=200, random_state=config.RANDOM_SEED),
            'xgb': XGBClassifier(n_estimators=200, random_state=config.RANDOM_SEED, eval_metric='logloss')
        }
        self.ensemble = None

    def tune_lr(self, X_train, y_train, X_val, y_val):
        print("--- [Baseline Optimization] Validation 데이터 기준 LR 튜닝 중 ---")
        
        # Merge Train and Val for PredefinedSplit
        X_combined = pd.concat([X_train, X_val])
        y_combined = pd.concat([y_train, y_val])
        
        # Create a test_fold array: -1 for training, 0 for validation
        test_fold = np.concatenate([
            np.full(len(X_train), -1),
            np.full(len(X_val), 0)
        ])
        ps = PredefinedSplit(test_fold)
        
        # Improved Parameter Grid
        param_grid = [
            {
                'C': np.logspace(-4, 1, 10),
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga'],
                'class_weight': ['balanced', None]
            },
            {
                'C': np.logspace(-4, 1, 10),
                'penalty': ['elasticnet'],
                'solver': ['saga'],
                'l1_ratio': [0.1, 0.5, 0.9],
                'class_weight': ['balanced', None]
            }
        ]
        
        grid_search = GridSearchCV(
            estimator=LogisticRegression(random_state=config.RANDOM_SEED, max_iter=5000),
            param_grid=param_grid,
            cv=ps, # Use PredefinedSplit (Validation set)
            scoring='f1',
            n_jobs=-1
        )
        grid_search.fit(X_combined, y_combined)
        print(f"최적 파라미터 (LR, Val 기준): {grid_search.best_params_}")
        return grid_search.best_estimator_

    def train(self):
        print("--- [1/3] 데이터 로드 및 분할 중 ---")
        df = pd.read_csv(self.data_path)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        
        exclude = ['Date', 'ticker', 'target', 'next_return']
        features = [c for c in df.columns if c not in exclude]
        
        X = df[features]
        y = df['target']
        
        # Split data for Tuning (Train 85% / Val 15%)
        split_idx = int(len(df) * 0.85)
        X_train_tune, y_train_tune = X.iloc[:split_idx], y.iloc[:split_idx]
        X_val_tune, y_val_tune = X.iloc[split_idx:], y.iloc[split_idx:]
        
        # 1. Tune Logistic Regression
        self.models['lr'] = self.tune_lr(X_train_tune, y_train_tune, X_val_tune, y_val_tune)
        
        # 2. Build Soft Voting Ensemble
        print("--- [Ensemble Construction] 소프트 보팅 앙상블 구성 중 ---")
        self.ensemble = VotingClassifier(
            estimators=[
                ('lr', self.models['lr']),
                ('rf', self.models['rf']),
                ('xgb', self.models['xgb'])
            ],
            voting='soft'
        )
        
        tscv = TimeSeriesSplit(n_splits=config.TS_SPLITS)
        
        results = []
        
        print(f"--- [2/3] {config.TS_SPLITS}-Fold 시계열 교차 검증 시작 ---")
        # Include Ensemble in cross-validation
        eval_models = self.models.copy()
        eval_models['ensemble'] = self.ensemble
        
        for i, (train_index, test_index) in enumerate(tscv.split(X)):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            
            fold_results = {'fold': i+1}
            
            for name, model in eval_models.items():
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                probs = model.predict_proba(X_test)[:, 1]
                
                fold_results[f'{name}_acc'] = accuracy_score(y_test, preds)
                fold_results[f'{name}_f1'] = f1_score(y_test, preds)
                fold_results[f'{name}_auc'] = roc_auc_score(y_test, probs)
            
            results.append(fold_results)
            print(f"Fold {i+1} 완료")

        # Summary results
        results_df = pd.DataFrame(results)
        print("\n--- 교차 검증 요약 ---")
        print(results_df.mean())
        
        print("\n--- [3/3] 최종 모델 학습 및 저장 중 ---")
        for name, model in eval_models.items():
            model.fit(X, y) # Train on full data for production
            save_path = config.MODEL_DIR / f"{name}_model.joblib"
            joblib.dump(model, save_path)
            print(f"모델 저장 완료: {save_path}")
            
        return results_df

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train()
