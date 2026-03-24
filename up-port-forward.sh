# Очищення
pkill -f "kubectl port-forward"

# Запуск усіх необхідних тунелів
kubectl port-forward svc/mlflow -n application 5000:5000 > /dev/null 2>&1 & \
kubectl port-forward svc/minio -n application 9000:9000 9001:9001 > /dev/null 2>&1 & \
kubectl port-forward svc/prometheus -n application 9090:80 > /dev/null 2>&1 & \
kubectl port-forward svc/pushgateway -n application 9091:9091 > /dev/null 2>&1 & \
kubectl port-forward svc/grafana -n application 3000:3000 > /dev/null 2>&1 &

# Перевірка
jobs
