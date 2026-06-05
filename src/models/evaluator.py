import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import sys
from sklearn.metrics import confusion_matrix, precision_recall_curve, auc, accuracy_score

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
    
    # Standard 70/15/15 Split for Consistency
    n = len(df)
    val_idx = int(n * 0.85)
    X_test, y_test = X.iloc[val_idx:], y.iloc[val_idx:]
    
    rf_model = joblib.load(config.MODEL_DIR / "rf_model.joblib")
    xgb_model = joblib.load(config.MODEL_DIR / "xgb_model.joblib")
    lr_model = joblib.load(config.MODEL_DIR / "lr_model.joblib")
    ensemble_model = joblib.load(config.MODEL_DIR / "ensemble_model.joblib")
    
    # 0. Load and Plot Classification Metrics (70/15/15)
    print("--- [0/4] 70/15/15 분할 기반 분류 지표 시각화 ---")
    metrics_path = config.REPORT_DIR / "model_classification_metrics.csv"
    if metrics_path.exists():
        m_df = pd.read_csv(metrics_path)
        plt.figure(figsize=(15, 8))
        test_m = m_df[m_df['Set'] == 'Test']
        melted_m = test_m.melt(id_vars='Model', value_vars=['Accuracy', 'Recall', 'Precision', 'F1'], 
                               var_name='Metric', value_name='Score')
        sns.barplot(data=melted_m, x='Model', y='Score', hue='Metric', palette='muted')
        plt.title('Final Model Comparison (Test Set)', fontsize=15)
        plt.ylim(0, 1.1)
        plt.savefig(config.REPORT_DIR / "classification_comparison.png", dpi=300)
        plt.close()

    # 1. Feature Importance Plot (Consolidated)
    print("--- [2/4] 변수 중요도 시각화 생성 중 ---")
    plt.figure(figsize=(15, 10))
    importances = pd.Series(xgb_model.feature_importances_, index=features).sort_values(ascending=False).head(20)
    sns.barplot(x=importances.values, y=importances.index, palette='viridis')
    plt.title('Top 20 Feature Importances (XGBoost)', fontsize=15)
    plt.xlabel('Importance Score')
    plt.tight_layout()
    plt.savefig(config.REPORT_DIR / "feature_importance.png", dpi=300)
    plt.close()
    
    # 2. Cumulative Return Simulation (On Test Set Only for True Performance)
    print("--- [3/4] 가상 수익률 시뮬레이션 중 (Test Set 기준) ---")
    df_test = df.iloc[val_idx:].copy()
    df_test['ensemble_prob'] = ensemble_model.predict_proba(X_test)[:, 1]
    df_test['signal'] = (df_test['ensemble_prob'] > 0.5).astype(int)
    df_test['strategy_return'] = df_test['signal'] * df_test['next_return']
    
    plt.figure(figsize=(15, 8))
    eng_names = {
        '005930.KS': 'Samsung',
        '000660.KS': 'SK Hynix',
        '005380.KS': 'Hyundai',
        '066570.KS': 'LG Elec',
        '035420.KS': 'NAVER',
        '012450.KS': 'Hanwha Aero'
    }
    
    for symbol, name in eng_names.items():
        ticker_df = df_test[df_test['ticker'] == symbol].sort_values('Date')
        if ticker_df.empty: continue
        cum_strategy = (1 + ticker_df['strategy_return']).cumprod()
        plt.plot(ticker_df['Date'], cum_strategy, label=f'{name} (Strategy)')
        
    plt.title('Soft Voting Ensemble: Strategy Returns (Test Set Only)', fontsize=15)
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(config.REPORT_DIR / "cumulative_returns.png", dpi=300)
    plt.close()
    
    # 3. Confusion Matrix & PR Curve (On Test Set)
    print("--- [4/4] 혼동 행렬 및 성능 지표 생성 중 (Test Set 기준) ---")
    y_pred = (df_test['ensemble_prob'] > 0.5).astype(int)
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Purples', 
                xticklabels=['Pred 0', 'Pred 1'], yticklabels=['Actual 0', 'Actual 1'])
    plt.title('Ensemble Confusion Matrix (Test Set)', fontsize=15)
    plt.savefig(config.REPORT_DIR / "confusion_matrix.png", dpi=300)
    plt.close()
    
    # PR Curve
    precision, recall, _ = precision_recall_curve(y_test, df_test['ensemble_prob'])
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, marker='.', color='purple')
    plt.title(f'Ensemble PR Curve (AUC={auc(recall, precision):.2f})', fontsize=15)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.grid(True, alpha=0.3)
    plt.savefig(config.REPORT_DIR / "pr_curve.png", dpi=300)
    plt.close()
    
    # Multi-Ticker Summary Table (On Test Set)
    summary = []
    for name, symbol in config.TICKER_MAP.items():
        t_df = df_test[df_test['ticker'] == symbol]
        if t_df.empty: continue
        t_acc = accuracy_score(t_df['target'], (t_df['ensemble_prob'] > 0.5))
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
