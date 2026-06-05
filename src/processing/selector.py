import pandas as pd
import numpy as np
import os
import sys
from xgboost import XGBClassifier

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import config

def select_features(target_count=25, corr_threshold=0.85):
    print(f"--- [1/3] 가공된 데이터 로드 중 ---")
    data_path = config.DATA_PROCESSED_DIR / "processed_model_data.csv"
    if not data_path.exists():
        print(f"[Error] 데이터가 없습니다: {data_path}")
        return

    df = pd.read_csv(data_path)
    
    # Define potential features
    exclude = ['Date', 'ticker', 'company_name', 'next_return', 'target']
    potential_features = [c for c in df.columns if c not in exclude]
    
    X = df[potential_features]
    y = df['target']
    
    # 1. Calculate Feature Importance with XGBoost
    print(f"--- [2/3] XGBoost 기반 중요도 산출 중 ({len(potential_features)}개 후보) ---")
    model = XGBClassifier(n_estimators=100, random_state=config.RANDOM_SEED, eval_metric='logloss')
    model.fit(X, y)
    
    importances = pd.Series(model.feature_importances_, index=potential_features).sort_values(ascending=False)
    
    # 2. Greedy Selection with Correlation Check
    print(f"--- [3/3] 다중공선성 제거 및 Top {target_count} 선택 중 ---")
    corr_matrix = X.corr().abs()
    selected_features = []
    
    for feat in importances.index:
        if len(selected_features) >= target_count:
            break
            
        # Check correlation with already selected features
        is_redundant = False
        for selected in selected_features:
            if corr_matrix.loc[feat, selected] > corr_threshold:
                is_redundant = True
                break
        
        if not is_redundant:
            selected_features.append(feat)
    
    print(f"최종 선택된 피처 ({len(selected_features)}개):")
    for i, f in enumerate(selected_features):
        print(f"{i+1}. {f}")
        
    # Save selected features list and data
    selected_data = df[['Date', 'ticker', 'target', 'next_return'] + selected_features]
    save_path = config.DATA_PROCESSED_DIR / "selected_features_data.csv"
    selected_data.to_csv(save_path, index=False)
    print(f"최종 데이터 저장 완료: {save_path}")
    
    return selected_features

if __name__ == "__main__":
    select_features()
