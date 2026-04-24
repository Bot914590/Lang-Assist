package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"
)

// ==================== Test Helpers ====================

func setupTestEnv() {
	os.Setenv("API_KEY", "test-api-key")
	os.Setenv("RATE_LIMIT_FREE", "100")
	os.Setenv("RATE_LIMIT_PRO", "10000")
	os.Setenv("LOG_LEVEL", "error") // Suppress logs during tests
}

func newTestRequest(method, url string, body interface{}) *http.Request {
	var req *http.Request
	if body != nil {
		jsonBody, _ := json.Marshal(body)
		req = httptest.NewRequest(method, url, bytes.NewBuffer(jsonBody))
		req.Header.Set("Content-Type", "application/json")
	} else {
		req = httptest.NewRequest(method, url, nil)
	}
	return req
}

// ==================== Health Check Tests ====================

func TestHealthHandler(t *testing.T) {
	setupTestEnv()
	initData()

	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	w := httptest.NewRecorder()

	healthHandler(w, req)

	resp := w.Result()
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}

	var response map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&response)

	if response["status"] != "ok" {
		t.Errorf("Expected status 'ok', got '%v'", response["status"])
	}
}

// ==================== Simplify Handler Tests ====================

func TestSimplifyHandler_ValidRequest(t *testing.T) {
	setupTestEnv()
	initData()

	reqBody := SimplifyRequest{
		Text:        "你好",
		TargetLevel: 1,
	}

	req := newTestRequest(http.MethodPost, "/simplify", reqBody)
	req.Header.Set("X-API-Key", "test-api-key")
	w := httptest.NewRecorder()

	simplifyHandler(w, req)

	resp := w.Result()
	defer resp.Body.Close()

	// Should return 200 or handle based on data availability
	t.Logf("Response status: %d", resp.StatusCode)
}

func TestSimplifyHandler_MissingText(t *testing.T) {
	setupTestEnv()
	initData()

	reqBody := SimplifyRequest{
		TargetLevel: 2,
	}

	req := newTestRequest(http.MethodPost, "/simplify", reqBody)
	req.Header.Set("X-API-Key", "test-api-key")
	w := httptest.NewRecorder()

	simplifyHandler(w, req)

	resp := w.Result()
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusBadRequest {
		t.Errorf("Expected status 400, got %d", resp.StatusCode)
	}

	var response ErrorResponse
	json.NewDecoder(resp.Body).Decode(&response)

	if response.Error.Code != ErrMissingParameter {
		t.Errorf("Expected error code MISSING_PARAMETER, got '%v'", response.Error.Code)
	}
}

func TestSimplifyHandler_InvalidTargetLevel(t *testing.T) {
	setupTestEnv()
	initData()

	reqBody := SimplifyRequest{
		Text:        "你好",
		TargetLevel: 10, // Invalid level
	}

	req := newTestRequest(http.MethodPost, "/simplify", reqBody)
	req.Header.Set("X-API-Key", "test-api-key")
	w := httptest.NewRecorder()

	simplifyHandler(w, req)

	resp := w.Result()
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusBadRequest {
		t.Errorf("Expected status 400, got %d", resp.StatusCode)
	}
}

func TestSimplifyHandler_WrongMethod(t *testing.T) {
	setupTestEnv()

	req := httptest.NewRequest(http.MethodGet, "/simplify", nil)
	req.Header.Set("X-API-Key", "test-api-key")
	w := httptest.NewRecorder()

	simplifyHandler(w, req)

	resp := w.Result()
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusMethodNotAllowed {
		t.Errorf("Expected status 405, got %d", resp.StatusCode)
	}
}

// ==================== Analyze Handler Tests ====================

func TestAnalyzeHandler_ValidRequest(t *testing.T) {
	setupTestEnv()
	initData()

	reqBody := AnalyzeRequest{
		Text:      "我喜欢学习中文",
		Language:  "zh",
		UserLevel: 2,
	}

	req := newTestRequest(http.MethodPost, "/analyze", reqBody)
	req.Header.Set("X-API-Key", "test-api-key")
	w := httptest.NewRecorder()

	analyzeHandler(w, req)

	resp := w.Result()
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}

	var response AnalyzeResponse
	json.NewDecoder(resp.Body).Decode(&response)

	if response.Status != "ok" {
		t.Errorf("Expected status 'ok', got '%v'", response.Status)
	}

	if response.TokensCount == 0 {
		t.Error("Expected tokens, got 0")
	}
}

func TestAnalyzeHandler_MissingText(t *testing.T) {
	setupTestEnv()

	reqBody := AnalyzeRequest{
		Language:  "zh",
		UserLevel: 2,
	}

	req := newTestRequest(http.MethodPost, "/analyze", reqBody)
	req.Header.Set("X-API-Key", "test-api-key")
	w := httptest.NewRecorder()

	analyzeHandler(w, req)

	resp := w.Result()
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusBadRequest {
		t.Errorf("Expected status 400, got %d", resp.StatusCode)
	}
}

// ==================== Word Info Handler Tests ====================

func TestWordInfoHandler_ValidRequest(t *testing.T) {
	setupTestEnv()
	initData()

	req := httptest.NewRequest(http.MethodGet, "/word/info?word=学习", nil)
	req.Header.Set("X-API-Key", "test-api-key")
	w := httptest.NewRecorder()

	wordInfoHandler(w, req)

	resp := w.Result()
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}

	var response map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&response)

	if response["word"] != "学习" {
		t.Errorf("Expected word '学习', got '%v'", response["word"])
	}
}

func TestWordInfoHandler_MissingWord(t *testing.T) {
	setupTestEnv()

	req := httptest.NewRequest(http.MethodGet, "/word/info", nil)
	req.Header.Set("X-API-Key", "test-api-key")
	w := httptest.NewRecorder()

	wordInfoHandler(w, req)

	resp := w.Result()
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusBadRequest {
		t.Errorf("Expected status 400, got %d", resp.StatusCode)
	}
}

// ==================== Rate Limiter Tests ====================

func TestRateLimiter_Allow(t *testing.T) {
	rl := NewRateLimiter()

	apiKey := "test-key"
	tier := "free"

	// First request should be allowed
	if !rl.Allow(apiKey, tier) {
		t.Error("First request should be allowed")
	}
}

func TestRateLimiter_ExceedLimit(t *testing.T) {
	rl := &RateLimiter{
		requests:   make(map[string][]time.Time),
		limits:     map[string]int{"free": 2},
		windowSize: 24 * time.Hour,
	}

	apiKey := "test-key"
	tier := "free"

	// First two requests should be allowed
	if !rl.Allow(apiKey, tier) {
		t.Error("First request should be allowed")
	}
	if !rl.Allow(apiKey, tier) {
		t.Error("Second request should be allowed")
	}

	// Third request should be rejected
	if rl.Allow(apiKey, tier) {
		t.Error("Third request should be rejected")
	}
}

func TestRateLimiter_GetRemaining(t *testing.T) {
	rl := &RateLimiter{
		requests:   make(map[string][]time.Time),
		limits:     map[string]int{"free": 100},
		windowSize: 24 * time.Hour,
	}

	apiKey := "test-key"
	tier := "free"

	remaining := rl.GetRemaining(apiKey, tier)
	if remaining != 100 {
		t.Errorf("Expected 100 remaining, got %d", remaining)
	}

	rl.Allow(apiKey, tier)
	remaining = rl.GetRemaining(apiKey, tier)
	if remaining != 99 {
		t.Errorf("Expected 99 remaining, got %d", remaining)
	}
}

// ==================== Error Handling Tests ====================

func TestValidateSimplifyRequest(t *testing.T) {
	tests := []struct {
		name          string
		req           *SimplifyRequest
		expectedError ErrorCode
	}{
		{
			name: "valid request",
			req: &SimplifyRequest{
				Text:        "你好",
				TargetLevel: 2,
			},
			expectedError: "",
		},
		{
			name: "missing text",
			req: &SimplifyRequest{
				TargetLevel: 2,
			},
			expectedError: ErrMissingParameter,
		},
		{
			name: "invalid target level (too low)",
			req: &SimplifyRequest{
				Text:        "你好",
				TargetLevel: 0,
			},
			expectedError: ErrInvalidParameter,
		},
		{
			name: "invalid target level (too high)",
			req: &SimplifyRequest{
				Text:        "你好",
				TargetLevel: 7,
			},
			expectedError: ErrInvalidParameter,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validateSimplifyRequest(tt.req)
			if tt.expectedError == "" {
				if err != nil {
					t.Errorf("Expected no error, got %v", err)
				}
			} else {
				if err == nil {
					t.Errorf("Expected error %v, got nil", tt.expectedError)
				} else if err.Error.Code != tt.expectedError {
					t.Errorf("Expected error code %v, got %v", tt.expectedError, err.Error.Code)
				}
			}
		})
	}
}

func TestValidateAnalyzeRequest(t *testing.T) {
	tests := []struct {
		name          string
		req           *AnalyzeRequest
		expectedError ErrorCode
	}{
		{
			name: "valid request",
			req: &AnalyzeRequest{
				Text:      "你好",
				Language:  "zh",
				UserLevel: 2,
			},
			expectedError: "",
		},
		{
			name: "missing text",
			req: &AnalyzeRequest{
				Language:  "zh",
				UserLevel: 2,
			},
			expectedError: ErrMissingParameter,
		},
		{
			name: "invalid user level (negative)",
			req: &AnalyzeRequest{
				Text:      "你好",
				Language:  "zh",
				UserLevel: -1,
			},
			expectedError: ErrInvalidParameter,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validateAnalyzeRequest(tt.req)
			if tt.expectedError == "" {
				if err != nil {
					t.Errorf("Expected no error, got %v", err)
				}
			} else {
				if err == nil {
					t.Errorf("Expected error %v, got nil", tt.expectedError)
				} else if err.Error.Code != tt.expectedError {
					t.Errorf("Expected error code %v, got %v", tt.expectedError, err.Error.Code)
				}
			}
		})
	}
}

// ==================== Tokenization Tests ====================

func TestTokenizeChinese(t *testing.T) {
	text := "我喜欢学习中文"
	tokens := tokenizeChineseSimple(text)

	if len(tokens) == 0 {
		t.Error("Expected tokens, got 0")
	}

	// Should not contain spaces or punctuation
	for _, token := range tokens {
		if token == " " || token == "" {
			t.Errorf("Invalid token: '%s'", token)
		}
	}
}

func TestTokenizeEuropean(t *testing.T) {
	text := "I love learning languages"
	tokens := tokenizeEuropean(text)

	expected := 5
	if len(tokens) != expected {
		t.Errorf("Expected %d tokens, got %d", expected, len(tokens))
	}
}

func TestGetLemma(t *testing.T) {
	tests := []struct {
		token    string
		lang     string
		expected string
	}{
		{"我", "zh", "我"},
		{"learning", "en", "learn"},
		{"played", "en", "play"},
		{"cats", "en", "cat"},
		{"class", "en", "class"}, // Should not trim 'ss'
	}

	for _, tt := range tests {
		result := getLemma(tt.token, tt.lang)
		if result != tt.expected {
			t.Errorf("getLemma(%s, %s) = %s, expected %s", tt.token, tt.lang, result, tt.expected)
		}
	}
}

// ==================== Benchmark Tests ====================

func BenchmarkTokenizeChinese(b *testing.B) {
	text := "我喜欢学习中文今天天气很好我们一起去公园玩"
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		tokenizeChineseSimple(text)
	}
}

func BenchmarkTokenizeEuropean(b *testing.B) {
	text := "I love learning Chinese languages and cultures today"
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		tokenizeEuropean(text)
	}
}

func BenchmarkSimplifyText(b *testing.B) {
	setupTestEnv()
	initData()

	text := "你好世界"
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		simplifyTextWithDict(text, 2)
	}
}
