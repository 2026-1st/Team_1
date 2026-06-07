import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from statsmodels.tsa.stattools import acf, ccf

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def perform_eda():
    data_path = Path("data/processed/selected_features_data.csv")
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 1. Low Signal-to-Noise: Target Correlation Bar Chart
    numeric_df = df.select_dtypes(include=[np.number])
    correlations = numeric_df.corr()['target'].drop(['target', 'next_return']).sort_values()
    
    plt.figure(figsize=(10, 8))
    colors = ['red' if 'trend' in c.lower() else 'skyblue' for c in correlations.index]
    correlations.plot(kind='barh', color=colors)
    plt.title('피처별 타겟(익일 방향) 상관계수 (빨간색: 검색 지표)')
    plt.axvline(0, color='black', linewidth=0.8)
    plt.tight_layout()
    plt.savefig(report_dir / 'target_correlation.png')
    plt.close()
    
    # 2. Distribution Overlap: KDE Plot
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data=df[df['target'] == 1], x='weighted_trend', label='상승일 (Up)', fill=True, color='red')
    sns.kdeplot(data=df[df['target'] == 0], x='weighted_trend', label='하락일 (Down)', fill=True, color='blue')
    plt.title('검색 트렌드 분포 비교: 상승일 vs 하락일')
    plt.xlabel('정규화된 검색 트렌드 (weighted_trend)')
    plt.legend()
    plt.savefig(report_dir / 'distribution_overlap.png')
    plt.close()
    
    # 3. Temporal Asynchrony: Cross-Correlation (CCF)
    # Average CCF across all tickers
    ccfs = []
    tickers = df['ticker'].unique()
    for ticker in tickers:
        t_df = df[df['ticker'] == ticker].sort_values('Date')
        # CCF between weighted_trend(t) and return(t+k)
        # Note: ccf(x, y) = E[x_t * y_{t+k}]
        c = [np.corrcoef(t_df['weighted_trend'].iloc[:-k], t_df['return'].iloc[k:])[0, 1] if k > 0 else 
             np.corrcoef(t_df['weighted_trend'], t_df['return'])[0, 1] if k == 0 else
             np.corrcoef(t_df['weighted_trend'].iloc[-k:], t_df['return'].iloc[:k])[0, 1]
             for k in range(-5, 6)]
        ccfs.append(c)
    
    avg_ccf = np.mean(ccfs, axis=0)
    plt.figure(figsize=(10, 5))
    plt.stem(range(-5, 6), avg_ccf)
    plt.title('검색 트렌드와 수익률 간 교차 상관관계 (Lag Analysis)')
    plt.xlabel('Lag (k일)')
    plt.ylabel('상관계수')
    plt.xticks(range(-5, 6))
    plt.axvline(0, color='red', linestyle='--', alpha=0.5)
    plt.annotate('후행 반응 (Lag > 0)', xy=(2, 0.05), color='blue')
    plt.annotate('선행 예측 (Lag < 0)', xy=(-4, 0.05), color='green')
    plt.savefig(report_dir / 'cross_correlation.png')
    plt.close()

    # 4. Feature Importance Comparison (Price vs Trend)
    # Grouping features
    trend_feats = [c for c in correlations.index if 'trend' in c.lower() or 'kor' in c.lower()]
    price_feats = [c for c in correlations.index if c not in trend_feats]
    
    avg_corr_trend = correlations[trend_feats].abs().mean()
    avg_corr_price = correlations[price_feats].abs().mean()
    
    plt.figure(figsize=(8, 6))
    sns.barplot(x=['검색 트렌드 지표', '기술적/가격 지표'], y=[avg_corr_trend, avg_corr_price])
    plt.title('지표 그룹별 평균 절대 상관계수 비교')
    plt.ylabel('평균 절대 상관계수')
    plt.savefig(report_dir / 'group_comparison.png')
    plt.close()

if __name__ == "__main__":
    perform_eda()

if __name__ == "__main__":
    perform_eda()
