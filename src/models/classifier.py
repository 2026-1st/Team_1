import pandas as pd
import numpy as np
import os
import sys
import joblib
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV, PredefinedSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import config

class ModelTrainer:
    def __init__(self):
        self.data_path = config.DATA_PROCESSED_DIR / "selected_features_data.csv"
        # Best Parameters from Lab Notebooks
        self.models = {
            'lr': LogisticRegression(
                C=0.001, 
                penalty='elasticnet', 
                solver='saga', 
                l1_ratio=0.5, 
                class_weight=None, 
                random_state=config.RANDOM_SEED, 
                max_iter=10000
            ),
            'rf': RandomForestClassifier(
                n_estimators=300, 
                max_depth=3, 
                min_samples_leaf=20, 
                min_samples_split=10, 
                max_features='sqrt', 
                class_weight=None,
                random_state=config.RANDOM_SEED
            ),
            'xgb': XGBClassifier(
                n_estimators=100, 
                learning_rate=0.01, 
                max_depth=4, 
                colsample_bytree=0.8, 
                gamma=0.1, 
                min_child_weight=5, 
                reg_alpha=10, 
                reg_lambda=0.1, 
                subsample=0.6,
                random_state=config.RANDOM_SEED, 
                eval_metric='logloss'
            )
        }
        self.ensemble = None

    def train(self):
        print("--- [1/3] 데이터 로드 및 70/15/15 분할 중 ---")
        df = pd.read_csv(self.data_path)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        
        exclude = ['Date', 'ticker', 'target', 'next_return']
        features = [c for c in df.columns if c not in exclude]
        
        X = df[features]
        y = df['target']
        
        # 70/15/15 Time-series Split
        n = len(df)
        tr_idx = int(n * 0.7)
        val_idx = int(n * 0.85)
        
        X_train, y_train = X.iloc[:tr_idx], y.iloc[:tr_idx]
        X_val, y_val = X.iloc[tr_idx:val_idx], y.iloc[tr_idx:val_idx]
        X_test, y_test = X.iloc[val_idx:], y.iloc[val_idx:]
        
        # 1. Build Soft Voting Ensemble
        print("--- [Ensemble Construction] 소프트 보팅 앙상블 구성 중 ---")
        self.ensemble = VotingClassifier(
            estimators=[
                ('lr', self.models['lr']),
                ('rf', self.models['rf']),
                ('xgb', self.models['xgb'])
            ],
            voting='soft'
        )
        
        eval_models = self.models.copy()
        eval_models['ensemble'] = self.ensemble
        
        performance_records = []
        
        print(f"--- [2/3] 모델 평가 시작 (Classification Metrics) ---")
        for name, model in eval_models.items():
            model.fit(X_train, y_train)
            
            for set_name, X_set, y_set in [('Train', X_train, y_train), ('Val', X_val, y_val), ('Test', X_test, y_test)]:
                preds = model.predict(X_set)
                probs = model.predict_proba(X_set)[:, 1]
                
                performance_records.append({
                    'Model': name,
                    'Set': set_name,
                    'Accuracy': accuracy_score(y_set, preds),
                    'Precision': precision_score(y_set, preds),
                    'Recall': recall_score(y_set, preds),
                    'F1': f1_score(y_set, preds),
                    'AUC': roc_auc_score(y_set, probs)
                })
        
        # Summary results
        results_df = pd.DataFrame(performance_records)
        save_metrics_path = config.REPORT_DIR / "model_classification_metrics.csv"
        results_df.to_csv(save_metrics_path, index=False)
        print(f"전체 평가지표 저장 완료: {save_metrics_path}")
        
        print("\n--- [3/3] 최종 모델 저장 중 ---")
        for name, model in eval_models.items():
            # final training can be on full data or keep tr/val split as per experiment
            # for strict 70/15/15 reporting, we already have results
            save_path = config.MODEL_DIR / f"{name}_model.joblib"
            joblib.dump(model, save_path)
            
        return results_df

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train()
