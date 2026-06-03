from __future__ import annotations

from pathlib import Path
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


OUT_PATH = OUT_DIR / "final_presentation_all_requirements.pptx"


def make_slides(summary: dict[str, str]) -> list[tuple[str, str | None]]:
    return [
        (
            slide_xml(
                shape(2, "Title", 620_000, 620_000, 11_900_000, 900_000, ["주가 방향 예측 모델 분석 발표자료"], 32, True)
                + shape(
                    3,
                    "Overview",
                    900_000,
                    1_900_000,
                    11_500_000,
                    4_400_000,
                    [
                        f"분석 데이터: 국내 주요 6개 기업 주가 + Google Trends 검색량",
                        f"분석 기간: {summary['start']} ~ {summary['end']}",
                        f"관측치: {summary['rows']}개, 기업 수: {summary['companies']}개",
                        "1. 피처 중요도 기반 심리학적 분석 및 결론",
                        "2. 주가-검색량 상관관계 시각화 및 시계열 중첩 그래프",
                        "3. 모델 성능 비교 그래프: ROC Curve, 지표 바 차트",
                        "4. 변수 간 상관관계 히트맵 및 데이터 특성 시각화",
                    ],
                    19,
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
                        "핵심 해석",
                        "상승/하락 클래스는 극단적으로 불균형하지 않음",
                        "기업별 target 분포 차이가 있어 class_weight 적용 필요",
                        "검색량과 단기 수익률 분포는 클래스 간 분리가 뚜렷하지 않음",
                        "단일 변수만으로 주가 방향을 설명하기 어렵다는 점을 시사",
                    ],
                    18,
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
                        "핵심 해석",
                        "target과 주요 feature 간 선형 상관관계는 전반적으로 낮음",
                        "weighted_trend와 target의 상관계수는 약 -0.07 수준",
                        "return_lag1과 target의 상관계수도 약 -0.06 수준",
                        "검색량은 단독 예측 신호보다 심리/관심도 보조 지표로 해석하는 것이 적절",
                    ],
                    18,
                    True,
                )
            ),
            "image2.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["주가-검색량 시계열 중첩"], 28, True)
                + picture(3, "Stock search overlay", "rId2", 380_000, 920_000, 8_550_000, 5_950_000)
                + shape(
                    4,
                    "Notes",
                    9_200_000,
                    1_100_000,
                    3_850_000,
                    4_950_000,
                    [
                        "핵심 해석",
                        "Close와 weighted_trend를 기업별 min-max 정규화 후 비교",
                        "대부분 기업의 주가-검색량 상관계수는 낮음",
                        "SK하이닉스는 -0.51로 음의 관계가 두드러짐",
                        "검색량 증가는 호재 관심과 악재 불안을 모두 포함할 수 있음",
                    ],
                    16,
                    True,
                )
            ),
            "image3.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["피처 중요도 기반 심리학적 분석"], 28, True)
                + picture(3, "Feature importance", "rId2", 620_000, 1_000_000, 6_150_000, 5_350_000)
                + shape(
                    4,
                    "Notes",
                    7_100_000,
                    1_000_000,
                    5_500_000,
                    5_150_000,
                    [
                        "핵심 해석",
                        "weighted_trend, trend_lag1, trend_lag3_mean은 투자자 관심과 정보 탐색 행동을 반영",
                        "지연 검색량 변수는 이슈 인지 후 판단과 매매까지의 시간 지연을 시사",
                        "Open, Close, ma20은 실제 가격 추세와 매매 결과를 반영",
                        "검색량은 긍정적 기대와 부정적 불안을 모두 포함하므로 뉴스 감성, 금리, 환율, 시장 지수와 함께 해석 필요",
                    ],
                    16,
                    True,
                )
            ),
            "image4.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["모델 성능: ROC Curve"], 28, True)
                + picture(3, "ROC curve", "rId2", 800_000, 1_000_000, 5_900_000, 5_300_000)
                + shape(
                    4,
                    "Notes",
                    7_300_000,
                    1_060_000,
                    5_000_000,
                    4_850_000,
                    [
                        "핵심 지표",
                        "Logistic Regression Test Accuracy: 0.4924",
                        "F1 Score: 0.4898",
                        "ROC-AUC: 0.4857",
                        "ROC Curve가 대각선 기준선과 유사하여 상승/하락 확률 구분력이 낮음",
                        "현재 선형 모델과 feature만으로는 안정적 예측에 한계",
                    ],
                    17,
                    True,
                )
            ),
            "image5.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["모델 성능 비교: 지표 바 차트"], 28, True)
                + picture(3, "Metric comparison", "rId2", 560_000, 1_000_000, 6_750_000, 5_450_000)
                + shape(
                    4,
                    "Notes",
                    7_650_000,
                    1_040_000,
                    4_900_000,
                    4_950_000,
                    [
                        "핵심 해석",
                        "Step 2: SelectKBest top12 + C=0.001이 가장 균형적",
                        "Step 2 Test Accuracy: 0.5431",
                        "Precision: 0.5889, Recall: 0.5000",
                        "F1 Score: 0.5408, ROC-AUC: 0.5180",
                        "Baseline 교차검증 평균 정확도 0.5013과는 평가 방식이 다른 Test Set 결과",
                        "Baseline 대비 모든 주요 지표가 개선되었지만 절대 성능은 여전히 제한적",
                    ],
                    17,
                    True,
                )
            ),
            "image6.png",
        ),
        (
            slide_xml(
                shape(2, "Title", 460_000, 260_000, 12_500_000, 520_000, ["최종 결론 및 개선 방향"], 28, True)
                + picture(3, "Confusion matrices", "rId2", 550_000, 1_050_000, 6_650_000, 5_250_000)
                + shape(
                    4,
                    "Notes",
                    7_550_000,
                    1_020_000,
                    5_000_000,
                    5_200_000,
                    [
                        "결론",
                        "검색량과 feature importance는 투자자 심리 신호로 활용 가능",
                        "하지만 검색량 단독으로 주가 방향을 안정적으로 설명하기는 어려움",
                        "Logistic Regression은 해석 가능한 baseline으로 의미가 있음",
                        "후속 개선: Random Forest, XGBoost 등 비선형 모델 적용",
                        "외부 변수 추가: 뉴스 감성, 시장 지수, 환율, 금리, 업종 지수, 실적 발표 여부",
                    ],
                    17,
                    True,
                )
            ),
            "image7.png",
        ),
    ]


def write_deck() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    image_map = {
        "image1.png": FIGURES / "01_eda_distribution.png",
        "image2.png": FIGURES / "02_feature_correlation.png",
        "image3.png": FIGURES / "10_stock_search_overlay.png",
        "image4.png": FIGURES / "06_coefficients.png",
        "image5.png": FIGURES / "05_roc_curve.png",
        "image6.png": FIGURES / "01_stepwise_metric_comparison.png",
        "image7.png": FIGURES / "02_stepwise_confusion_matrices.png",
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

        for idx, (xml, image_name) in enumerate(slides, start=1):
            z.writestr(f"ppt/slides/slide{idx}.xml", xml)
            if image_name is None:
                z.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", rels_xml())
            else:
                z.writestr(
                    f"ppt/slides/_rels/slide{idx}.xml.rels",
                    rels_xml("rId2", f"../media/{image_name}"),
                )

        for name, path in image_map.items():
            z.write(path, f"ppt/media/{name}")

    print(OUT_PATH)


if __name__ == "__main__":
    write_deck()
