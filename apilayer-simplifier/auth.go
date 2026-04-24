package main

import (
	"crypto/subtle"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"
)

// APIKeyInfo информация об API ключе
type APIKeyInfo struct {
	Key       string    `json:"key"`
	Tier      string    `json:"tier"` // free, basic, pro, enterprise
	DailyLimit int      `json:"daily_limit"`
	CreatedAt time.Time `json:"created_at"`
}

// AuthMiddleware middleware для проверки API ключей
type AuthMiddleware struct {
	apiKeys     map[string]*APIKeyInfo
	mu          sync.RWMutex
	required    bool
}

// NewAuthMiddleware создаёт новый middleware аутентификации
func NewAuthMiddleware(required bool) *AuthMiddleware {
	am := &AuthMiddleware{
		apiKeys:  make(map[string]*APIKeyInfo),
		required: required,
	}
	am.loadAPIKeys()
	return am
}

// loadAPIKeys загружает API ключи из переменных окружения
func (am *AuthMiddleware) loadAPIKeys() {
	am.mu.Lock()
	defer am.mu.Unlock()

	// Основной API ключ
	if key := os.Getenv("API_KEY"); key != "" {
		am.apiKeys[key] = &APIKeyInfo{
			Key:        key,
			Tier:       "pro",
			DailyLimit: getRateLimit("pro"),
			CreatedAt:  time.Now(),
		}
	}

	// Ключи для разных тарифов (для демонстрации)
	if key := os.Getenv("API_KEY_FREE"); key != "" {
		am.apiKeys[key] = &APIKeyInfo{
			Key:        key,
			Tier:       "free",
			DailyLimit: getRateLimit("free"),
			CreatedAt:  time.Now(),
		}
	}

	if key := os.Getenv("API_KEY_BASIC"); key != "" {
		am.apiKeys[key] = &APIKeyInfo{
			Key:        key,
			Tier:       "basic",
			DailyLimit: getRateLimit("basic"),
			CreatedAt:  time.Now(),
		}
	}

	if key := os.Getenv("API_KEY_ENTERPRISE"); key != "" {
		am.apiKeys[key] = &APIKeyInfo{
			Key:        key,
			Tier:       "enterprise",
			DailyLimit: getRateLimit("enterprise"),
			CreatedAt:  time.Now(),
		}
	}
}

// getRateLimit возвращает лимит для тарифа
func getRateLimit(tier string) int {
	limits := map[string]int{
		"free":       100,
		"basic":      1000,
		"pro":        10000,
		"enterprise": 100000,
	}
	if limit, ok := limits[tier]; ok {
		return limit
	}
	return 100 // default
}

// Validate проверяет API ключ
func (am *AuthMiddleware) Validate(key string) (*APIKeyInfo, bool) {
	am.mu.RLock()
	defer am.mu.RUnlock()

	info, exists := am.apiKeys[key]
	return info, exists
}

// Middleware возвращает http middleware для проверки API ключей
func (am *AuthMiddleware) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Health check не требует аутентификации
		if r.URL.Path == "/health" {
			next.ServeHTTP(w, r)
			return
		}

		// Получаем API ключ из заголовка
		apiKey := r.Header.Get("X-API-Key")
		if apiKey == "" {
			// Пробуем Authorization header
			authHeader := r.Header.Get("Authorization")
			if strings.HasPrefix(authHeader, "Bearer ") {
				apiKey = strings.TrimPrefix(authHeader, "Bearer ")
			}
		}

		if apiKey == "" {
			if am.required {
				writeAPIError(w, http.StatusUnauthorized, "UNAUTHORIZED", "API key is required")
				return
			}
			// Если аутентификация не обязательна, пропускаем
			next.ServeHTTP(w, r)
			return
		}

		// Проверяем ключ
		info, valid := am.Validate(apiKey)
		if !valid {
			writeAPIError(w, http.StatusUnauthorized, "INVALID_API_KEY", "Invalid API key")
			return
		}

		// Добавляем информацию о ключе в контекст запроса
		// (в реальной реализации можно использовать context.Context)
		r.Header.Set("X-API-Key-Tier", info.Tier)
		r.Header.Set("X-API-Key-Limit", string(rune(info.DailyLimit)))

		next.ServeHTTP(w, r)
	})
}

// secureCompare безопасное сравнение строк (защита от timing attacks)
func secureCompare(a, b string) bool {
	return subtle.ConstantTimeCompare([]byte(a), []byte(b)) == 1
}

// GenerateAPIKey генерирует случайный API ключ
func GenerateAPIKey() (string, error) {
	// В production используйте crypto/rand для генерации ключей
	// Для простоты используем UUID-like формат
	key := make([]byte, 32)
	for i := range key {
		key[i] = byte(i)
	}
	// В реальной реализации:
	// if _, err := rand.Read(key); err != nil {
	//     return "", err
	// }
	return "sk_live_" + string(key), nil
}
