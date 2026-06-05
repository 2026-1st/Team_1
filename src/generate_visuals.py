import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import sys
from pathlib import Path
from sklearn.metrics import confusion_matrix, precision_recall_curve, auc, ConfusionMatrixDisplay

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import config

def generate_comparison_plots():
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    # Load Data
    data_path = config.DATA_PROCESSED_DIR / "selected_features_data.csv"
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    exclude = ['Date', 'ticker', 'target', 'next_return']
    features = [c for c in df.columns if c not in exclude]
    X = df[features]
    y = df['target']
    
    # Test Split (matching evaluator.py)
    n = len(df)
    val_idx = int(n * 0.85)
    X_test, y_test = X.iloc[val_idx:], y.iloc[val_idx:]
    
    # Load Models
    models = {
        'Logistic Regression': joblib.load(config.MODEL_DIR / "lr_model.joblib"),
        'Random Forest': joblib.load(config.MODEL_DIR / "rf_model.joblib"),
        'XGBoost': joblib.load(config.MODEL_DIR / "xgb_model.joblib"),
        'Soft Voting Ensemble': joblib.load(config.MODEL_DIR / "ensemble_model.joblib")
    }
    
    # 1. 2x2 Confusion Matrix
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes = axes.flatten()
    
    for i, (name, model) in enumerate(models.items()):
        y_prob = model.predict_proba(X_test)[:, 1]
        y_pred = (y_prob > 0.5).astype(int)
        cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
        
        print(f"Model: {name}")
        print(cm)
        
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, 
                                      display_labels=['0 (Down)', '1 (Up)'])
        
        # Draw on axes[i]
        disp.plot(ax=axes[i], cmap='Blues', values_format='d', 
                  text_kw={'size': 14, 'weight': 'bold'})
        
        axes[i].set_title(f'{name}', fontsize=16, pad=15)
        axes[i].set_ylabel('Actual Label', fontsize=12)
        axes[i].set_xlabel('Predicted Label', fontsize=12)
        
    plt.suptitle('Confusion Matrix Comparison (Test Set)', fontsize=22, y=0.98)
    plt.tight_layout(pad=4.0)
    plt.savefig(report_dir / "confusion_matrix_comparison.png", dpi=150) # Reduced DPI for faster handling, enough for MD
    plt.close()
    plt.close()
    
    # 2. 2x2 PR Curve
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.flatten()
    
    for i, (name, model) in enumerate(models.items()):
        y_prob = model.predict_proba(X_test)[:, 1]
        precision, recall, _ = precision_recall_curve(y_test, y_prob)
        pr_auc = auc(recall, precision)
        
        axes[i].plot(recall, precision, marker='.', label=f'AUC={pr_auc:.2f}')
        axes[i].set_title(f'{name} PR Curve', fontsize=14)
        axes[i].set_xlabel('Recall')
        axes[i].set_ylabel('Precision')
        axes[i].legend()
        axes[i].grid(True, alpha=0.3)
        
    plt.tight_layout()
    plt.savefig(report_dir / "pr_curve_comparison.png", dpi=300)
    plt.close()
    
    print("Combined comparison plots generated successfully.")

if __name__ == "__main__":
    generate_comparison_plots()
