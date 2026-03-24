import os
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
import joblib
import time
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, log_loss
from sklearn.preprocessing import LabelEncoder
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# НАЛАШТУВАННЯ
MLFLOW_URI = "http://localhost:5000"
PUSHGATEWAY_URL = "localhost:9091"
EXPERIMENT_NAME = "iris_full_pipeline"

os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://localhost:9000"
os.environ['AWS_ACCESS_KEY_ID'] = "minioadmin"
os.environ['AWS_SECRET_ACCESS_KEY'] = "minioadmin"

def train():
    print(f"Ініціалізація експерименту: {EXPERIMENT_NAME}")
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    # Завантаження даних
    url = 'https://raw.githubusercontent.com/uiuc-cse/data-fa14/gh-pages/data/iris.csv'
    df = pd.read_csv(url)
    X = df.drop('species', axis=1)
    y = df['species']
    
    # Енкодування міток для log_loss
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Розбиваємо дані
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    # Список моделей
    models = [
        ("LogReg", LogisticRegression(max_iter=200)),
        ("DecisionTree", DecisionTreeClassifier(max_depth=3)),
        ("RandomForest", RandomForestClassifier(n_estimators=50, max_depth=5))
    ]

    # Реєстр для Prometheus (новий для кожної ітерації)
    registry = CollectorRegistry()
    gauge_accuracy = Gauge('model_accuracy', 'Accuracy of the model', ['model_name'], registry=registry)
    gauge_loss = Gauge('model_log_loss', 'Log Loss of the model', ['model_name'], registry=registry)

    for name, model in models:
        try:
            with mlflow.start_run(run_name=f"Run_{name}"):
                print(f"Тренування моделі: {name}")
                
                # Навчання
                model.fit(X_train, y_train)
                
                # Прогнози
                y_pred = model.predict(X_test)
                y_pred_prob = model.predict_proba(X_test)
                
                # Метрики
                acc = accuracy_score(y_test, y_pred)
                loss = log_loss(y_test, y_pred_prob)
                
                print(f"{name} -> Accuracy: {acc:.4f}, Log Loss: {loss:.4f}")

                # Логування в MLflow
                mlflow.log_param("model_type", name)
                mlflow.log_metric("accuracy", acc)
                mlflow.log_metric("log_loss", loss)
                # 1. Зберігаємо модель локально
                model_path = "model.pkl"
                joblib.dump(model, model_path)
                # 2. Закидаємо файл як артефакт
                mlflow.log_artifact(model_path)
                
                # Оновлення метрик для Prometheus
                gauge_accuracy.labels(model_name=name).set(acc)
                gauge_loss.labels(model_name=name).set(loss)
        except Exception as e:
            print(f"Помилка для моделі {name}: {e}")

                 # Відправка метрик у Pushgateway
    try:
       push_to_gateway(PUSHGATEWAY_URL, job='iris_training_pipeline', registry=registry)
       print("Всі метрики відправлено в Prometheus")
    except Exception as e:
       print(f"Помилка Pushgateway: {e}")

if __name__ == "__main__":
    try:
        while True:
            train()
            print("Пауза 1 перед наступною ітерацією")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nЗупинка скрипта.")
