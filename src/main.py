import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from processing.processor import DataProcessor
from processing.selector import select_features
from models.classifier import ModelTrainer
from models.evaluator import evaluate_models

def main():
    print("==================================================")
    print("🚀 검색 관심도 기반 주가 방향 예측 리빌드 파이프라인 시작")
    print("==================================================")
    
    # Step 1: Data Processing
    print("\n[Step 1] 데이터 전처리 및 100+ 피처 생성")
    processor = DataProcessor()
    processor.run()
    
    # Step 2: Feature Selection
    print("\n[Step 2] XGBoost 중요도 및 상관관계 기반 피처 최적화")
    select_features(target_count=25)
    
    # Step 3: Model Training
    print("\n[Step 3] 앙상블 모델 학습 및 시계열 교차 검증")
    trainer = ModelTrainer()
    trainer.train()
    
    # Step 4: Evaluation & Reporting
    print("\n[Step 4] 다각적 성능 분석 및 직관적 리포트 생성")
    evaluate_models()
    
    print("\n==================================================")
    print("✅ 모든 파이프라인이 성공적으로 완료되었습니다!")
    print("결과물 확인: reports/ 폴더")
    print("==================================================")

if __name__ == "__main__":
    main()
