# Model 1 Stepwise Improvement Report

## 1. 개선 목표

기존 Logistic Regression baseline 모델은 테스트 세트에서 Accuracy 0.4924, F1 Score 0.4898, ROC-AUC 0.4857을 기록하였다. 이는 무작위 예측 수준과 유사하므로, 다음과 같은 방향으로 단계적 성능 개선을 시도하였다.

- 정규화 강도 조정
- `class_weight` 설정 변경
- Feature selection 적용
- Decision threshold 조정

단, 성능 개선은 단일 지표만 기준으로 판단하지 않았다. Accuracy, Precision, Recall, F1 Score, ROC-AUC, Confusion Matrix를 함께 확인하여 실제로 의미 있는 개선인지 해석하였다.

## 2. 단계별 실험 결과

| Step | 설정 | Threshold | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
|---|---|---:|---:|---:|---:|---:|---:|
| Step 0 | Baseline: `C=1`, `class_weight=balanced` | 0.50 | 0.4924 | 0.5333 | 0.4528 | 0.4898 | 0.4857 |
| Step 1 | Strong regularization: `C=0.001`, `class_weight=None` | 0.50 | 0.5431 | 0.5513 | 0.8113 | 0.6565 | 0.5189 |
| Step 2 | SelectKBest top12 + `C=0.001`, `class_weight=balanced` | 0.50 | 0.5431 | 0.5889 | 0.5000 | 0.5408 | 0.5180 |
| Step 3 | Baseline + threshold tuning | 0.32 | 0.5431 | 0.5417 | 0.9811 | 0.6980 | 0.4857 |

![Stepwise metric comparison](figures/model1_improvement/01_stepwise_metric_comparison.png)

![Stepwise confusion matrices](figures/model1_improvement/02_stepwise_confusion_matrices.png)

## 3. Step 0: Baseline

Baseline 모델은 다음 설정을 사용하였다.

```python
LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42
)
```

Baseline의 Confusion Matrix는 다음과 같다.

|  | Predicted 0 | Predicted 1 |
|---|---:|---:|
| Actual 0 | 49 | 42 |
| Actual 1 | 58 | 48 |

Baseline은 실제 상승 106개 중 48개만 맞혔고, 58개를 하락으로 잘못 예측하였다. 이 때문에 Recall이 0.4528로 낮게 나타났다. Accuracy는 0.4924, ROC-AUC는 0.4857로 무작위 예측 수준에 가까웠다.

## 4. Step 1: 정규화 강화 및 class weight 제거

Step 1에서는 다음과 같이 설정을 변경하였다.

```python
LogisticRegression(
    C=0.001,
    max_iter=1000,
    class_weight=None,
    random_state=42
)
```

변경 의도는 다음과 같다.

- `C=0.001`: 강한 정규화를 적용하여 불안정한 계수 변동을 줄인다.
- `class_weight=None`: 기존 `balanced` 설정이 상승/하락 판단을 오히려 불안정하게 만들 가능성을 확인한다.

Step 1 결과는 다음과 같다.

| Metric | Baseline | Step 1 | 변화 |
|---|---:|---:|---:|
| Accuracy | 0.4924 | 0.5431 | +0.0508 |
| Precision | 0.5333 | 0.5513 | +0.0179 |
| Recall | 0.4528 | 0.8113 | +0.3585 |
| F1 Score | 0.4898 | 0.6565 | +0.1667 |
| ROC-AUC | 0.4857 | 0.5189 | +0.0332 |

Confusion Matrix는 다음과 같다.

|  | Predicted 0 | Predicted 1 |
|---|---:|---:|
| Actual 0 | 21 | 70 |
| Actual 1 | 20 | 86 |

Step 1은 실제 상승 106개 중 86개를 상승으로 맞히면서 Recall이 크게 개선되었다. F1 Score도 0.4898에서 0.6565로 상승하였다. 다만 실제 하락 91개 중 70개를 상승으로 잘못 예측하여 False Positive가 크게 증가하였다. 즉, 상승 포착 능력은 개선되었지만 하락을 구분하는 능력은 약해졌다.

이 단계는 "상승 기회를 놓치지 않는 것"을 중요하게 보는 경우에는 유용하지만, 잘못된 상승 신호를 줄여야 하는 투자 전략에서는 주의가 필요하다.

## 5. Step 2: Feature Selection 적용

Step 2에서는 `SelectKBest`를 사용하여 상위 12개 feature만 선택하고, 강한 정규화를 함께 적용하였다.

```python
Pipeline([
    ("select", SelectKBest(score_func=f_classif, k=12)),
    ("clf", LogisticRegression(
        C=0.001,
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ))
])
```

변경 의도는 다음과 같다.

- 전체 feature 중 target과 관련성이 상대적으로 높은 feature만 사용한다.
- 불필요하거나 노이즈가 큰 feature를 줄여 일반화 성능을 개선한다.
- 강한 정규화를 함께 적용하여 계수의 과도한 변동을 줄인다.

Step 2 결과는 다음과 같다.

| Metric | Baseline | Step 2 | 변화 |
|---|---:|---:|---:|
| Accuracy | 0.4924 | 0.5431 | +0.0508 |
| Precision | 0.5333 | 0.5889 | +0.0556 |
| Recall | 0.4528 | 0.5000 | +0.0472 |
| F1 Score | 0.4898 | 0.5408 | +0.0510 |
| ROC-AUC | 0.4857 | 0.5180 | +0.0323 |

Confusion Matrix는 다음과 같다.

|  | Predicted 0 | Predicted 1 |
|---|---:|---:|
| Actual 0 | 54 | 37 |
| Actual 1 | 53 | 53 |

Step 2는 Step 1보다 Recall은 낮지만, Precision이 0.5889로 가장 높게 나타났다. 또한 Confusion Matrix도 Step 1처럼 한쪽 클래스로 크게 치우치지 않았다. 실제 하락 91개 중 54개를 맞혔고, 실제 상승 106개 중 53개를 맞혔다.

따라서 Step 2는 "상승 포착률을 극단적으로 높이는 모델"이라기보다는, Precision과 Recall의 균형을 조금 더 유지하면서 baseline 대비 성능을 개선한 모델로 해석할 수 있다.

## 6. Step 3: Decision Threshold 조정

Step 3에서는 baseline 모델의 분류 기준을 0.5에서 0.32로 낮추었다.

```python
pred = (predict_proba[:, 1] >= 0.32).astype(int)
```

변경 의도는 다음과 같다.

- 상승으로 판단하는 기준을 낮춰 실제 상승을 더 많이 포착한다.
- Recall과 F1 Score를 개선할 수 있는지 확인한다.

Step 3 결과는 다음과 같다.

| Metric | Baseline | Step 3 | 변화 |
|---|---:|---:|---:|
| Accuracy | 0.4924 | 0.5431 | +0.0508 |
| Precision | 0.5333 | 0.5417 | +0.0083 |
| Recall | 0.4528 | 0.9811 | +0.5283 |
| F1 Score | 0.4898 | 0.6980 | +0.2082 |
| ROC-AUC | 0.4857 | 0.4857 | +0.0000 |

Confusion Matrix는 다음과 같다.

|  | Predicted 0 | Predicted 1 |
|---|---:|---:|
| Actual 0 | 3 | 88 |
| Actual 1 | 2 | 104 |

Step 3은 Recall과 F1 Score가 가장 높게 나타났다. 그러나 Confusion Matrix를 보면 거의 모든 샘플을 상승으로 예측하고 있다. 실제 하락 91개 중 88개를 상승으로 잘못 예측했기 때문에, 하락을 구분하는 능력은 거의 사라졌다.

또한 ROC-AUC는 0.4857로 baseline과 동일하다. Threshold 조정은 예측 확률 자체의 순위를 바꾸지 않기 때문에 ROC-AUC를 개선하지 못한다. 따라서 Step 3은 지표상 F1 Score는 좋아 보이지만, 실제 분류 능력이 개선되었다고 보기는 어렵다.

## 7. 최종 개선안 선택

성능 개선 단계 중 가장 해석 가능한 개선안은 Step 2로 판단하였다.

| 기준 | Step 1 | Step 2 | Step 3 |
|---|---|---|---|
| 장점 | Recall과 F1 크게 개선 | Precision, Accuracy, ROC-AUC 균형 개선 | Recall과 F1 가장 높음 |
| 단점 | False Positive 증가 | Recall 개선 폭은 제한적 | 거의 전부 상승으로 예측 |
| 최종 모델 적합성 | 목적에 따라 사용 가능 | 가장 균형적 | 일반 모델로 부적합 |

Step 2는 baseline 대비 Accuracy, Precision, Recall, F1 Score, ROC-AUC가 모두 개선되었다. 특히 Precision은 0.5333에서 0.5889로 상승하여, 모델이 상승이라고 예측했을 때 실제 상승일 가능성이 더 높아졌다. 또한 Confusion Matrix가 한쪽 클래스로 과도하게 쏠리지 않아 Step 3보다 일반적인 분류 모델로 적합하다.

따라서 Logistic Regression 내부에서의 최종 개선안은 다음과 같이 정리할 수 있다.

```python
Pipeline([
    ("select", SelectKBest(score_func=f_classif, k=12)),
    ("clf", LogisticRegression(
        C=0.001,
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ))
])
```

## 8. 결론 및 후속 개선 방향

단계적 개선을 통해 baseline 대비 일부 성능 향상을 확인하였다. 특히 Step 2는 모든 주요 지표에서 baseline보다 개선되었고, 예측 결과도 한쪽 클래스로 극단적으로 치우치지 않았다.

그러나 최종 개선안의 Test Accuracy는 0.5431, F1 Score는 0.5408, ROC-AUC는 0.5180으로 여전히 높은 수준은 아니다. 이는 Logistic Regression의 선형 결정 경계만으로는 주가 방향 예측의 복잡한 패턴을 충분히 학습하기 어렵다는 점을 보여준다.

후속 개선 방향은 다음과 같다.

- Random Forest, XGBoost 등 비선형 모델과 비교
- 뉴스 감성, 시장 지수, 환율, 금리 등 외부 변수 추가
- 기업별 개별 모델과 전체 통합 모델 성능 비교
- 예측 목표를 다음 날 상승/하락이 아니라 3일 또는 5일 후 방향으로 변경
- 상승/하락 기준을 단순 0% 초과가 아니라 거래비용을 고려한 임계값으로 재정의

결론적으로 Logistic Regression은 해석 가능한 baseline 모델로는 의미가 있지만, 최종 예측 모델로 사용하기에는 한계가 있다. 현재 단계에서는 Step 2를 Logistic Regression 기반 최종 개선안으로 사용하고, 이후 비선형 모델과의 비교를 통해 추가 성능 개선을 시도하는 것이 적절하다.
