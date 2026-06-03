from __future__ import annotations

from zipfile import ZIP_DEFLATED, ZipFile

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


OUT_PATH = OUT_DIR / "model1_detailed_report_presentation.pptx"


def img_slide(title: str, image_name: str, image_title: str, notes: list[str], fs: int = 15) -> tuple[str, str]:
    return (
        slide_xml(
            shape(2, "Title", 450_000, 230_000, 12_550_000, 520_000, [title], 27, True)
            + picture(3, image_title, "rId2", 430_000, 930_000, 7_250_000, 5_650_000)
            + shape(4, "Explanation", 7_950_000, 930_000, 4_980_000, 5_650_000, notes, fs, True)
        ),
        image_name,
    )


def text_slide(title: str, lines: list[str], fs: int = 18) -> tuple[str, None]:
    return (
        slide_xml(
            shape(2, "Title", 520_000, 330_000, 12_300_000, 560_000, [title], 28, True)
            + shape(3, "Body", 760_000, 1_130_000, 11_900_000, 5_650_000, lines, fs, True)
        ),
        None,
    )


def make_slides(summary: dict[str, str]) -> list[tuple[str, str | None]]:
    return [
        text_slide(
            "Logistic Regression 기반 주가 방향 예측 분석",
            [
                "발표 목표",
                "주가 데이터와 Google Trends 검색량을 결합해 다음 거래일 주가 방향을 예측한다.",
                "모델 성능만 제시하는 것이 아니라, 왜 성능이 낮게 나왔는지 데이터와 심리 신호 관점에서 해석한다.",
                "발표 흐름: 데이터 구성 -> 주요 변수 설명 -> 시각화 해석 -> 모델 결과 -> 심리학적 해석 -> 개선 방향",
            ],
            21,
        ),
        text_slide(
            "데이터셋 구성",
            [
                "데이터셋",
                "국내 주요 6개 기업의 주가 데이터와 Google Trends 검색량 데이터를 결합했다.",
                f"분석 기간: {summary['start']} ~ {summary['end']}",
                f"전체 표본 수: {summary['rows']}개",
                "분할: Train 914개, Validation 196개, Test 197개",
                "예측 목표: 다음 거래일 주가가 상승하면 1, 상승하지 않거나 하락하면 0으로 분류한다.",
                "주의점: 이 데이터는 시계열이므로 시간 순서를 섞지 않고 학습/검증/테스트를 나누었다.",
            ],
            19,
        ),
        text_slide(
            "주가 기반 피처 설명",
            [
                "주가 기반 피처",
                "Open, High, Low, Close는 하루 동안의 가격 수준과 가격 위치를 보여준다.",
                "Volume은 실제 매매 참여 규모를 나타내며, 시장 관심이 실제 거래로 이어졌는지 확인하는 데 중요하다.",
                "return_lag1은 직전 거래일 수익률, return_lag3_mean은 최근 3일 평균 수익률이다.",
                "ma5_gap, ma20_gap은 현재 가격이 단기/중기 이동평균 대비 얼마나 위 또는 아래에 있는지 나타낸다.",
                "volatility_7은 최근 7일 변동성으로, 시장이 불안정한지 안정적인지 보여준다.",
            ],
            18,
        ),
        text_slide(
            "검색 트렌드 피처와 weighted_trend",
            [
                "검색 트렌드 피처",
                "trend_kor: 국내 Google Trends 검색량을 0~100 범위로 정리한 값이다.",
                "trend_glb: 글로벌 Google Trends 검색량을 0~100 범위로 정리한 값이다.",
                "foreign_ratio: 해당 기업 주식에서 외국인 투자자 비중을 반영하기 위한 값이다.",
                "weighted_trend = foreign_ratio * trend_glb + (1 - foreign_ratio) * trend_kor",
                "의미: 외국인 비중이 높은 기업은 글로벌 검색 관심을 더 크게 반영하고, 국내 비중이 높은 기업은 국내 검색 관심을 더 크게 반영한다.",
                "따라서 weighted_trend는 단순 검색량이 아니라 국내/해외 투자자 관심도를 합친 심리 지표로 해석할 수 있다.",
            ],
            17,
        ),
        text_slide(
            "지연 검색량 변수의 의미",
            [
                "trend_lag1, trend_lag3_mean, trend_lag7_mean",
                "검색량은 주가에 반드시 당일 바로 반영되지 않는다.",
                "투자자는 뉴스를 보고 검색하고, 정보를 확인한 뒤, 매수/매도 결정을 내린다.",
                "이 과정에는 시간 지연이 생길 수 있으므로 직전 1일, 최근 3일, 최근 7일 검색량 평균을 사용했다.",
                "trend_change는 검색량이 갑자기 증가하거나 감소했는지 보는 변수다.",
                "이 변수들은 투자자의 관심 변화, 불안, 기대감, 이슈 반응을 포착하기 위해 넣었다.",
            ],
            18,
        ),
        img_slide(
            "데이터 특성 시각화: 무엇을 봐야 하나?",
            "image1.png",
            "EDA distribution",
            [
                "이미지 해석",
                "왼쪽 위: target 분포를 보면 상승 클래스가 약간 많지만 극단적인 불균형은 아니다.",
                "오른쪽 위: 기업별 상승/하락 비율이 완전히 같지 않다.",
                "왼쪽 아래: weighted_trend 분포가 target 0과 1을 명확히 나누지 못한다.",
                "오른쪽 아래: return_lag1도 상승/하락 클래스를 깔끔하게 분리하지 못한다.",
                "결론: 모델이 쉽게 구분할 수 있는 단순한 패턴은 데이터에 강하게 나타나지 않는다.",
            ],
        ),
        img_slide(
            "변수 간 상관관계 히트맵 상세 해석",
            "image2.png",
            "Correlation heatmap",
            [
                "이미지 해석",
                "색이 진할수록 두 변수의 선형 관계가 강하다는 뜻이다.",
                "target과 weighted_trend의 상관계수는 약 -0.07로 매우 낮다.",
                "target과 return_lag1의 상관계수도 약 -0.06 수준이다.",
                "즉, 검색량이나 직전 수익률 하나만 보고 다음 날 상승/하락을 예측하기 어렵다.",
                "이 결과는 Logistic Regression처럼 선형 관계를 찾는 모델의 성능이 낮게 나올 수 있음을 미리 보여준다.",
            ],
        ),
        img_slide(
            "주가-검색량 시계열 중첩 그래프 상세 해석",
            "image3.png",
            "Stock-search overlay",
            [
                "이미지 해석",
                "파란색은 Close, 주황색은 weighted_trend이며 단위가 달라 기업별 min-max 정규화했다.",
                "대부분 기업에서 두 선이 안정적으로 같이 움직이지 않는다.",
                "삼성전자 0.13, 한화 0.04, 현대차 -0.02, 네이버 -0.08, LG전자 -0.09로 상관관계가 낮다.",
                "SK하이닉스는 -0.51로 음의 상관이 큰데, 검색량이 높았던 구간 이후 주가가 강하게 상승했기 때문이다.",
                "해석: 검색량 증가는 호재 기대뿐 아니라 악재 불안, 이슈 확인, 단순 관심 증가를 모두 포함한다.",
            ],
            14,
        ),
        text_slide(
            "왜 검색량과 주가가 단순히 같이 움직이지 않을까?",
            [
                "이유 1: 검색량은 방향성이 없다.",
                "검색량 증가는 좋은 뉴스 때문에 생길 수도 있고, 나쁜 뉴스 때문에 생길 수도 있다.",
                "이유 2: 검색 후 매매까지 시간 차가 있다.",
                "투자자는 검색 직후 바로 매매하지 않을 수 있고, 이미 주가가 먼저 움직인 뒤 검색량이 증가할 수도 있다.",
                "이유 3: 주가는 외부 요인의 영향을 크게 받는다.",
                "금리, 환율, 시장 지수, 실적 발표, 업종 흐름, 뉴스 감성 등이 함께 작용한다.",
                "결론: 검색량은 단독 예측 변수보다 투자자 심리를 보완하는 변수로 보는 것이 타당하다.",
            ],
            18,
        ),
        text_slide(
            "실험 설계: 왜 이렇게 나누었나?",
            [
                "모델: Logistic Regression",
                "선택 이유: 빠르고 해석 가능하며, 계수로 feature 영향 방향을 확인할 수 있어 baseline 모델로 적합하다.",
                "분할 방식: Train 70%, Validation 15%, Test 15%",
                "시계열 데이터이므로 랜덤 셔플을 하지 않았다.",
                "교차 검증: TimeSeriesSplit 5 folds",
                "각 fold는 과거 데이터를 학습하고 이후 구간을 검증한다.",
                "이 방식은 미래 정보가 과거 학습에 섞이는 데이터 누수를 줄이기 위한 설정이다.",
            ],
            18,
        ),
        img_slide(
            "시계열 교차 검증 결과 상세 해석",
            "image4.png",
            "CV accuracy",
            [
                "이미지 해석",
                "Fold별 정확도는 0.47~0.55 사이에 머문다.",
                "평균 정확도는 0.5013으로, 무작위 예측 수준인 0.5와 거의 같다.",
                "Fold 4만 0.5461로 상대적으로 높지만, 전체적으로 안정적인 예측력을 보이지 않는다.",
                "이 결과는 모델이 특정 기간에서는 조금 맞지만, 전체 시계열에서 반복적으로 통하는 패턴을 잡지 못했다는 뜻이다.",
                "주의: 0.5013은 baseline 모델의 교차 검증 평균 정확도이다.",
            ],
        ),
        img_slide(
            "Test Set 성능과 Confusion Matrix 상세 해석",
            "image5.png",
            "Confusion matrix",
            [
                "이미지 해석",
                "Test Accuracy는 0.4924로 무작위 수준보다 낮다.",
                "실제 하락/비상승 91개 중 49개를 맞히고 42개를 상승으로 잘못 예측했다.",
                "실제 상승 106개 중 48개만 맞히고 58개를 하락으로 잘못 예측했다.",
                "Recall이 0.4528로 낮다는 것은 실제 상승 기회를 놓치는 경우가 많다는 뜻이다.",
                "투자 관점에서는 상승 기회를 놓치는 FN이 많다는 점이 큰 한계다.",
            ],
        ),
        img_slide(
            "ROC Curve 상세 해석",
            "image6.png",
            "ROC curve",
            [
                "이미지 해석",
                "ROC-AUC는 0.4857이다.",
                "ROC Curve가 대각선 기준선과 거의 비슷하다.",
                "대각선은 모델이 상승/하락을 구분하지 못하고 거의 랜덤하게 맞히는 기준선이다.",
                "따라서 이 모델의 예측 확률은 상승 샘플에 더 높은 점수를 주는 능력이 약하다.",
                "결론: baseline Logistic Regression만으로는 분류력이 충분하지 않다.",
            ],
        ),
        img_slide(
            "하이퍼파라미터 C 변경 효과 상세 해석",
            "image7.png",
            "Hyperparameter effect",
            [
                "이미지 해석",
                "C는 정규화 강도를 조절하는 값이다. C가 작을수록 강한 정규화가 적용된다.",
                "C=0.001에서 Validation Accuracy 0.5153, ROC-AUC 0.5316으로 가장 좋았다.",
                "하지만 가장 좋은 값도 0.5 근처라 성능 개선 폭은 작다.",
                "이는 단순히 정규화 강도를 조절하는 것만으로는 데이터의 복잡한 패턴을 잡기 어렵다는 뜻이다.",
                "비선형 모델이나 외부 변수 추가가 필요한 이유다.",
            ],
        ),
        img_slide(
            "피처 중요도: 어떤 변수가 모델 판단에 쓰였나?",
            "image8.png",
            "Coefficients",
            [
                "이미지 해석",
                "계수 절댓값이 클수록 Logistic Regression 판단에 더 큰 영향을 준 변수다.",
                "trend_lag3_mean, weighted_trend, trend_lag1이 상위에 포함되어 검색 트렌드가 모델 판단에 사용되었다.",
                "Open, Close, ma20도 중요하게 나타나 실제 가격 수준과 추세가 함께 반영되었다.",
                "다만 중요한 변수로 쓰였다는 것과 예측 성능이 높다는 것은 다르다.",
                "검색 트렌드는 신호로 사용되었지만, 상승/하락을 안정적으로 구분할 만큼 강한 신호는 아니었다.",
            ],
            14,
        ),
        text_slide(
            "피처 중요도 기반 심리학적 해석",
            [
                "심리학적 해석",
                "weighted_trend는 투자자의 정보 탐색 행동과 시장 관심도를 반영하는 대리 변수다.",
                "검색량 증가는 투자자가 해당 기업을 더 많이 신경 쓰기 시작했다는 뜻으로 볼 수 있다.",
                "trend_lag1, trend_lag3_mean은 관심 증가가 당일이 아니라 며칠 뒤 의사결정에 영향을 줄 가능성을 반영한다.",
                "하지만 검색량 증가는 좋은 관심과 나쁜 관심을 구분하지 못한다.",
                "따라서 검색 트렌드는 투자자 심리의 강도는 보여주지만, 심리의 방향이 긍정인지 부정인지는 별도 정보가 필요하다.",
            ],
            18,
        ),
        text_slide(
            "외부 요인이 부족하면 왜 해석이 어려운가?",
            [
                "외부 요인의 필요성",
                "검색량이 증가한 이유가 호재 뉴스인지 악재 뉴스인지 알 수 없으면 주가 방향을 해석하기 어렵다.",
                "금리 상승은 성장주에 부담이 될 수 있고, 환율 변화는 수출 기업에 영향을 줄 수 있다.",
                "시장 지수가 하락하는 날에는 개별 기업 검색량이 높아도 주가가 함께 하락할 수 있다.",
                "실적 발표, 산업 이슈, 정책 변화, 업종 흐름도 주가에 큰 영향을 준다.",
                "따라서 검색량 변수는 뉴스 감성, 시장 지수, 금리, 환율, 거래량 변화와 결합해야 더 의미 있는 심리 지표가 된다.",
            ],
            18,
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["예측 확률 분포와 Learning Curve"], 27, True)
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
                        "왼쪽: 실제 0과 1의 예측 확률 분포가 겹쳐 있어 모델이 확신 있게 구분하지 못한다.",
                        "오른쪽: 학습 정확도 자체도 높지 않아 과적합보다는 언더피팅 성격이 크다.",
                    ],
                    14,
                )
            ),
            "image9.png,image10.png",
        ),
        img_slide(
            "단계적 성능 개선 실험",
            "image11.png",
            "Metric comparison",
            [
                "이미지 해석",
                "Baseline은 Test Accuracy 0.4924, F1 0.4898, ROC-AUC 0.4857이다.",
                "Step 2는 SelectKBest top12 + C=0.001 + class_weight=balanced를 적용한 개선안이다.",
                "Step 2 Test Accuracy는 0.5431, Precision 0.5889, Recall 0.5000, F1 0.5408, ROC-AUC 0.5180이다.",
                "0.5013은 baseline 교차 검증 평균이고, 0.5431은 Step 2 Test Set 결과이므로 평가 단계가 다르다.",
                "Step 2는 모든 주요 지표가 baseline보다 개선되었지만 절대 성능은 여전히 높지 않다.",
            ],
            14,
        ),
        img_slide(
            "최종 개선안의 Confusion Matrix 비교",
            "image12.png",
            "Stepwise confusion matrices",
            [
                "이미지 해석",
                "Step 1은 Recall이 크게 좋아졌지만 상승으로 많이 예측해 False Positive가 늘었다.",
                "Step 3은 거의 모든 샘플을 상승으로 예측해 F1은 높아 보이지만 일반적 분류 모델로는 부적합하다.",
                "Step 2는 Precision과 Recall의 균형이 상대적으로 좋고 한쪽 클래스로 과도하게 치우치지 않는다.",
                "따라서 Logistic Regression 내부에서는 Step 2를 가장 해석 가능한 개선안으로 볼 수 있다.",
                "다만 이 역시 최종 모델로 쓰기에는 성능이 충분하지 않다.",
            ],
            14,
        ),
        text_slide(
            "최종 결론",
            [
                "최종 결론",
                "Logistic Regression은 빠르고 해석 가능하므로 baseline 모델로는 의미가 있다.",
                "하지만 Test Accuracy 0.4924, ROC-AUC 0.4857로 기본 모델의 예측력은 낮다.",
                "Step 2 개선안은 Test Accuracy 0.5431까지 개선되었지만 여전히 높은 성능은 아니다.",
                "검색 트렌드 변수는 모델 판단에 사용되었고, 투자자 관심/심리 신호로 해석할 수 있다.",
                "그러나 검색량은 긍정/부정 방향을 구분하지 못하기 때문에 단독 예측 신호로는 한계가 있다.",
                "향후에는 Random Forest, XGBoost 같은 비선형 모델과 뉴스 감성, 시장 지수, 환율, 금리 등 외부 변수를 함께 활용해야 한다.",
            ],
            18,
        ),
        text_slide(
            "발표 마무리 한 문장",
            [
                "핵심 메시지",
                "검색량은 사람들이 어떤 기업에 얼마나 관심을 가지는지를 보여주는 심리적 신호다.",
                "하지만 관심이 항상 매수나 주가 상승을 의미하지는 않는다.",
                "이번 Logistic Regression 결과는 주가 방향 예측이 단순 검색량과 선형 모델만으로는 어렵다는 점을 보여준다.",
                "따라서 검색량은 뉴스 감성, 시장 상황, 가격 추세와 함께 해석할 때 더 의미 있는 투자자 심리 지표가 된다.",
            ],
            21,
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
