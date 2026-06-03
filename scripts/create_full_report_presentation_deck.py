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


OUT_PATH = OUT_DIR / "model1_full_report_presentation.pptx"


def make_slides(summary: dict[str, str]) -> list[tuple[str, str | None]]:
    return [
        (
            slide_xml(
                shape(2, "Title", 600_000, 520_000, 12_100_000, 800_000, ["Logistic Regression 기반 주가 방향 예측 분석"], 30, True)
                + shape(
                    3,
                    "Subtitle",
                    900_000,
                    1_640_000,
                    11_500_000,
                    4_700_000,
                    [
                        "발표 흐름",
                        "1. 데이터셋 구성과 주요 피처",
                        "2. 데이터 특성 및 변수 간 상관관계",
                        "3. 주가-검색량 시계열 관계",
                        "4. Logistic Regression 실험 설계와 성능 평가",
                        "5. 피처 중요도 기반 심리학적 해석",
                        "6. 모델 개선 실험과 최종 결론",
                    ],
                    21,
                    True,
                )
            ),
            None,
        ),
        (
            slide_xml(
                shape(2, "Title", 500_000, 300_000, 12_300_000, 560_000, ["데이터셋 구성"], 28, True)
                + shape(
                    3,
                    "Dataset",
                    760_000,
                    1_140_000,
                    11_900_000,
                    5_520_000,
                    [
                        "분석 대상: 국내 주요 6개 기업",
                        f"분석 기간: {summary['start']} ~ {summary['end']}",
                        f"전체 표본 수: {summary['rows']}개",
                        "데이터 분할: Train 914개, Validation 196개, Test 197개",
                        "예측 목표: 다음 거래일 주가 방향 예측",
                        "Target: 0 = 하락 또는 상승 아님, 1 = 상승",
                        "데이터 출처: 프로젝트 수집 주가 데이터 + Google Trends 검색량 데이터",
                    ],
                    21,
                    False,
                )
            ),
            None,
        ),
        (
            slide_xml(
                shape(2, "Title", 500_000, 300_000, 12_300_000, 560_000, ["주요 피처 구성"], 28, True)
                + shape(
                    3,
                    "Features",
                    760_000,
                    1_160_000,
                    11_900_000,
                    5_300_000,
                    [
                        "주가 기반 피처",
                        "Open, High, Low, Close, Volume",
                        "return_lag1, return_lag3_mean, ma5_gap, ma20_gap, volatility_7",
                        "",
                        "검색 트렌드 기반 피처",
                        "trend_kor, trend_glb, weighted_trend",
                        "trend_lag1, trend_lag3_mean, trend_lag7_mean, trend_change",
                        "",
                        "핵심 아이디어: 가격 흐름 + 투자자 검색 관심도를 함께 사용해 다음 거래일 방향을 예측",
                    ],
                    20,
                    True,
                )
            ),
            None,
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["데이터 특성 시각화"], 28, True)
                + picture(3, "EDA distribution", "rId2", 520_000, 940_000, 7_250_000, 5_770_000)
                + shape(
                    4,
                    "Notes",
                    8_050_000,
                    1_120_000,
                    4_700_000,
                    4_900_000,
                    [
                        "발표 포인트",
                        "상승 클래스가 약간 많지만 극단적 불균형은 아님",
                        "기업별 상승/하락 비율 차이가 존재",
                        "class_weight='balanced'로 클래스 편향 완화",
                        "검색량과 수익률만으로 클래스가 뚜렷하게 분리되지는 않음",
                    ],
                    17,
                    True,
                )
            ),
            "image1.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["변수 간 상관관계 히트맵"], 28, True)
                + picture(3, "Feature correlation heatmap", "rId2", 680_000, 960_000, 6_700_000, 5_600_000)
                + shape(
                    4,
                    "Notes",
                    7_650_000,
                    1_060_000,
                    5_030_000,
                    4_950_000,
                    [
                        "해석",
                        "target과 개별 feature의 선형 상관관계는 전반적으로 낮음",
                        "weighted_trend와 target: 약 -0.07",
                        "return_lag1과 target: 약 -0.06",
                        "단일 변수만으로 주가 방향을 명확히 설명하기 어려움",
                    ],
                    17,
                    True,
                )
            ),
            "image2.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["주가-검색량 시계열 중첩"], 28, True)
                + picture(3, "Stock search overlay", "rId2", 370_000, 900_000, 8_560_000, 5_980_000)
                + shape(
                    4,
                    "Notes",
                    9_180_000,
                    1_060_000,
                    3_900_000,
                    5_100_000,
                    [
                        "해석",
                        "Close와 weighted_trend를 기업별 min-max 정규화",
                        "상관계수: 삼성전자 0.13, 한화 0.04, 현대차 -0.02",
                        "네이버 -0.08, LG전자 -0.09, SK하이닉스 -0.51",
                        "검색량은 즉각적인 매수 신호가 아니라 관심/불안/정보 탐색을 함께 반영",
                    ],
                    15,
                    True,
                )
            ),
            "image3.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 500_000, 300_000, 12_300_000, 560_000, ["실험 설계"], 28, True)
                + shape(
                    3,
                    "Setup",
                    760_000,
                    1_140_000,
                    11_900_000,
                    5_500_000,
                    [
                        "모델: Logistic Regression",
                        "데이터 분할: 시간 순서를 유지한 Train 70%, Validation 15%, Test 15%",
                        "교차 검증: TimeSeriesSplit, 5 folds",
                        "주요 파라미터: max_iter=1000, class_weight='balanced', random_state=42",
                        "하이퍼파라미터 실험: C = [0.001, 0.01, 0.1, 1, 10, 100]",
                        "평가 지표: Accuracy, Precision, Recall, F1 Score, Confusion Matrix, ROC-AUC",
                        "핵심 이유: 시계열 데이터이므로 랜덤 셔플을 피하고 미래 정보 누수를 방지",
                    ],
                    19,
                    False,
                )
            ),
            None,
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["시계열 교차 검증 결과"], 28, True)
                + picture(3, "CV accuracy", "rId2", 760_000, 1_000_000, 6_300_000, 5_250_000)
                + shape(
                    4,
                    "Notes",
                    7_420_000,
                    1_080_000,
                    4_900_000,
                    4_900_000,
                    [
                        "결과",
                        "Fold 1: 0.4868",
                        "Fold 2: 0.4934",
                        "Fold 3: 0.4737",
                        "Fold 4: 0.5461",
                        "Fold 5: 0.5066",
                        "교차 검증 평균 정확도: 0.5013",
                        "무작위 예측 수준인 0.5와 거의 유사",
                    ],
                    17,
                    True,
                )
            ),
            "image4.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["Test Set 성능 및 Confusion Matrix"], 28, True)
                + picture(3, "Confusion matrix", "rId2", 760_000, 1_040_000, 5_900_000, 5_150_000)
                + shape(
                    4,
                    "Notes",
                    7_250_000,
                    1_030_000,
                    5_100_000,
                    5_050_000,
                    [
                        "Baseline Test Set 성능",
                        "Accuracy: 0.4924",
                        "Precision: 0.5333",
                        "Recall: 0.4528",
                        "F1 Score: 0.4898",
                        "ROC-AUC: 0.4857",
                        "실제 상승 106개 중 48개만 맞혀 상승 기회 포착이 약함",
                    ],
                    17,
                    True,
                )
            ),
            "image5.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["ROC Curve"], 28, True)
                + picture(3, "ROC curve", "rId2", 850_000, 1_020_000, 5_800_000, 5_200_000)
                + shape(
                    4,
                    "Notes",
                    7_250_000,
                    1_080_000,
                    5_100_000,
                    4_850_000,
                    [
                        "해석",
                        "ROC-AUC: 0.4857",
                        "ROC Curve가 대각선 기준선과 거의 유사",
                        "상승과 하락을 확률적으로 잘 구분하지 못함",
                        "현재 feature와 선형 모델 구조만으로는 예측력이 제한적",
                    ],
                    18,
                    True,
                )
            ),
            "image6.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["하이퍼파라미터 C 변경 효과"], 28, True)
                + picture(3, "Hyperparameter effect", "rId2", 640_000, 1_020_000, 6_350_000, 5_200_000)
                + shape(
                    4,
                    "Notes",
                    7_400_000,
                    1_080_000,
                    4_900_000,
                    4_850_000,
                    [
                        "해석",
                        "가장 높은 Validation Accuracy와 ROC-AUC는 C=0.001에서 확인",
                        "Validation Accuracy: 0.5153",
                        "Validation ROC-AUC: 0.5316",
                        "하지만 전체적으로 0.5 근처라 C 조정만으로는 큰 개선이 어려움",
                    ],
                    17,
                    True,
                )
            ),
            "image7.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["피처 중요도와 모델 해석"], 28, True)
                + picture(3, "Coefficients", "rId2", 620_000, 1_000_000, 6_100_000, 5_350_000)
                + shape(
                    4,
                    "Notes",
                    7_050_000,
                    1_000_000,
                    5_500_000,
                    5_150_000,
                    [
                        "중요 feature",
                        "trend_lag3_mean, Open, weighted_trend, Close, ma20, trend_lag1",
                        "검색 트렌드 정보가 모델 판단에 사용됨",
                        "하지만 실제 성능 향상으로 충분히 이어지지는 않음",
                        "검색량 변수는 단독 예측 신호보다는 심리/관심도 보조 지표로 해석",
                    ],
                    16,
                    True,
                )
            ),
            "image8.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 500_000, 300_000, 12_300_000, 560_000, ["피처 중요도 기반 심리학적 해석"], 28, True)
                + shape(
                    3,
                    "Psychology",
                    760_000,
                    1_120_000,
                    11_900_000,
                    5_520_000,
                    [
                        "검색 트렌드 변수는 투자자의 정보 탐색 행동과 시장 관심도를 나타내는 대리 변수",
                        "weighted_trend는 국내/글로벌 관심과 외국인 비중을 함께 반영한 심리 지표",
                        "trend_lag1, trend_lag3_mean은 이슈 인지 후 판단과 매매 행동까지의 시간 지연을 시사",
                        "Open, Close, ma20은 실제 매매 결과와 가격 추세를 반영",
                        "검색량 증가는 긍정적 기대와 부정적 불안을 모두 포함",
                        "따라서 뉴스 감성, 금리, 환율, 시장 지수 등 외부 변수와 함께 해석해야 함",
                    ],
                    20,
                    False,
                )
            ),
            None,
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["예측 확률 분포와 Learning Curve"], 28, True)
                + picture(3, "Probability distribution", "rId2", 520_000, 1_030_000, 5_650_000, 4_950_000)
                + picture(4, "Learning curve", "rId3", 6_520_000, 1_030_000, 5_650_000, 4_950_000)
                + shape(
                    5,
                    "Notes",
                    900_000,
                    6_150_000,
                    11_600_000,
                    550_000,
                    ["확률 분포가 실제 0/1을 명확히 나누지 못하고, Learning Curve도 언더피팅 성격을 보여준다."],
                    16,
                )
            ),
            "image9.png,image10.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["단계적 성능 개선 실험"], 28, True)
                + picture(3, "Metric comparison", "rId2", 560_000, 1_000_000, 6_750_000, 5_450_000)
                + shape(
                    4,
                    "Notes",
                    7_650_000,
                    1_040_000,
                    4_900_000,
                    4_950_000,
                    [
                        "Step 2가 가장 균형적인 개선안",
                        "설정: SelectKBest top12 + C=0.001 + class_weight=balanced",
                        "Step 2 Test Accuracy: 0.5431",
                        "Precision: 0.5889, Recall: 0.5000",
                        "F1 Score: 0.5408, ROC-AUC: 0.5180",
                        "주의: 0.5013은 baseline 교차검증 평균, 0.5431은 개선 모델 Test Set 결과",
                    ],
                    16,
                    True,
                )
            ),
            "image11.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["최종 결론 및 후속 개선 방향"], 28, True)
                + picture(3, "Stepwise confusion matrices", "rId2", 540_000, 1_060_000, 6_620_000, 5_180_000)
                + shape(
                    4,
                    "Notes",
                    7_520_000,
                    1_020_000,
                    5_060_000,
                    5_280_000,
                    [
                        "최종 결론",
                        "Logistic Regression은 해석 가능한 baseline 모델로는 의미가 있음",
                        "하지만 최종 예측 모델로 사용하기에는 성능 한계가 큼",
                        "검색량은 투자자 심리 신호로 활용 가능하지만 단독 설명력은 제한적",
                        "후속 개선: Random Forest, XGBoost 등 비선형 모델 적용",
                        "외부 변수 추가: 뉴스 감성, 시장 지수, 환율, 금리, 업종 지수, 실적 발표 여부",
                    ],
                    16,
                    True,
                )
            ),
            "image12.png",
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
                z.writestr(
                    f"ppt/slides/_rels/slide{idx}.xml.rels",
                    rels_for_images(image_names.split(",")),
                )
            else:
                z.writestr(
                    f"ppt/slides/_rels/slide{idx}.xml.rels",
                    rels_xml("rId2", f"../media/{image_names}"),
                )

        for name, path in image_map.items():
            z.write(path, f"ppt/media/{name}")

    print(OUT_PATH)


if __name__ == "__main__":
    write_deck()
