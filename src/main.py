import time
from trend_korea_collector import KoreaTrendsCollector
from collect_global_trends import GlobalTrendCollector
from stock_collector import StockDataCollector
from data_processor import DataProcessor
from model_trainer import ModelTrainer

def main():
    print("=" * 60)
    print("      [종합 데이터 파이프라인 실행 시작]")
    print("=" * 60)
    start_time = time.time()

    # 1. 국내(KR) 구글 트렌드 수집
    print("\n[1/5] 국내 구글 트렌드 데이터 수집 중...")
    kr_collector = KoreaTrendsCollector()
    kr_collector.run()

    # 2. 글로벌 구글 트렌드 수집
    print("\n[2/5] 글로벌 구글 트렌드 데이터 수집 중...")
    glb_collector = GlobalTrendCollector()
    glb_collector.run()

    # 3. 주가 데이터 수집 (Yahoo Finance)
    print("\n[3/5] 주가 데이터 수집 중...")
    stock_collector = StockDataCollector()
    stock_collector.run()

    # 4. 데이터 전처리 및 피처 엔지니어링
    print("\n[4/5] 데이터 전처리 및 피처 생성 중...")
    processor = DataProcessor()
    processor.run()

    # 5. 모델 학습 및 평가
    print("\n[5/5] 모델 학습 및 평가 진행 중...")
    trainer = ModelTrainer()
    trainer.run()

    end_time = time.time()
    duration = (end_time - start_time) / 60
    
    print("\n" + "=" * 60)
    print(f"      [모든 공정 완료] 소요 시간: {duration:.2f}분")
    print("=" * 60)

if __name__ == "__main__":
    main()
