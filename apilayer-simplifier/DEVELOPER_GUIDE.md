# Developer Guide

Chinese Text Simplifier API — Developer Documentation

## 📖 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Structure](#code-structure)
- [API Implementation](#api-implementation)
- [Data Processing](#data-processing)
- [Testing](#testing)
- [Building and Deployment](#building-and-deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Applications                     │
│         (Python, JavaScript, Mobile Apps, etc.)             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway / Nginx                       │
│              (SSL, Rate Limiting, Routing)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Chinese Simplifier Service                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Auth      │  │   Rate      │  │   HTTP Handlers     │  │
│  │ Middleware  │  │  Limiter    │  │  (/simplify, etc.)  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Core Processing Engine                   │   │
│  │  • Tokenization  • HSK Lookup  • Semantic Search     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────────┐  ┌──────────────────────────────────┐    │
│  │ HSK Dictionary│  │ Vector Embeddings (Tencent AILab)│    │
│  │   (90k+ words)│  │      (Cached .gob files)         │    │
│  └──────────────┘  └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow

```
1. Client Request → 2. CORS Middleware → 3. Auth Middleware → 4. Rate Limit
       ↓
5. HTTP Handler → 6. Core Logic → 7. Data Access → 8. Response
```

---

## Getting Started

### Prerequisites

- **Go 1.21+** — [Download](https://golang.org/dl/)
- **Git** — Version control
- **Docker** (optional) — Containerization
- **Data files** — HSK dictionary and embeddings

### Clone Repository

```bash
git clone https://github.com/yourusername/chinese-simplifier-api.git
cd chinese-simplifier-api
```

### Install Dependencies

```bash
go mod download
```

### Setup Data Directory

```bash
# Create data directory
mkdir -p data/cache

# Place HSK dictionary
# Download from: https://github.com/Coerphinus/chinese-dictionary
cp hsk.json data/

# Place embeddings (optional, for semantic search)
# Download: light_Tencent_AILab_ChineseEmbedding.bin
cp light_Tencent_AILab_ChineseEmbedding.bin data/
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
PORT=8081
API_KEY=your-test-api-key
DATA_DIR=./data
MAX_HSK_LEVEL=4
LOG_LEVEL=debug
```

### Run Service

```bash
# Development mode
go run main.go

# Production build
go build -o simplifier
./simplifier
```

---

## Development Environment

### IDE Setup

**VS Code Extensions:**
- Go (by Go Team at Google)
- Docker
- YAML (Red Hat)

**settings.json:**
```json
{
    "go.formatTool": "goimports",
    "go.lintTool": "golangci-lint",
    "go.testFlags": ["-v", "-race"],
    "go.buildFlags": ["-tags", "timetrace"]
}
```

### Useful Commands

```bash
# Format code
go fmt ./...

# Run linter
golangci-lint run

# Run tests
go test -v ./...

# Run tests with coverage
go test -v -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Build binary
go build -o simplifier -ldflags="-s -w"

# Run with race detector
go run -race main.go
```

### Pre-commit Hooks

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash

echo "Running pre-commit checks..."

# Format check
go fmt ./...
if [ $? -ne 0 ]; then
    echo "❌ Format check failed"
    exit 1
fi

# Lint check
golangci-lint run
if [ $? -ne 0 ]; then
    echo "❌ Lint check failed"
    exit 1
fi

# Tests
go test ./...
if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi

echo "✅ All checks passed"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Code Structure

### File Organization

```
.
├── main.go              # Entry point, HTTP server setup
├── auth.go              # Authentication middleware
├── rate_limit.go        # Rate limiting implementation
├── embeddings.go        # Embedding loading, semantic search
├── errors.go            # Error types and handling
├── go.mod               # Module definition
├── Dockerfile           # Container build instructions
└── tests/
    └── main_test.go     # Test suite
```

### main.go

**Responsibilities:**
- HTTP server configuration
- Route registration
- Middleware chain setup
- Graceful shutdown

**Key Functions:**
```go
func main()              // Entry point
func initData()          // Initialize HSK and embeddings
func getDataDir() string // Determine data directory
```

### auth.go

**Responsibilities:**
- API key validation
- Constant-time comparison
- Multiple key support

**Structures:**
```go
type AuthMiddleware struct {
    requireAuth bool
    apiKeys     map[string]bool
}
```

### rate_limit.go

**Responsibilities:**
- Per-key request tracking
- Sliding window rate limiting
- Automatic cleanup

**Structures:**
```go
type RateLimiter struct {
    mu       sync.RWMutex
    requests map[string][]time.Time
}
```

### embeddings.go

**Responsibilities:**
- Binary embedding file parsing
- Gob cache serialization
- Cosine similarity calculation

**Key Functions:**
```go
func LoadEmbeddingsWithCache(...)  // Load with caching
func CosineSimilarity(...)         // Vector similarity
func FindSimplerWord(...)          // Semantic search
```

### errors.go

**Responsibilities:**
- Custom error types
- API error responses
- Validation errors

**Error Codes:**
```go
ErrInvalidJSON         // 400
ErrUnauthorized        // 401
ErrRateLimitExceeded   // 429
ErrInternalServer      // 500
```

---

## API Implementation

### Handler Pattern

All handlers follow this pattern:

```go
func handlerName(w http.ResponseWriter, r *http.Request) {
    // 1. Set headers
    w.Header().Set("Content-Type", "application/json")
    w.Header().Set("Access-Control-Allow-Origin", "*")

    // 2. Check method
    if r.Method != http.MethodPost {
        writeAPIError(w, http.StatusMethodNotAllowed, ErrMethodNotAllowed, "...")
        return
    }

    // 3. Read body
    body, err := io.ReadAll(r.Body)
    if err != nil {
        writeAPIError(w, http.StatusBadRequest, ErrInvalidJSON, "...")
        return
    }
    defer r.Body.Close()

    // 4. Parse JSON
    var req RequestType
    if err := json.Unmarshal(body, &req); err != nil {
        writeAPIError(w, http.StatusBadRequest, ErrInvalidJSON, "...")
        return
    }

    // 5. Validate
    if err := validate(&req); err != nil {
        writeAPIError(w, err.StatusCode, err.Code, err.Message)
        return
    }

    // 6. Process
    result := processLogic(req)

    // 7. Respond
    json.NewEncoder(w).Encode(result)
}
```

### Adding New Endpoint

1. **Define request/response types** in `main.go`:
```go
type NewRequest struct {
    Param string `json:"param"`
}

type NewResponse struct {
    Result string `json:"result"`
}
```

2. **Create handler function**:
```go
func newHandler(w http.ResponseWriter, r *http.Request) {
    // Implementation
}
```

3. **Register route** in `main()`:
```go
mux.HandleFunc("/new-endpoint", newHandler)
```

4. **Add validation**:
```go
func validateNewRequest(req *NewRequest) *APIError {
    if req.Param == "" {
        return NewAPIError(http.StatusBadRequest, ErrMissingParameter, "param required")
    }
    return nil
}
```

5. **Update OpenAPI spec** in `openapi.yaml`

---

## Data Processing

### HSK Dictionary

**Format** (`data/hsk.json`):
```json
{
  "你好": 1,
  "学习": 3,
  "经济": 4
}
```

**Loading**:
```go
func LoadHSK(dataDir string) (map[string]int, []HSKEntry, error) {
    // 1. Read hsk.json
    // 2. Parse to map[string]int
    // 3. Load extended entries (pinyin, translations)
    // 4. Return dictionary and entries
}
```

### Vector Embeddings

**Binary Format** (Tencent AILab):
```
Header:
  - vocab_size (int32)
  - vector_dim (int32)

Entries:
  - word (string, length-prefixed)
  - vector (float32[dim])
```

**Loading with Cache**:
```go
func LoadEmbeddingsWithCache(embPath, cachePath string, hskDict map[string]int, maxLevel int) {
    // 1. Check cache exists
    // 2. If cache valid, load .gob
    // 3. Otherwise parse binary, filter by HSK, save cache
    // 4. Return embeddings map
}
```

**Cache Format** (`.gob`):
```go
type EmbeddingCache struct {
    Version    string
    MaxHSK     int
    VectorSize int
    Embeddings map[string][]float32
}
```

### Tokenization

**Chinese Tokenization**:
```go
func tokenizeChineseSimple(text string) []string {
    // Simple character-by-character tokenization
    // Can be extended with dictionary-based segmentation
}
```

**European Tokenization**:
```go
func tokenizeEuropean(text string) []string {
    // Space-split and punctuation stripping
}
```

### Simplification Algorithm

```go
func simplifyTextWithDict(text string, targetLevel int) *SimplifyResult {
    // 1. Tokenize input
    // 2. For each token:
    //    a. Look up HSK level
    //    b. If level > target:
    //       - Find semantic match via embeddings
    //       - If similarity >= 0.55, replace
    //       - Else mark as [COMPLEX:level]
    // 3. Join tokens
    // 4. Return result with replacements
}
```

---

## Testing

### Test Structure

```
tests/
├── main_test.go         # Integration tests
├── simplify_test.go     # Simplification tests
├── analyze_test.go      # Analysis tests
└── embeddings_test.go   # Embedding tests
```

### Unit Tests

**Example** (`simplify_test.go`):
```go
package main

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestSimplifyText(t *testing.T) {
    // Setup
    hskDict = map[string]int{"美丽": 4, "漂亮": 1}
    
    // Test
    result := simplifyTextWithDict("她很美丽", 2)
    
    // Assert
    assert.Equal(t, "ok", result.Status)
    assert.Equal(t, 1, result.ReplacedCount)
}
```

### Integration Tests

**Example** (`main_test.go`):
```go
func TestSimplifyEndpoint(t *testing.T) {
    // Start test server
    go func() {
        server := httptest.NewServer(http.HandlerFunc(simplifyHandler))
        defer server.Close()
    }()
    
    // Make request
    resp, err := http.Post(server.URL, "application/json", body)
    
    // Validate response
    assert.Equal(t, 200, resp.StatusCode)
}
```

### Running Tests

```bash
# All tests
go test -v ./...

# Specific package
go test -v ./tests/...

# With coverage
go test -v -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html

# Benchmark
go test -v -bench=. -benchmem ./...
```

---

## Building and Deployment

### Local Build

```bash
# Linux amd64
GOOS=linux GOARCH=amd64 go build -o simplifier-linux-amd64

# macOS arm64
GOOS=darwin GOARCH=arm64 go build -o simplifier-macos-arm64

# Windows amd64
GOOS=windows GOARCH=amd64 go build -o simplifier-windows-amd64.exe
```

### Docker Build

```bash
# Build image
docker build -t chinese-simplifier:latest .

# Run container
docker run -p 8081:8081 \
  -e API_KEY=test-key \
  -v $(pwd)/data:/app/data \
  chinese-simplifier:latest

# Push to registry
docker tag chinese-simplifier:latest registry.example.com/simplifier:1.0.0
docker push registry.example.com/simplifier:1.0.0
```

### Dockerfile Explanation

```dockerfile
# Stage 1: Build
FROM golang:1.21 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o simplifier .

# Stage 2: Runtime
FROM alpine:latest
RUN apk --no-cache add ca-certificates
RUN adduser -D simplifier
WORKDIR /app
COPY --from=builder /app/simplifier .
COPY --from=builder /app/data ./data
USER simplifier
EXPOSE 8081
CMD ["./simplifier"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simplifier
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
        image: registry.example.com/simplifier:1.0.0
        ports:
        - containerPort: 8081
        env:
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secret
              key: api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8081
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8081
          initialDelaySeconds: 5
          periodSeconds: 5
```

### CI/CD Pipeline

**.github/workflows/go.yml**:
```yaml
name: Go CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-go@v4
      with:
        go-version: '1.21'
    - run: go mod download
    - run: go test -v ./...
    - run: golangci-lint run

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-go@v4
      with:
        go-version: '1.21'
    - run: go build -o simplifier
    - uses: actions/upload-artifact@v3
      with:
        name: simplifier-binary
        path: simplifier
```

---

## Troubleshooting

### Common Issues

**1. HSK Dictionary Not Found**
```
ERROR: Failed to load HSK: open data/hsk.json: no such file or directory
```
**Solution:** Ensure `hsk.json` exists in data directory or set `DATA_DIR` environment variable.

**2. Embeddings Loading Slow**
```
INFO: Loading embeddings... (this may take a few minutes)
```
**Solution:** Use cache by running once with `--preload` flag, or set `NO_EMBEDDINGS=true`.

**3. Rate Limit Errors**
```json
{"error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests"}}
```
**Solution:** Check your tier limits in environment variables, wait for reset, or upgrade tier.

**4. API Key Invalid**
```json
{"error": {"code": "INVALID_API_KEY", "message": "Invalid API key"}}
```
**Solution:** Verify `API_KEY` environment variable matches request header.

**5. High Memory Usage**
```
RSS: 500MB
```
**Solution:** Reduce `MAX_HSK_LEVEL` or set `NO_EMBEDDINGS=true` for dictionary-only mode.

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=debug
go run main.go
```

Debug logs show:
- Request details
- Processing steps
- Data loading progress

### Performance Profiling

```bash
# CPU profile
go test -cpuprofile=cpu.prof -bench=.
go tool pprof cpu.prof

# Memory profile
go test -memprofile=mem.prof -bench=.
go tool pprof mem.prof

# HTTP profiling
import _ "net/http/pprof"
# Access http://localhost:8081/debug/pprof/
```

---

## Contributing

### Code Style

Follow [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments):

- Use `go fmt` for formatting
- Use `golint` for linting
- Keep functions small and focused
- Add tests for new features
- Document exported identifiers

### Pull Request Process

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**PR Checklist:**
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] `go fmt` run
- [ ] `golangci-lint` passes
- [ ] All tests pass

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new simplification algorithm
fix: correct HSK level lookup
docs: update API examples
refactor: improve embedding cache
test: add integration tests for /analyze
```

### Reporting Issues

Use GitHub Issues with templates:

**Bug Report:**
- Description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, Go version)

**Feature Request:**
- Problem statement
- Proposed solution
- Use cases
- Alternatives considered

---

## Additional Resources

- [Go Documentation](https://golang.org/doc/)
- [Effective Go](https://golang.org/doc/effective_go.html)
- [Go by Example](https://gobyexample.com/)
- [Tencent AILab Embeddings](https://ai.tencent.com/ailab/nlp/en/embedding.html)
- [HSK Dictionary Reference](https://github.com/Coerphinus/chinese-dictionary)

---

**Version:** 1.0.0
**Last Updated:** March 2024
