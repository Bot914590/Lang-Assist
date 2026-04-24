# Chinese Text Simplifier API - Развёртывание

Это руководство описывает как развернуть Chinese Text Simplifier API для использования с APILayer.

## 📋 Требования

- Go 1.21+ (для локальной разработки)
- Docker 20.10+ (для контейнеризации)
- 2GB+ RAM
- 5GB+ свободного места на диске

## 🚀 Быстрый старт

### Локальная разработка

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/chinese-simplifier-api.git
cd chinese-simplifier-api

# Копирование переменных окружения
cp .env.example .env

# Отредактируйте .env и установите API_KEY
# API_KEY=sk_live_your-secure-key-here

# Запуск
go run main.go
```

Сервис будет доступен на `http://localhost:8081`

### Docker запуск

```bash
# Сборка и запуск
docker-compose up -d --build

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

## 📦 Production Развёртывание

### Вариант 1: Docker Compose

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/yourusername/chinese-simplifier-api.git
cd chinese-simplifier-api

# 2. Настройте переменные окружения
cp .env.example .env
nano .env

# Измените:
# API_KEY=sk_live_$(openssl rand -base64 32)
# LOG_LEVEL=warn
# RATE_LIMIT_PRO=10000

# 3. Запустите сервис
docker-compose up -d

# 4. Проверьте статус
docker-compose ps
docker-compose logs -f
```

### Вариант 2: Systemd (Linux VPS)

```bash
# 1. Скачайте бинарник
wget https://github.com/yourusername/chinese-simplifier-api/releases/latest/download/simplifier-linux-amd64
chmod +x simplifier-linux-amd64
sudo mv simplifier-linux-amd64 /usr/local/bin/simplifier

# 2. Создайте директорию для данных
sudo mkdir -p /var/lib/simplifier/data
sudo cp -r data/* /var/lib/simplifier/data/

# 3. Создайте пользователя
sudo useradd -r -s /bin/false simplifier
sudo chown -R simplifier:simplifier /var/lib/simplifier

# 4. Создайте systemd сервис
sudo nano /etc/systemd/system/simplifier.service
```

**Содержимое `/etc/systemd/system/simplifier.service`:**

```ini
[Unit]
Description=Chinese Text Simplifier API
After=network.target

[Service]
Type=simple
User=simplifier
Group=simplifier
WorkingDirectory=/var/lib/simplifier
EnvironmentFile=/etc/simplifier/.env
ExecStart=/usr/local/bin/simplifier
Restart=always
RestartSec=5
LimitNOFILE=65536

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Активация:**

```bash
# 5. Создайте файл окружения
sudo mkdir -p /etc/simplifier
sudo nano /etc/simplifier/.env

# Содержимое .env:
# PORT=8081
# API_KEY=sk_live_your-secure-key
# DATA_DIR=/var/lib/simplifier/data
# LOG_LEVEL=warn
# RATE_LIMIT_PRO=10000

sudo chmod 600 /etc/simplifier/.env

# 6. Активируйте сервис
sudo systemctl daemon-reload
sudo systemctl enable simplifier
sudo systemctl start simplifier

# 7. Проверьте статус
sudo systemctl status simplifier
sudo journalctl -u simplifier -f
```

### Вариант 3: Kubernetes

```yaml
# simplifier-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chinese-simplifier
  labels:
    app: simplifier
spec:
  replicas: 3
  selector:
    matchLabels:
      app: simplifier
  template:
    metadata:
      labels:
        app: simplifier
    spec:
      containers:
      - name: simplifier
        image: ghcr.io/yourusername/chinese-simplifier-api:latest
        ports:
        - containerPort: 8081
        env:
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: simplifier-secret
              key: api-key
        - name: DATA_DIR
          value: /app/data
        - name: LOG_LEVEL
          value: "warn"
        - name: RATE_LIMIT_PRO
          value: "10000"
        volumeMounts:
        - name: data
          mountPath: /app/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8081
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8081
          initialDelaySeconds: 5
          periodSeconds: 10
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: simplifier-data-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: simplifier-service
spec:
  selector:
    app: simplifier
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8081
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: simplifier-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: simplifier-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: simplifier-service
            port:
              number: 80
```

**Развёртывание:**

```bash
# Создайте секрет
kubectl create secret generic simplifier-secret \
  --from-literal=api-key='sk_live_your-secure-key'

# Примените манифесты
kubectl apply -f simplifier-deployment.yaml
```

## 🔐 Nginx Reverse Proxy

Для production рекомендуется использовать Nginx как reverse proxy:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL сертификаты (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Rate limiting (дополнительно к встроенному)
        limit_req zone=api burst=20 nodelay;
    }

    # Health check endpoint (без лимитов)
    location /health {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        access_log off;
    }
}

# Rate limiting zone
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
}
```

## 🔍 Мониторинг

### Prometheus Metrics

Добавьте endpoint для метрик (требуется доработка):

```go
import "github.com/prometheus/client_golang/prometheus/promhttp"

mux.HandleFunc("/metrics", promhttp.Handler().ServeHTTP)
```

### Grafana Dashboard

Импортируйте dashboard ID `10915` для Go приложений.

### Логирование

Для централизованного логирования используйте:
- **Loki** + **Promtail** для сбора логов
- **ELK Stack** (Elasticsearch, Logstash, Kibana)

## 🛡️ Безопасность

### Checklist для Production

- [ ] Измените `API_KEY` на случайную строку (минимум 32 символа)
- [ ] Установите `LOG_LEVEL=warn` или `error`
- [ ] Настройте HTTPS через Nginx
- [ ] Включите firewall (откройте только 80, 443, 22)
- [ ] Настройте автоматические обновления
- [ ] Включите мониторинг и алерты
- [ ] Настройте backup данных
- [ ] Ограничьте права пользователя (не root)
- [ ] Включите rate limiting
- [ ] Настройте CORS для конкретных доменов

### Генерация безопасного API ключа

```bash
# OpenSSL
openssl rand -base64 32

# Или через Go
go run -e 'package main; import ("crypto/rand"; "encoding/base64"; "fmt"); func main() { b := make([]byte, 32); rand.Read(b); fmt.Println(base64.StdEncoding.EncodeToString(b)) }'
```

## 📊 Масштабирование

### Горизонтальное масштабирование

```bash
# Docker Swarm
docker service create \
  --name simplifier \
  --replicas 5 \
  --env API_KEY=$API_KEY \
  --mount type=volume,source=simplifier-data,target=/app/data \
  -p 8081:8081 \
  chinese-simplifier-api:latest
```

### Load Balancing

Используйте Nginx или HAProxy для балансировки:

```nginx
upstream simplifier_backend {
    least_conn;
    server 192.168.1.10:8081;
    server 192.168.1.11:8081;
    server 192.168.1.12:8081;
}

server {
    location / {
        proxy_pass http://simplifier_backend;
    }
}
```

## 🐛 Отладка

### Проверка логов

```bash
# Docker
docker-compose logs -f

# Systemd
sudo journalctl -u simplifier -f

# Файл логов
tail -f /var/log/simplifier.log
```

### Проверка доступности

```bash
# Health check
curl http://localhost:8081/health

# Тест упрощения
curl -X POST http://localhost:8081/simplify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"text":"你好","target_level":1}'
```

### Проверка rate limiting

```bash
# Быстрые запросы
for i in {1..150}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -H "X-API-Key: your-free-key" \
    http://localhost:8081/health
done
```

## 📈 Performance Tuning

### Оптимизация Go приложения

```bash
# Сборка с оптимизацией
go build -ldflags="-w -s" -o simplifier

# Использование pprof для профилирования
import _ "net/http/pprof"

go tool pprof http://localhost:8081/debug/pprof/heap
```

### Настройка ядра Linux

```bash
# /etc/sysctl.conf
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1024 65535
```

## 🆘 Решение проблем

### Сервис не запускается

```bash
# Проверка логов
sudo journalctl -u simplifier -n 100

# Проверка порта
sudo lsof -i :8081

# Проверка прав доступа
ls -la /var/lib/simplifier/data
```

### Embeddings не загружаются

```bash
# Проверка файла
ls -lh /var/lib/simplifier/data/light_Tencent_AILab_ChineseEmbedding.bin

# Проверка памяти
free -h

# Запуск без эмбеддингов
echo "NO_EMBEDDINGS=true" >> /etc/simplifier/.env
sudo systemctl restart simplifier
```

### Rate limiting не работает

```bash
# Проверка переменных окружения
sudo systemctl show simplifier | grep Environment

# Перезапуск сервиса
sudo systemctl restart simplifier
```

## 📞 Поддержка

- **Документация:** https://github.com/yourusername/chinese-simplifier-api
- **Issues:** https://github.com/yourusername/chinese-simplifier-api/issues
- **Email:** support@yourdomain.com
