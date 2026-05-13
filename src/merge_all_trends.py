from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = BASE_DIR / "data" / "raw" / "google_trends"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = "2025-05-12"
END_DATE = "2026-05-12"

COMPANY_CONFIG = {
    "samsung": {
        "files": ["삼성_1.csv", "삼성_2.csv", "삼성_3.csv", "삼성_4.csv"],
        "ticker": "005930.KS",
        "company_name": "삼성전자",
        "foreign_ratio": 0.50,
    },
    "skhynix": {
        "files": ["sk_1.csv", "sk_2.csv", "sk_3.csv", "sk_4.csv"],
        "ticker": "000660.KS",
        "company_name": "SK하이닉스",
        "foreign_ratio": 0.53,
    },
    "naver": {
        "files": ["네이버_1.csv", "네이버_2.csv", "네이버_3.csv", "네이버_4.csv"],
        "ticker": "035420.KS",
        "company_name": "네이버",
        "foreign_ratio": 0.45,
    },
    "hanwha": {
        "files": ["한화_1.csv", "한화_2.csv", "한화_3.csv", "한화_4.csv"],
        "ticker": "012450.KS",
        "company_name": "한화에어로스페이스",
        "foreign_ratio": 0.32,
    },
    "lg": {
        "files": ["엘지_1.csv", "엘지_2.csv", "엘지_3.csv", "엘지_4.csv"],
        "ticker": "066570.KS",
        "company_name": "LG전자",
        "foreign_ratio": 0.36,
    },
    "hyundai": {
        "files": ["현대차_1.csv", "현대차_2.csv", "현대차_3.csv", "현대차_4.csv"],
        "ticker": "005380.KS",
        "company_name": "현대차",
        "foreign_ratio": 0.40,
    },
}


def read_trend_csv(file_path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

    df = df.iloc[:, :2]
    df.columns = ["Date", "trend"]

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["trend"] = pd.to_numeric(df["trend"], errors="coerce")

    df = df.dropna(subset=["Date"])
    df = df.dropna(subset=["trend"])

    return df


def merge_company_files(company_key: str, info: dict) -> pd.DataFrame:
    dfs = []

    for filename in info["files"]:
        file_path = RAW_DIR / filename

        if not file_path.exists():
            print(f"[파일 없음] {file_path}")
            continue

        print(f"[읽는 중] {info['company_name']} - {filename}")
        df = read_trend_csv(file_path)
        dfs.append(df)

    if not dfs:
        print(f"[스킵] {info['company_name']} 데이터 없음")
        return pd.DataFrame()

    company_df = pd.concat(dfs, ignore_index=True)

    # 겹치는 날짜는 평균 처리
    company_df = (
        company_df
        .groupby("Date", as_index=False)["trend"]
        .mean()
    )

    # 전체 일간 날짜 생성
    full_dates = pd.DataFrame({
        "Date": pd.date_range(
            start=START_DATE,
            end=END_DATE,
            freq="D"
        )
    })

    company_df = pd.merge(
        full_dates,
        company_df,
        on="Date",
        how="left"
    )

    # 핵심: 주간 데이터로 인해 생긴 중간 결측은 선형 보간
    company_df["trend"] = company_df["trend"].interpolate(method="linear")

    # 앞뒤 끝부분 결측이 남으면 가까운 값으로 채움
    company_df["trend"] = company_df["trend"].ffill().bfill()

    company_df["ticker"] = info["ticker"]
    company_df["company_name"] = info["company_name"]
    company_df["foreign_ratio"] = info["foreign_ratio"]
    company_df["weighted_trend"] = company_df["trend"] * company_df["foreign_ratio"]

    output_path = PROCESSED_DIR / f"{company_key}_trend_cleaned.csv"

    company_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"[기업 저장 완료] {output_path}")
    print(company_df.shape)

    return company_df


def main():
    all_data = []

    for company_key, info in COMPANY_CONFIG.items():
        df = merge_company_files(company_key, info)

        if not df.empty:
            all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)

    final_output = PROCESSED_DIR / "all_companies_trends_cleaned.csv"

    final_df.to_csv(
        final_output,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n[전체 병합 완료]")
    print(final_output)
    print(final_df.shape)
    print(final_df.groupby("company_name").size())
    print(final_df.head())


if __name__ == "__main__":
    main()