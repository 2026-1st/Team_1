import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from model_trainer import ModelTrainer
import config

def analyze_advanced_features():
    print("--- 고도화 피처 분석 (model4) 시작 ---")
    
    # 1. ModelTrainer를 통해 전처리된 데이터 로드
    trainer = ModelTrainer()
    
    # _load_and_preprocess를 직접 호출하여 전체 데이터프레임 획득 (스케일링 전 원본 값 확인용)
    df = trainer._load_and_preprocess()
    
    advanced_features = ['trend_shock', 'kor_glb_spread', 'trend_ma_interaction']
    target = trainer.target
    
    # 2. 상관관계 분석
    print("\n[1. 상관관계 분석 (Target과의 상관계수)]")
    cols_to_corr = advanced_features + ['trend_change', target]
    corr_matrix = df[cols_to_corr].corr()
    print(corr_matrix[target].sort_values(ascending=False))
    
    # 추가 통계: 타겟별 평균값
    print("\n[2. 타겟별 피처 평균값 비교 (0: 하락/보합, 1: 상승)]")
    stats_features = advanced_features + ['trend_change']
    print(df.groupby(target)[stats_features].mean())

    # 추가 통계: Trend Shock 빈도
    print("\n[3. Trend Shock 발생 빈도 (%) (0: 미발생, 1: 발생)]")
    shock_freq = df.groupby(target)['trend_shock'].value_counts(normalize=True).unstack() * 100
    print(shock_freq)
    
    # 상관관계 히트맵 시각화
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', center=0)
    plt.title("Correlation: Advanced Features vs Target")
    plt.savefig(Path(config.REPORTS_DIR) / "advanced_features_corr.png")
    print(f"상관관계 히트맵 저장 완료: {Path(config.REPORTS_DIR) / 'advanced_features_corr.png'}")
    
    # 3. 변수 중요도(Feature Importance) 분석
    print("\n[2. 변수 중요도 분석]")
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = trainer.get_prepared_data()
    
    rf = RandomForestClassifier(n_estimators=100, random_state=config.RANDOM_STATE)
    rf.fit(X_train, y_train)
    
    importances = rf.feature_importances_
    feature_names = trainer.features
    feature_importance_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
    feature_importance_df = feature_importance_df.sort_values(by='importance', ascending=False)
    
    print("\n상위 10개 피처 중요도:")
    print(feature_importance_df.head(10))
    
    # 변수 중요도 시각화 (상위 15개)
    plt.figure(figsize=(10, 8))
    sns.barplot(x='importance', y='feature', data=feature_importance_df.head(15))
    plt.title("Top 15 Feature Importances (including Advanced Features)")
    plt.tight_layout()
    plt.savefig(Path(config.REPORTS_DIR) / "feature_importance_model4.png")
    print(f"변수 중요도 플롯 저장 완료: {Path(config.REPORTS_DIR) / 'feature_importance_model4.png'}")
    
    # 4. 고도화 피처별 상세 시각화 (Target과의 관계)
    print("\n[3. 피처별 상세 분석 시각화 중...]")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Trend Shock vs Target (Bar Plot)
    sns.barplot(x=target, y='trend_shock', data=df, ax=axes[0])
    axes[0].set_title("Trend Shock Rate by Target")
    
    # KOR-GLB Spread vs Target (Box Plot)
    sns.boxplot(x=target, y='kor_glb_spread', data=df, ax=axes[1])
    axes[1].set_title("KOR-GLB Spread Distribution")
    
    # Trend-MA Interaction vs Target (Box Plot)
    sns.boxplot(x=target, y='trend_ma_interaction', data=df, ax=axes[2])
    axes[2].set_title("Trend-MA Interaction Distribution")
    
    plt.tight_layout()
    plt.savefig(Path(config.REPORTS_DIR) / "advanced_features_dist.png")
    print(f"상세 분석 시각화 저장 완료: {Path(config.REPORTS_DIR) / 'advanced_features_dist.png'}")
    
    print("\n--- 분석 완료 ---")

if __name__ == "__main__":
    analyze_advanced_features()
