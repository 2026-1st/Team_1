from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import csv
import html
import shutil


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures" / "model1"
OUT_DIR = REPORTS / "slides"
OUT_PATH = OUT_DIR / "data_characteristics_correlation_slides.pptx"

SLIDE_W = 13_333_333
SLIDE_H = 7_500_000


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def text_body(lines: list[str], font_size: int = 18, bold_first: bool = False) -> str:
    paragraphs = []
    for idx, line in enumerate(lines):
        bold = " b=\"1\"" if bold_first and idx == 0 else ""
        paragraphs.append(
            f"""
            <a:p>
              <a:r>
                <a:rPr lang="ko-KR" sz="{font_size * 100}"{bold}/>
                <a:t>{esc(line)}</a:t>
              </a:r>
            </a:p>"""
        )
    return "".join(paragraphs)


def shape(shape_id: int, name: str, x: int, y: int, cx: int, cy: int, lines: list[str], font_size: int = 18, bold_first: bool = False) -> str:
    return f"""
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="{shape_id}" name="{esc(name)}"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square"/>
          <a:lstStyle/>
          {text_body(lines, font_size, bold_first)}
        </p:txBody>
      </p:sp>"""


def picture(shape_id: int, name: str, rel_id: str, x: int, y: int, cx: int, cy: int) -> str:
    return f"""
      <p:pic>
        <p:nvPicPr>
          <p:cNvPr id="{shape_id}" name="{esc(name)}"/>
          <p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>
          <p:nvPr/>
        </p:nvPicPr>
        <p:blipFill>
          <a:blip r:embed="{rel_id}"/>
          <a:stretch><a:fillRect/></a:stretch>
        </p:blipFill>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        </p:spPr>
      </p:pic>"""


def slide_xml(content: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      {content}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def rels_xml(image_rel: str | None = None, image_target: str | None = None) -> str:
    image_part = ""
    if image_rel and image_target:
        image_part = f'<Relationship Id="{image_rel}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{image_target}"/>'
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  {image_part}
</Relationships>"""


def load_summary() -> dict[str, str]:
    data_path = ROOT / "data" / "processed" / "all_companies_model_data.csv"
    companies = set()
    rows = 0
    start = None
    end = None
    with data_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows += 1
            companies.add(row["company_name"])
            date = row["Date"]
            start = date if start is None or date < start else start
            end = date if end is None or date > end else end
    return {
        "rows": f"{rows:,}",
        "companies": str(len(companies)),
        "start": start or "-",
        "end": end or "-",
    }


def write_deck() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    image_map = {
        "image1.png": FIGURES / "01_eda_distribution.png",
        "image2.png": FIGURES / "02_feature_correlation.png",
        "image3.png": FIGURES / "10_stock_search_overlay.png",
    }
    missing = [str(path) for path in image_map.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing figure files: " + ", ".join(missing))

    summary = load_summary()

    slides = [
        slide_xml(
            shape(2, "Title", 620_000, 760_000, 11_900_000, 900_000, ["변수 간 상관관계 및 데이터 특성 시각화"], 32, True)
            + shape(
                3,
                "Overview",
                900_000,
                2_030_000,
                11_500_000,
                3_400_000,
                [
                    f"분석 데이터: 국내 주요 6개 기업 주가 + Google Trends 검색량",
                    f"분석 기간: {summary['start']} ~ {summary['end']}",
                    f"관측치: {summary['rows']}개, 기업 수: {summary['companies']}개",
                    "주요 변수: Close, Volume, 수익률, 이동평균, 변동성, weighted_trend",
                    "목적: 데이터 분포와 변수 간 선형 관계를 확인하여 모델 해석 근거 마련",
                ],
                20,
            )
        ),
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
    ]

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

        for idx, xml in enumerate(slides, start=1):
            z.writestr(f"ppt/slides/slide{idx}.xml", xml)
            if idx == 1:
                z.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", rels_xml())
            else:
                z.writestr(
                    f"ppt/slides/_rels/slide{idx}.xml.rels",
                    rels_xml("rId2", f"../media/image{idx - 1}.png"),
                )

        for name, path in image_map.items():
            z.write(path, f"ppt/media/{name}")

    print(OUT_PATH)


def content_types(slide_count: int) -> str:
    slide_overrides = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  {slide_overrides}
</Types>"""


def package_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def presentation_xml(slide_count: int) -> str:
    ids = "\n".join(f'<p:sldId id="{255 + i}" r:id="rId{i}"/>' for i in range(1, slide_count + 1))
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{slide_count + 1}"/></p:sldMasterIdLst>
  <p:sldIdLst>{ids}</p:sldIdLst>
  <p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
  <p:defaultTextStyle/>
</p:presentation>"""


def presentation_rels(slide_count: int) -> str:
    rels = [
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, slide_count + 1)
    ]
    rels.append(
        f'<Relationship Id="rId{slide_count + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    )
    rels.append(
        f'<Relationship Id="rId{slide_count + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>'
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {"".join(rels)}
</Relationships>"""


def app_xml(slide_count: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
  <PresentationFormat>On-screen Show (16:9)</PresentationFormat>
  <Slides>{slide_count}</Slides>
  <Company>Team_1</Company>
</Properties>"""


def core_xml() -> str:
    now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>변수 간 상관관계 및 데이터 특성 시각화</dc:title>
  <dc:creator>Team_1</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""


def theme_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Simple">
  <a:themeElements>
    <a:clrScheme name="Simple">
      <a:dk1><a:srgbClr val="111111"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="1F2937"/></a:dk2><a:lt2><a:srgbClr val="F8FAFC"/></a:lt2>
      <a:accent1><a:srgbClr val="2563EB"/></a:accent1><a:accent2><a:srgbClr val="F97316"/></a:accent2>
      <a:accent3><a:srgbClr val="16A34A"/></a:accent3><a:accent4><a:srgbClr val="DC2626"/></a:accent4>
      <a:accent5><a:srgbClr val="7C3AED"/></a:accent5><a:accent6><a:srgbClr val="0891B2"/></a:accent6>
      <a:hlink><a:srgbClr val="2563EB"/></a:hlink><a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Simple">
      <a:majorFont><a:latin typeface="Aptos Display"/><a:ea typeface="Malgun Gothic"/></a:majorFont>
      <a:minorFont><a:latin typeface="Aptos"/><a:ea typeface="Malgun Gothic"/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Simple">
      <a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
      <a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
      <a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
      <a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
  <a:objectDefaults/>
  <a:extraClrSchemeLst/>
</a:theme>"""


def slide_master_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>"""


def slide_master_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""


def slide_layout_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""


def slide_layout_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""


if __name__ == "__main__":
    write_deck()
