import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import sys
from sklearn.metrics import confusion_matrix, precision_recall_curve, auc

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import config

def evaluate_models():
    print("--- [1/4] 분석을 위한 데이터 및 모델 로드 중 ---")
    data_path = config.DATA_PROCESSED_DIR / "selected_features_data.csv"
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    exclude = ['Date', 'ticker', 'target', 'next_return']
    features = [c for c in df.columns if c not in exclude]
    X = df[features]
    y = df['target']
    
    rf_model = joblib.load(config.MODEL_DIR / "rf_model.joblib")
    xgb_model = joblib.load(config.MODEL_DIR / "xgb_model.joblib")
    lr_model = joblib.load(config.MODEL_DIR / "lr_model.joblib")
    ensemble_model = joblib.load(config.MODEL_DIR / "ensemble_model.joblib")
    
    # 1. Feature Importance Plot
    print("--- [2/4] 변수 중요도 시각화 생성 중 ---")
    fig, axes = plt.subplots(1, 3, figsize=(25, 10))
    
    # Tree based models
    for i, (name, model) in enumerate([('Random Forest', rf_model), ('XGBoost', xgb_model)]):
        importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False).head(20)
        sns.barplot(x=importances.values, y=importances.index, ax=axes[i], palette='viridis')
        axes[i].set_title(f'{name} Top 20 Features')
    
    # Logistic Regression coefficients
    lr_importances = pd.Series(np.abs(lr_model.coef_[0]), index=features).sort_values(ascending=False).head(20)
    sns.barplot(x=lr_importances.values, y=lr_importances.index, ax=axes[2], palette='magma')
    axes[2].set_title('Logistic Regression (Baseline) Top 20 Coefs')
    
    plt.tight_layout()
    plt.savefig(config.REPORT_DIR / "feature_importance.png")
    
    # 2. Cumulative Return Simulation
    print("--- [3/4] 가상 수익률 시뮬레이션 중 ---")
    df['ensemble_prob'] = ensemble_model.predict_proba(X)[:, 1]
    
    # Strategy: Buy if ensemble prob > 0.5
    df['signal'] = (df['ensemble_prob'] > 0.5).astype(int)
    df['strategy_return'] = df['signal'] * df['next_return']
    
    # Calculate cumulative returns per ticker
    plt.figure(figsize=(15, 8))
    for name, symbol in config.TICKER_MAP.items():
        ticker_df = df[df['ticker'] == symbol].sort_values('Date')
        if ticker_df.empty: continue
        cum_strategy = (1 + ticker_df['strategy_return']).cumprod()
        cum_market = (1 + ticker_df['next_return']).cumprod()
        plt.plot(ticker_df['Date'], cum_strategy, label=f'{name} (Strategy)', linestyle='--')
        plt.plot(ticker_df['Date'], cum_market, label=f'{name} (Market)', alpha=0.3)
        
    plt.title('Cumulative Returns: Strategy vs Market')
    plt.legend()
    plt.savefig(config.REPORT_DIR / "cumulative_returns.png")
    
    # 3. Confusion Matrix & PR Curve
    print("--- [4/4] 혼동 행렬 및 성능 지표 생성 중 ---")
    y_pred = (df['ensemble_prob'] > 0.5).astype(int)
    cm = confusion_matrix(y, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Ensemble Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.savefig(config.REPORT_DIR / "confusion_matrix.png")
    
    # PR Curve
    precision, recall, _ = precision_recall_curve(y, df['ensemble_prob'])
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, marker='.')
    plt.title(f'Precision-Recall Curve (AUC={auc(recall, precision):.2f})')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.savefig(config.REPORT_DIR / "pr_curve.png")
    
    # Multi-Ticker Summary Table
    summary = []
    for name, symbol in config.TICKER_MAP.items():
        t_df = df[df['ticker'] == symbol]
        if t_df.empty: continue
        t_acc = (t_df['target'] == (t_df['ensemble_prob'] > 0.5)).mean()
        t_ret = (1 + t_df['strategy_return']).prod() - 1
        m_ret = (1 + t_df['next_return']).prod() - 1
        summary.append({
            'Ticker': name,
            'Accuracy': t_acc,
            'Strategy Return': t_ret,
            'Market Return': m_ret,
            'Alpha': t_ret - m_ret
        })
    
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(config.REPORT_DIR / "ticker_performance_summary.csv", index=False)
    print(f"분석 보고서 저장 완료: {config.REPORT_DIR}")

if __name__ == "__main__":
    evaluate_models()
