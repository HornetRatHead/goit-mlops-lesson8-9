import mlflow
import os

# 1. Налаштування для зв'язку з MinIO (S3)
os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://localhost:9000'
os.environ['AWS_ACCESS_KEY_ID'] = 'minioadmin'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'minioadmin'

# 2. Вказуємо адресу сервера MLflow
mlflow.set_tracking_uri("http://localhost:5000")

def run_test():
    try:
        # Створюємо експеримент для StockWise
        mlflow.set_experiment("StockWise_Test_Run")

        with mlflow.start_run():
            print("🚀 Запуск тестування системи...")
            
            # Логуємо "метрики" навчання моделі
            mlflow.log_param("algorithm", "NeuralNetwork")
            mlflow.log_metric("accuracy", 0.98)
            
            # Створюємо файл, який імітує збережену модель
            with open("test_model.txt", "w") as f:
                f.write("Це тестова модель StockWise v1.0")
            
            # Відправляємо файл у MinIO через MLflow
            mlflow.log_artifact("test_model.txt")
            
            print("✅ ТЕСТ ПРОЙДЕНО!")
            print("Тепер перевір http://localhost:5000 (MLflow) та http://localhost:8080 (MinIO)")

    except Exception as e:
        print(f"❌ ПОМИЛКА: {e}")

if __name__ == "__main__":
    run_test()
