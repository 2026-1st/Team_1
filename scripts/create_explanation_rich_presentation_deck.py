from __future__ import annotations

from zipfile import ZIP_DEFLATED, ZipFile

from create_detailed_report_presentation_deck import (
    img_slide,
    rels_for_images,
    text_slide,
)
from create_eda_slide_deck import (
    FIGURES,
    OUT_DIR,
    app_xml,
    content_types,
    core_xml,
    load_summary,
    package_rels,
    picture,
    presentation_rels,
    presentation_xml,
    rels_xml,
    shape,
    slide_layout_rels,
    slide_layout_xml,
    slide_master_rels,
    slide_master_xml,
    slide_xml,
    theme_xml,
)


OUT_PATH = OUT_DIR / "model1_explanation_rich_presentation.pptx"


def make_slides(summary: dict[str, str]) -> list[tuple[str, str | None]]:
    return [
        text_slide(
            "Logistic Regression 기반 주가 방향 예측 분석",
            [
                "발표 목표",
                "주가 데이터와 Google Trends 검색량 데이터를 결합해 다음 거래일 주가 방향을 예측한다.",
                "단순히 정확도만 보는 것이 아니라, 데이터가 어떤 특성을 갖는지, 모델이 왜 잘 맞히지 못했는지 설명한다.",
                "핵심 질문: 검색량은 투자자 심리를 반영하는가? 그리고 그 심리가 실제 주가 방향 예측에 도움이 되는가?",
                "결론 미리보기: 검색량은 심리 신호로 의미가 있지만, 단독으로 주가 방향을 안정적으로 예측하기에는 부족하다.",
            ],
            20,
        ),
        text_slide(
            "분석 문제를 쉽게 설명하면",
            [
                "이 프로젝트의 문제 정의",
                "오늘까지의 주가와 검색량 정보를 보고, 다음 거래일 주가가 오를지 예측하는 문제다.",
                "예측값은 두 가지다.",
                "1 = 다음 거래일 주가 상승",
                "0 = 다음 거래일 주가 하락 또는 상승하지 않음",
                "즉, 주가를 정확히 얼마로 맞히는 회귀 문제가 아니라, 상승/비상승을 구분하는 분류 문제다.",
                "그래서 Accuracy, Precision, Recall, F1, ROC-AUC 같은 분류 지표를 사용했다.",
            ],
            18,
        ),
        text_slide(
            "데이터셋 구성",
            [
                "사용 데이터",
                "국내 주요 6개 기업의 주가 데이터와 Google Trends 검색량 데이터를 결합했다.",
                f"분석 기간: {summary['start']} ~ {summary['end']}",
                f"전체 표본 수: {summary['rows']}개",
                "분할 수: Train 914개, Validation 196개, Test 197개",
                "시간 순서가 중요한 데이터이므로, 무작위로 섞지 않고 과거에서 미래 방향으로 나누었다.",
                "이렇게 해야 미래 정보를 과거 학습에 사용하는 데이터 누수를 줄일 수 있다.",
            ],
            18,
        ),
        text_slide(
            "주가 기반 피처 설명",
            [
                "주가 기반 피처가 담고 있는 정보",
                "Open, High, Low, Close: 하루 동안 가격이 어느 수준에서 움직였는지 보여준다.",
                "Volume: 실제 거래가 얼마나 활발했는지 보여준다.",
                "return_lag1: 직전 거래일 수익률로, 최근 가격 반응을 반영한다.",
                "return_lag3_mean: 최근 3일 평균 수익률로, 단기 흐름을 완화해서 본다.",
                "ma5_gap, ma20_gap: 현재 가격이 5일/20일 이동평균 대비 얼마나 떨어져 있는지 나타낸다.",
                "volatility_7: 최근 7일간 가격 변동성이 커졌는지 확인한다.",
            ],
            17,
        ),
        text_slide(
            "검색 트렌드 피처 설명",
            [
                "검색 트렌드 피처가 담고 있는 정보",
                "trend_kor: 국내에서 해당 기업을 얼마나 검색했는지 나타내는 Google Trends 값이다.",
                "trend_glb: 글로벌 기준으로 해당 기업 검색 관심도를 나타낸 값이다.",
                "검색량은 0~100 범위로 정규화된 상대적 관심도이다.",
                "검색량이 높다는 것은 사람들이 그 기업에 대해 더 많이 찾아봤다는 뜻이다.",
                "하지만 검색량만으로는 그 관심이 긍정적인 관심인지, 부정적인 불안인지 구분할 수 없다.",
            ],
            18,
        ),
        text_slide(
            "weighted_trend는 무엇인가?",
            [
                "weighted_trend 정의",
                "weighted_trend = foreign_ratio * trend_glb + (1 - foreign_ratio) * trend_kor",
                "foreign_ratio는 외국인 투자자 비중을 의미한다.",
                "외국인 비중이 높은 기업은 글로벌 검색 관심도가 더 중요할 수 있다.",
                "국내 투자자 비중이 높은 기업은 국내 검색 관심도가 더 중요할 수 있다.",
                "따라서 weighted_trend는 국내 검색량과 글로벌 검색량을 기업 특성에 맞게 섞은 관심도 지표다.",
                "발표에서는 이를 투자자 관심도 또는 심리 신호의 대리 변수로 설명하면 된다.",
            ],
            17,
        ),
        text_slide(
            "weighted_trend 예시로 이해하기",
            [
                "예시",
                "어떤 기업의 foreign_ratio가 0.60이라고 가정한다.",
                "trend_glb가 80, trend_kor가 40이라면 weighted_trend는 다음과 같다.",
                "0.60 * 80 + 0.40 * 40 = 64",
                "즉, 외국인 비중이 높기 때문에 글로벌 검색량의 영향이 더 크게 반영된다.",
                "이 변수는 단순히 사람들이 검색한 횟수가 아니라, 국내/해외 투자자 관심을 함께 반영한 값이다.",
                "그래서 심리학적으로는 '집단적 관심 변화'를 나타내는 변수로 볼 수 있다.",
            ],
            18,
        ),
        text_slide(
            "trend_lag 변수는 왜 필요한가?",
            [
                "지연 검색량 변수의 의미",
                "trend_lag1은 하루 전 검색 관심도이다.",
                "trend_lag3_mean은 최근 3일 평균 검색 관심도이다.",
                "trend_lag7_mean은 최근 7일 평균 검색 관심도이다.",
                "투자자는 뉴스를 보고 바로 매매하지 않을 수도 있다.",
                "검색 -> 정보 확인 -> 판단 -> 매매 행동까지 시간이 걸릴 수 있다.",
                "그래서 검색량의 당일 값뿐 아니라 며칠 전 검색량과 평균 검색량도 모델에 넣었다.",
            ],
            18,
        ),
        text_slide(
            "데이터 특성을 보기 전에 알아야 할 점",
            [
                "이미지를 볼 때의 기준",
                "우리는 먼저 target 0과 target 1이 데이터상에서 잘 구분되는지 확인해야 한다.",
                "만약 검색량이나 수익률 분포가 target별로 확실히 나뉜다면 모델이 쉽게 학습할 수 있다.",
                "반대로 두 클래스의 분포가 많이 겹치면, 모델은 상승/하락을 구분하기 어렵다.",
                "따라서 EDA 이미지는 모델이 왜 잘 맞히거나 못 맞히는지 이해하기 위한 첫 단서다.",
            ],
            18,
        ),
        img_slide(
            "데이터 특성 시각화 상세 설명",
            "image1.png",
            "EDA distribution",
            [
                "이미지에서 볼 것",
                "1. target 분포: 상승 클래스가 조금 많지만 극단적 불균형은 아니다.",
                "2. 기업별 target 분포: 기업마다 상승/하락 비율 차이가 있다.",
                "3. weighted_trend 분포: target 0과 1이 명확히 분리되지 않는다.",
                "4. return_lag1 분포: 직전 수익률도 상승/하락을 강하게 구분하지 못한다.",
                "해석: 데이터 자체에 쉬운 분리 기준이 약하므로 모델 성능이 낮게 나올 가능성이 있다.",
            ],
            14,
        ),
        img_slide(
            "상관관계 히트맵 상세 설명",
            "image2.png",
            "Correlation heatmap",
            [
                "이미지에서 볼 것",
                "히트맵은 변수 간 선형 관계를 색으로 보여준다.",
                "target과 weighted_trend의 상관계수는 약 -0.07로 매우 낮다.",
                "target과 return_lag1도 약 -0.06 수준으로 낮다.",
                "즉, 검색량이 높으면 다음 날 상승한다는 단순한 선형 규칙이 강하지 않다.",
                "Logistic Regression은 선형 경계를 찾는 모델이므로 이런 데이터에서는 성능이 제한될 수 있다.",
            ],
            14,
        ),
        img_slide(
            "주가-검색량 시계열 중첩 그래프 상세 설명",
            "image3.png",
            "Stock-search overlay",
            [
                "이미지에서 볼 것",
                "파란색은 Close, 주황색은 weighted_trend이다.",
                "두 변수는 단위가 달라서 기업별 min-max 정규화 후 비교했다.",
                "대부분 기업에서 두 선이 안정적으로 같이 움직이지 않는다.",
                "상관계수는 삼성전자 0.13, 한화 0.04, 현대차 -0.02, 네이버 -0.08, LG전자 -0.09, SK하이닉스 -0.51이다.",
                "해석: 검색량은 관심도를 보여주지만, 그 관심이 바로 주가 상승으로 이어지지는 않는다.",
            ],
            13,
        ),
        text_slide(
            "왜 검색량과 주가가 단순히 같이 움직이지 않을까?",
            [
                "이유 1: 검색량은 방향성이 없다.",
                "검색량 증가는 좋은 뉴스에 대한 기대감일 수도 있고, 나쁜 뉴스에 대한 불안감일 수도 있다.",
                "이유 2: 검색과 매매 사이에는 시간 차가 있다.",
                "검색이 먼저 나오고 주가가 나중에 움직일 수도 있고, 주가가 먼저 움직인 뒤 검색량이 늘 수도 있다.",
                "이유 3: 주가는 외부 요인의 영향을 크게 받는다.",
                "시장 지수, 금리, 환율, 실적 발표, 업종 흐름, 뉴스 감성 등이 검색량보다 더 강하게 작용할 수 있다.",
                "따라서 검색량은 단독 예측 신호보다 심리 보조 지표로 보는 것이 적절하다.",
            ],
            17,
        ),
        text_slide(
            "실험 설계 상세 설명",
            [
                "모델과 평가 방식",
                "모델은 Logistic Regression을 사용했다.",
                "이 모델은 빠르고 해석 가능하며, 계수를 통해 어떤 변수가 판단에 영향을 주는지 볼 수 있다.",
                "데이터 분할은 Train 70%, Validation 15%, Test 15%이다.",
                "교차 검증은 TimeSeriesSplit 5 folds를 사용했다.",
                "일반 K-Fold처럼 섞지 않은 이유는 주가 데이터가 시간 순서를 가진 시계열 데이터이기 때문이다.",
                "평가 지표는 Accuracy, Precision, Recall, F1 Score, Confusion Matrix, ROC-AUC를 함께 사용했다.",
            ],
            17,
        ),
        text_slide(
            "평가 지표를 쉽게 이해하기",
            [
                "Accuracy",
                "전체 예측 중 맞힌 비율이다. 하지만 상승/하락 중 어떤 쪽을 잘 맞혔는지는 알려주지 않는다.",
                "Precision",
                "모델이 상승이라고 예측한 것 중 실제 상승한 비율이다.",
                "Recall",
                "실제 상승한 것 중 모델이 상승으로 잡아낸 비율이다. 상승 기회를 놓치지 않는 능력과 관련 있다.",
                "F1 Score",
                "Precision과 Recall의 균형을 보는 지표다.",
                "ROC-AUC",
                "예측 확률이 상승과 하락을 얼마나 잘 구분하는지 보는 지표다.",
            ],
            16,
        ),
        img_slide(
            "교차 검증 결과 상세 설명",
            "image4.png",
            "CV accuracy",
            [
                "이미지에서 볼 것",
                "Fold별 정확도는 0.4868, 0.4934, 0.4737, 0.5461, 0.5066이다.",
                "평균 정확도는 0.5013이다.",
                "이는 무작위 예측 수준인 0.5와 거의 같다.",
                "Fold 4만 상대적으로 높지만, 전체적으로 반복해서 안정적인 성능이 나오지 않는다.",
                "해석: 모델이 특정 기간에만 약간 맞고, 전체 시계열에 통하는 규칙은 잘 찾지 못했다.",
            ],
            14,
        ),
        img_slide(
            "Test Set 성능과 Confusion Matrix 상세 설명",
            "image5.png",
            "Confusion matrix",
            [
                "이미지에서 볼 것",
                "Actual 0 중 49개는 맞혔고 42개는 상승으로 잘못 예측했다.",
                "Actual 1 중 48개는 맞혔고 58개는 하락으로 잘못 예측했다.",
                "실제 상승 106개 중 48개만 잡았기 때문에 Recall이 0.4528로 낮다.",
                "투자 관점에서는 실제 상승 기회를 놓치는 FN이 많다는 점이 문제다.",
                "결론: baseline 모델은 상승 신호를 충분히 포착하지 못했다.",
            ],
            14,
        ),
        img_slide(
            "ROC Curve 상세 설명",
            "image6.png",
            "ROC curve",
            [
                "이미지에서 볼 것",
                "ROC-AUC는 0.4857이다.",
                "대각선은 랜덤 예측 수준을 의미한다.",
                "곡선이 대각선과 거의 겹친다는 것은 상승과 하락의 확률 점수를 잘 구분하지 못했다는 뜻이다.",
                "AUC가 0.5보다 낮거나 비슷하면 모델의 분류력이 매우 약하다고 볼 수 있다.",
                "결론: baseline Logistic Regression은 확률 기반 구분 능력도 낮다.",
            ],
            14,
        ),
        img_slide(
            "하이퍼파라미터 C 변경 결과 상세 설명",
            "image7.png",
            "Hyperparameter effect",
            [
                "이미지에서 볼 것",
                "C는 정규화 강도와 관련된 값이다.",
                "C가 작을수록 강한 정규화가 적용되어 계수가 과도하게 커지는 것을 막는다.",
                "C=0.001에서 Validation Accuracy 0.5153, ROC-AUC 0.5316으로 가장 좋았다.",
                "하지만 가장 좋은 값도 0.5 근처에 머문다.",
                "해석: C 조정만으로는 데이터의 복잡한 패턴을 충분히 학습하기 어렵다.",
            ],
            14,
        ),
        img_slide(
            "피처 중요도 그래프 상세 설명",
            "image8.png",
            "Coefficients",
            [
                "이미지에서 볼 것",
                "Logistic Regression의 계수는 각 변수가 예측에 미치는 영향을 보여준다.",
                "trend_lag3_mean, weighted_trend, trend_lag1이 상위에 있어 검색 트렌드가 모델 판단에 사용되었다.",
                "Open, Close, ma20도 상위에 있어 실제 가격 수준과 추세도 중요하게 반영되었다.",
                "하지만 중요 변수로 쓰였다는 것이 곧 높은 성능을 의미하지는 않는다.",
                "검색량은 심리 신호로 쓰였지만, 상승/하락 방향을 안정적으로 구분하기에는 정보가 부족했다.",
            ],
            13,
        ),
        text_slide(
            "피처 중요도 기반 심리학적 해석",
            [
                "심리학적 해석",
                "검색량은 투자자의 정보 탐색 행동을 반영한다.",
                "weighted_trend가 중요하게 나온 것은 국내/해외 투자자의 관심 변화가 모델 판단에 일부 사용되었다는 뜻이다.",
                "trend_lag1, trend_lag3_mean이 중요하게 나온 것은 투자자 심리가 당일이 아니라 며칠 뒤 행동에 연결될 가능성을 보여준다.",
                "하지만 검색량 증가는 긍정적 기대와 부정적 불안을 모두 포함한다.",
                "따라서 검색량은 심리의 강도는 보여주지만, 방향성은 뉴스 감성 같은 추가 정보가 있어야 알 수 있다.",
            ],
            17,
        ),
        text_slide(
            "성능이 낮게 나온 이유를 종합하면",
            [
                "이유 1: target과 주요 feature의 선형 상관관계가 낮았다.",
                "Logistic Regression은 선형 관계를 잘 활용하는 모델이므로, 선형 패턴이 약하면 성능이 제한된다.",
                "이유 2: 검색량은 방향성이 부족하다.",
                "검색량이 높아도 호재 관심인지 악재 불안인지 구분되지 않는다.",
                "이유 3: 외부 요인이 부족하다.",
                "금리, 환율, 시장 지수, 뉴스 감성, 실적 발표 등이 빠져 있어 실제 주가 변동을 충분히 설명하지 못한다.",
                "이유 4: 주가 방향 예측 자체가 비선형적이고 잡음이 많은 문제다.",
            ],
            17,
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["예측 확률 분포와 Learning Curve 상세 설명"], 27, True)
                + picture(3, "Probability distribution", "rId2", 520_000, 1_020_000, 5_650_000, 4_900_000)
                + picture(4, "Learning curve", "rId3", 6_620_000, 1_020_000, 5_650_000, 4_900_000)
                + shape(
                    5,
                    "Notes",
                    750_000,
                    6_120_000,
                    11_900_000,
                    720_000,
                    [
                        "왼쪽: 실제 0과 1의 예측 확률 분포가 겹쳐 모델이 확신 있게 구분하지 못한다.",
                        "오른쪽: 학습 정확도 자체도 높지 않아 과적합보다 언더피팅 성격이 크다.",
                    ],
                    14,
                )
            ),
            "image9.png,image10.png",
        ),
        img_slide(
            "단계적 성능 개선 실험 상세 설명",
            "image11.png",
            "Metric comparison",
            [
                "이미지에서 볼 것",
                "Baseline은 Test Accuracy 0.4924, F1 0.4898, ROC-AUC 0.4857이다.",
                "Step 2는 SelectKBest top12 + C=0.001 + class_weight=balanced를 적용했다.",
                "Step 2 Test Accuracy는 0.5431, Precision 0.5889, Recall 0.5000, F1 0.5408, ROC-AUC 0.5180이다.",
                "0.5013은 baseline 교차 검증 평균, 0.5431은 Step 2 Test Set 결과이므로 서로 다른 지표다.",
                "개선은 있었지만 절대 성능은 여전히 낮아 최종 모델로 쓰기에는 부족하다.",
            ],
            13,
        ),
        img_slide(
            "Confusion Matrix 개선 비교 상세 설명",
            "image12.png",
            "Stepwise confusion matrices",
            [
                "이미지에서 볼 것",
                "Step 1은 Recall이 좋아졌지만 상승으로 많이 예측해 False Positive가 늘었다.",
                "Step 3은 거의 모든 샘플을 상승으로 예측해 F1은 높아 보이나 실제 구분 능력은 약하다.",
                "Step 2는 Precision과 Recall의 균형이 상대적으로 좋고 한쪽 클래스로 심하게 치우치지 않는다.",
                "그래서 Logistic Regression 내부에서는 Step 2가 가장 해석 가능한 개선안이다.",
                "하지만 ROC-AUC가 0.5180 수준이라 여전히 강한 예측 모델이라고 보기는 어렵다.",
            ],
            13,
        ),
        text_slide(
            "후속 개선 방향을 구체적으로 말하면",
            [
                "모델 개선",
                "Random Forest, XGBoost 같은 비선형 모델을 사용하면 변수 간 복잡한 상호작용을 반영할 수 있다.",
                "외부 변수 추가",
                "뉴스 감성: 검색량 증가가 긍정적 관심인지 부정적 불안인지 구분한다.",
                "시장 지수: 전체 시장이 상승장인지 하락장인지 반영한다.",
                "환율/금리: 거시경제 환경이 기업 주가에 미치는 영향을 반영한다.",
                "업종 지수와 실적 발표 여부: 개별 기업 이슈와 산업 흐름을 보완한다.",
            ],
            17,
        ),
        text_slide(
            "최종 결론",
            [
                "최종 결론",
                "Logistic Regression은 해석 가능한 baseline 모델로는 의미가 있다.",
                "하지만 baseline Test Accuracy 0.4924, ROC-AUC 0.4857로 성능은 낮다.",
                "Step 2 개선안은 Test Accuracy 0.5431까지 개선되었지만 여전히 충분히 높은 수준은 아니다.",
                "검색 트렌드 변수는 투자자 관심과 심리를 반영하는 신호로 볼 수 있다.",
                "그러나 검색량은 긍정/부정 방향성을 구분하지 못하므로 단독 예측 신호로는 한계가 있다.",
                "검색량은 뉴스 감성, 시장 상황, 가격 추세, 거시경제 변수와 함께 사용할 때 더 의미 있는 지표가 된다.",
            ],
            17,
        ),
        text_slide(
            "발표 때 마지막으로 강조할 문장",
            [
                "마무리 문장",
                "이번 분석은 검색량이 투자자의 관심과 심리를 반영할 수 있다는 가능성을 보여준다.",
                "하지만 사람들이 많이 검색했다는 사실만으로 주가가 오른다고 말할 수는 없다.",
                "검색량은 호재 기대와 악재 불안을 모두 포함하기 때문이다.",
                "따라서 검색량은 단독 예측 변수라기보다, 뉴스 감성 및 시장 변수와 결합했을 때 의미 있는 심리 지표가 된다.",
            ],
            20,
        ),
    ]


def rels_for_images(image_names: list[str]) -> str:
    parts = [
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
    ]
    for idx, name in enumerate(image_names, start=2):
        parts.append(
            f'<Relationship Id="rId{idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{name}"/>'
        )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {"".join(parts)}
</Relationships>"""


def write_deck() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image_map = {
        "image1.png": FIGURES / "01_eda_distribution.png",
        "image2.png": FIGURES / "02_feature_correlation.png",
        "image3.png": FIGURES / "10_stock_search_overlay.png",
        "image4.png": FIGURES / "03_cv_accuracy.png",
        "image5.png": FIGURES / "04_confusion_matrix.png",
        "image6.png": FIGURES / "05_roc_curve.png",
        "image7.png": FIGURES / "09_hyperparameter_effect.png",
        "image8.png": FIGURES / "06_coefficients.png",
        "image9.png": FIGURES / "07_probability_distribution.png",
        "image10.png": FIGURES / "08_learning_curve.png",
        "image11.png": FIGURES / "01_stepwise_metric_comparison.png",
        "image12.png": FIGURES / "02_stepwise_confusion_matrices.png",
    }
    missing = [str(path) for path in image_map.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing figure files: " + ", ".join(missing))

    slides = make_slides(load_summary())

    with ZipFile(OUT_PATH, "w", ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types(len(slides)))
        z.writestr("_rels/.rels", package_rels())
        z.writestr("docProps/app.xml", app_xml(len(slides)))
        z.writestr("docProps/core.xml", core_xml())
        z.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(slides)))
        z.writestr("ppt/theme/theme1.xml", theme_xml())
        z.writestr("ppt/slideMasters/slideMaster1.xml", slide_master_xml())
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels())
        z.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout_xml())
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels())
        for idx, (xml, image_names) in enumerate(slides, start=1):
            z.writestr(f"ppt/slides/slide{idx}.xml", xml)
            if image_names is None:
                z.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", rels_xml())
            elif "," in image_names:
                z.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", rels_for_images(image_names.split(",")))
            else:
                z.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", rels_xml("rId2", f"../media/{image_names}"))
        for name, path in image_map.items():
            z.write(path, f"ppt/media/{name}")
    print(OUT_PATH)


if __name__ == "__main__":
    write_deck()
