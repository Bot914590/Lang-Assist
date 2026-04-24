# Chinese Text Simplifier API

[![Go Version](https://img.shields.io/badge/go-1.21+-blue.svg)](https://golang.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![APILayer](https://img.shields.io/badge/marketplace-APILayer-orange.svg)](https://apilayer.com/marketplace/chinese-simplifier-api)

A powerful API for simplifying Chinese texts to target HSK levels using semantic analysis and vector embeddings.

## 🌟 Features

- **Text Simplification** — Automatic replacement of complex words with simpler alternatives
- **Semantic Search** — Synonym matching using vector embeddings (Tencent AILab)
- **HSK Levels** — Support for all HSK levels (1-6)
- **Text Analysis** — Tokenization, word level detection, frequency analysis
- **High Performance** — Optimized Go application with caching
- **API Key Authentication** — Secure API access
- **Rate Limiting** — Flexible limits for different subscription tiers

## 📖 Table of Contents

- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [Authentication](#-authentication)
- [Pricing Tiers](#-pricing-tiers)
- [Usage Examples](#-usage-examples)
- [Environment Variables](#-environment-variables)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)

## 🚀 Quick Start

### Local Run

```bash
# Clone repository
git clone https://github.com/yourusername/chinese-simplifier-api.git
cd chinese-simplifier-api

# Copy environment variables
cp .env.example .env

# Run (Go 1.21+ required)
go run main.go
```

Service will be available at `http://localhost:8081`

### Docker Run

```bash
# Build image
docker build -t chinese-simplifier .

# Run container
docker run -p 8081:8081 \
  -e API_KEY=your-api-key \
  -e DATA_DIR=/app/data \
  -v $(pwd)/data:/app/data \
  chinese-simplifier
```

## 🔑 API Endpoints

### Simplify Text

**POST** `/simplify`

Simplifies Chinese text to target HSK level by replacing complex words with semantically similar simpler alternatives.

**Request:**
```bash
curl -X POST http://localhost:8081/simplify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "text": "这个经济问题很复杂",
    "target_level": 2
  }'
```

**Response:**
```json
{
  "status": "ok",
  "original_text": "这个经济问题很复杂",
  "simplified_text": "这个经济问题很 [COMPLEX:4]",
  "replacements": [
    {
      "original": "经济",
      "replacement": "[COMPLEX:4]",
      "reason": "HSK level too high, no similar word found",
      "hsk_level": 4,
      "similarity": 0
    }
  ],
  "target_level": 2,
  "total_tokens": 6,
  "replaced_count": 2
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|----------|-----|----------|----------|
| `text` | string | ✅ Yes | Text to simplify (Chinese characters) |
| `target_level` | integer | ✅ Yes | Target HSK level (1-6) |

---

### Analyze Text

**POST** `/analyze`

Analyzes text: tokenization, HSK word level detection, frequency analysis.

**Request:**
```bash
curl -X POST http://localhost:8081/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "text": "我喜欢学习中文",
    "lang": "zh",
    "user_level": 2
  }'
```

**Response:**
```json
{
  "status": "ok",
  "tokens_count": 7,
  "tokens": [
    {
      "value": "我",
      "lemma": "我",
      "frequency": 1,
      "positions": [0],
      "hsk": 1,
      "is_known": true
    }
  ]
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|----------|-----|----------|----------|
| `text` | string | ✅ Yes | Text to analyze |
| `lang` | string | ❌ No | Language code (default: "zh") |
| `user_level` | integer | ❌ No | User HSK level (default: 1) |

---

### Word Information

**GET** `/word/info?word={word}`

Get word information: HSK level, pinyin, translations.

**Request:**
```bash
curl "http://localhost:8081/word/info?word=学习" \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "word": "学习",
  "hsk_level": 3,
  "pinyin": "xué xí",
  "strokes": "8",
  "translations": {
    "eng": ["to learn", "to study"],
    "rus": ["учить", "изучать"]
  },
  "has_embedding": true
}
```

---

### Similar Words

**GET** `/word/similar?word={word}&max_level={level}&top_k={k}`

Find semantically similar words simpler than specified.

**Request:**
```bash
curl "http://localhost:8081/word/similar?word=美丽&max_level=2&top_k=5" \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "word": "美丽",
  "max_level": 2,
  "similar": [
    {
      "word": "漂亮",
      "similarity": 0.70,
      "hsk_level": 1
    },
    {
      "word": "好",
      "similarity": 0.55,
      "hsk_level": 1
    }
  ]
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|----------|-----|----------|----------|
| `word` | string | ✅ Yes | Source word |
| `max_level` | integer | ❌ No | Maximum HSK level (default: 4) |
| `top_k` | integer | ❌ No | Number of results (default: 10) |

---

### Health Check

**GET** `/health`

Check service availability.

**Request:**
```bash
curl http://localhost:8081/health
```

**Response:**
```json
{
  "status": "ok",
  "hsk_loaded": true,
  "embeddings": true,
  "vector_size": 200,
  "max_hsk_level": 4
}
```

---

## 🔐 Authentication

All API requests must include the `X-API-Key` header:

```bash
-H "X-API-Key: your-api-key"
```

### Getting API Key

1. Register at [APILayer](https://apilayer.com/)
2. Subscribe to the API
3. Copy your API key from your dashboard

### Pricing Tiers

| Tier | Requests per Day | Requests per Minute | Price |
|-------|-----------------|-------------------|------|
| **Free** | 100 | 10 | Free |
| **Basic** | 1,000 | 50 | $9.99/month |
| **Pro** | 10,000 | 200 | $29.99/month |
| **Enterprise** | 100,000+ | 1000+ | Custom |

---

## 💻 Usage Examples

### Python

```python
import requests

API_KEY = "your-api-key"
BASE_URL = "http://localhost:8081"

headers = {"X-API-Key": API_KEY}

# Simplify text
response = requests.post(
    f"{BASE_URL}/simplify",
    headers=headers,
    json={"text": "她很美丽", "target_level": 2}
)
result = response.json()
print(result["simplified_text"])

# Analyze text
response = requests.post(
    f"{BASE_URL}/analyze",
    headers=headers,
    json={"text": "我喜欢学习中文", "lang": "zh", "user_level": 2}
)
tokens = response.json()["tokens"]
for token in tokens:
    print(f"{token['value']}: HSK {token['hsk']}")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const API_KEY = 'your-api-key';
const BASE_URL = 'http://localhost:8081';

const headers = { 'X-API-Key': API_KEY };

// Simplify text
async function simplifyText(text, targetLevel) {
  const response = await axios.post(
    `${BASE_URL}/simplify`,
    { text, target_level: targetLevel },
    { headers }
  );
  return response.data;
}

// Analyze text
async function analyzeText(text, userLevel) {
  const response = await axios.post(
    `${BASE_URL}/analyze`,
    { text, lang: 'zh', user_level: userLevel },
    { headers }
  );
  return response.data;
}

// Usage
simplifyText('她很美丽', 2).then(result => {
  console.log('Simplified:', result.simplified_text);
});
```

### cURL

```bash
# Simplify
curl -X POST http://localhost:8081/simplify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"text":"她很美丽","target_level":2}'

# Analyze
curl -X POST http://localhost:8081/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"text":"我喜欢学习中文","lang":"zh","user_level":2}'

# Word info
curl "http://localhost:8081/word/info?word=学习" \
  -H "X-API-Key: your-api-key"

# Similar words
curl "http://localhost:8081/word/similar?word=美丽&max_level=2&top_k=5" \
  -H "X-API-Key: your-api-key"
```

---

## ⚙️ Environment Variables

| Variable | Description | Default |
|------------|----------|--------------|
| `PORT` | Service port | `8081` |
| `API_KEY` | API key for authentication | *(required)* |
| `DATA_DIR` | Path to data directory | `./data` |
| `MAX_HSK_LEVEL` | Maximum HSK level for embeddings | `4` |
| `NO_EMBEDDINGS` | Don't load embeddings | `false` |
| `RATE_LIMIT_FREE` | Free tier limit (requests/day) | `100` |
| `RATE_LIMIT_BASIC` | Basic tier limit | `1000` |
| `RATE_LIMIT_PRO` | Pro tier limit | `10000` |
| `RATE_LIMIT_ENTERPRISE` | Enterprise tier limit | `100000` |
| `LOG_LEVEL` | Logging level (debug, info, warn, error) | `info` |

---

## 📦 Deployment

### Docker Compose

```yaml
version: '3.8'

services:
  simplifier:
    image: chinese-simplifier:latest
    ports:
      - "8081:8081"
    environment:
      - API_KEY=${API_KEY}
      - DATA_DIR=/app/data
      - MAX_HSK_LEVEL=4
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chinese-simplifier
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
        image: chinese-simplifier:latest
        ports:
        - containerPort: 8081
        env:
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secret
              key: api-key
        - name: DATA_DIR
          value: /app/data
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: simplifier-data
```

---

## 📁 Project Structure

```
chinese-simplifier-api/
├── main.go                 # Entry point, HTTP server
├── embeddings.go           # Embedding loading and operations
├── auth.go                 # API Key authentication
├── rate_limit.go           # Rate limiting
├── errors.go               # Error handling
├── go.mod                  # Go module
├── go.sum                  # Dependencies
├── Dockerfile              # Docker image
├── .env.example            # Environment variables example
├── .dockerignore           # Ignored files for Docker
├── LICENSE                 # MIT License
├── README.md               # Documentation
├── openapi.yaml            # OpenAPI 3.0 specification
├── data/
│   ├── hsk.json            # HSK dictionary (90k+ entries)
│   ├── cache/              # Embeddings cache
│   └── light_Tencent_AILab_ChineseEmbedding.bin  # Embeddings
├── tests/
│   ├── main_test.go        # Integration tests
│   └── simplify_test.go    # Unit tests
└── .github/
    └── workflows/
        ├── go.yml          # CI: tests and linting
        └── release.yml     # CD: releases and Docker
```

---

## 🧪 Testing

```bash
# Run all tests
go test -v ./...

# Run with coverage
go test -v -cover ./...

# Benchmark tests
go test -v -bench=. ./...
```

---

## 📊 Metrics and Monitoring

Service provides metrics via `/health` endpoint:

- `hsk_loaded` — HSK dictionary load status
- `embeddings` — Embeddings load status
- `vector_size` — Vector dimension
- `max_hsk_level` — Maximum HSK level

For production, consider setting up:
- Prometheus for metrics collection
- Grafana for visualization
- Alertmanager for notifications

---

## 🔧 Production Configuration

### 1. API Keys Setup

Create `.env` file:
```env
API_KEY=your-secure-api-key-generated-with-openssl-rand-base64-32
DATA_DIR=/var/lib/simplifier/data
LOG_LEVEL=warn
```

### 2. Systemd Service

```ini
[Unit]
Description=Chinese Text Simplifier API
After=network.target

[Service]
Type=simple
User=simplifier
WorkingDirectory=/opt/simplifier
EnvironmentFile=/etc/simplifier/.env
ExecStart=/opt/simplifier/simplifier
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3. Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📞 Support

- **Documentation:** https://apilayer.com/marketplace/chinese-simplifier-api
- **Email:** support@yourdomain.com
- **GitHub Issues:** https://github.com/yourusername/chinese-simplifier-api/issues

---

## 📄 License

MIT License — see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Tencent AILab](https://ai.tencent.com/) for vector embeddings
- [HSK Dictionary](https://github.com/Coerphinus/chinese-dictionary) for HSK data
- [APILayer](https://apilayer.com/) for API publishing platform
