🚀 MLOps Experimentation Stack (ArgoCD Edition)
Цей проект розгортає повний цикл машинного навчання: від тренування моделей до моніторингу метрик у реальному часі. Все керується через GitOps за допомогою ArgoCD.

🏗️ Архітектура та запуск
Уся інфраструктура описується декларативно. Для запуску стеку:

Додай репозиторій в ArgoCD.

Створи Application, вказавши шлях до твоїх YAML-маніфестів.

Натисни Sync — ArgoCD автоматично розгорне:

MLflow (Tracking Server) + PostgreSQL (DB).

MinIO (S3 Artifact Storage).

Prometheus + Pushgateway (Metrics).

Grafana (Visualization).

🔌 Доступ до сервісів (Port-Forwarding)
Оскільки сервіси працюють всередині кластера, для локальної роботи використовується допоміжний скрипт up-port-forward.sh.

Використання:
Bash
chmod +x up-port-forward.sh
./up-port-forward.sh
Скрипт відкриває наступні порти:

MLflow UI: http://localhost:5000

MinIO Console: http://localhost:9001

Prometheus: http://localhost:9090

Grafana: http://localhost:3000

Pushgateway: http://localhost:9091

⚠️ Важливі зауваження (Ресурси)
Стек є досить ресурсомістким. Якщо поди залишаються у статусі Pending або постійно перезавантажуються:

Пам'ять: Перевір квоти в namespace-quota.yaml. Grafana та MLflow потребують мінімум 512Mi-1Gi RAM для стабільної роботи.

CPU: Якщо вузол перевантажений, ArgoCD може позначати поди як Healthy, але вони будуть "фризити".

🛠️ Відомі проблеми та їх вирішення (Troubleshooting)
Ми пройшли через ці кроки, щоб усе запрацювало. Якщо виникнуть помилки — читай тут:

1. Помилка NoSuchBucket у MLflow
Симптом: Скрипт навчання не може завантажити model.pkl.
Вирішення: MinIO піднімається з порожнім сховищем. Потрібно вручну створити бакет mlflow.

Bash
kubectl exec -n application <minio-pod-name> -- mkdir -p /data/mlflow
2. DNS-сліпота та Timeouts (Grafana -> Prometheus)
Симптом: Grafana видає i/o timeout при спробі підключити Prometheus.
Вирішення: Внутрішній DNS кластера або ClusterIP може барахлити. Використовуй прямий IP поду Prometheus у налаштуваннях Data Source:

Дізнайся IP: kubectl get pods -n application -o wide

Встав у Grafana: http://<POD_IP>:9090

3. Connection Refused на портах
Симптом: Port-forward запущено, але сторінка не відкривається.
Вирішення: ArgoCD міг перестворити поди. Вбий старі процеси pkill -f kubectl та запустіть скрипт заново. Також спробуй використовувати 127.0.0.1 замість localhost.

4. Квоти та "Зупинка" бази даних
Симптом: MLflow не бачить базу або Postgres не стартує.
Вирішення: Переконайся, що ліміти в ResourceQuota дозволяють запустити всі 6+ компонентів одночасно.

🧪 Запуск навчання
Після прокидання портів запусти локальний скрипт:

Bash
python3 train_and_push.py
Результати з'являться в MLflow (артефакти) та Grafana (метрики model_accuracy).
