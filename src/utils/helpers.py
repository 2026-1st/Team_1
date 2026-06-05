import pandas as pd
import numpy as np

def calculate_rsi(series, window=14):
    """상대강도지수 (RSI) 계산"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def calculate_macd(series, fast=12, slow=26, signal=9):
    """MACD 히스토그램 계산"""
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    return macd - macd_signal

def calculate_bollinger_bands(series, window=20, num_std=2):
    """볼린저 밴드 상/하단 계산"""
    rolling_mean = series.rolling(window=window).mean()
    rolling_std = series.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band, lower_band

def winsorize_series(series, limits=(0.01, 0.01)):
    """이상치 클리핑 (Winsorizing)"""
    lower_bound = series.quantile(limits[0])
    upper_bound = series.quantile(1 - limits[1])
    return series.clip(lower=lower_bound, upper=upper_bound)
