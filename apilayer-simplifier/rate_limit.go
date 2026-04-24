package main

import (
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"
)

// RateLimiter лимитер запросов
type RateLimiter struct {
	requests   map[string][]time.Time
	limits     map[string]int
	mu         sync.RWMutex
	windowSize time.Duration
}

// NewRateLimiter создаёт новый лимитер
func NewRateLimiter() *RateLimiter {
	rl := &RateLimiter{
		requests:   make(map[string][]time.Time),
		limits:     make(map[string]int),
		windowSize: 24 * time.Hour, // Суточное окно
	}
	rl.loadLimits()
	return rl
}

// loadLimits загружает лимиты из переменных окружения
func (rl *RateLimiter) loadLimits() {
	rl.limits["free"] = getEnvInt("RATE_LIMIT_FREE", 100)
	rl.limits["basic"] = getEnvInt("RATE_LIMIT_BASIC", 1000)
	rl.limits["pro"] = getEnvInt("RATE_LIMIT_PRO", 10000)
	rl.limits["enterprise"] = getEnvInt("RATE_LIMIT_ENTERPRISE", 100000)
}

// getEnvInt получает integer из переменной окружения
func getEnvInt(key string, defaultVal int) int {
	if val := os.Getenv(key); val != "" {
		if intVal, err := strconv.Atoi(val); err == nil {
			return intVal
		}
	}
	return defaultVal
}

// Allow проверяет, можно ли сделать запрос
func (rl *RateLimiter) Allow(apiKey string, tier string) bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	// Получаем лимит для тарифа
	limit, exists := rl.limits[tier]
	if !exists {
		limit = rl.limits["free"]
	}

	// Enterprise без лимитов
	if tier == "enterprise" {
		return true
	}

	now := time.Now()
	windowStart := now.Add(-rl.windowSize)

	// Получаем существующие запросы
	requests, exists := rl.requests[apiKey]
	if !exists {
		rl.requests[apiKey] = []time.Time{now}
		return true
	}

	// Фильтруем запросы за последние 24 часа
	validRequests := make([]time.Time, 0, len(requests))
	for _, t := range requests {
		if t.After(windowStart) {
			validRequests = append(validRequests, t)
		}
	}

	// Проверяем лимит
	if len(validRequests) >= limit {
		rl.requests[apiKey] = validRequests
		return false
	}

	// Добавляем новый запрос
	rl.requests[apiKey] = append(validRequests, now)
	return true
}

// GetRemaining возвращает оставшееся количество запросов
func (rl *RateLimiter) GetRemaining(apiKey string, tier string) int {
	rl.mu.RLock()
	defer rl.mu.RUnlock()

	limit, exists := rl.limits[tier]
	if !exists {
		limit = rl.limits["free"]
	}

	if tier == "enterprise" {
		return -1 // Безлимитно
	}

	now := time.Now()
	windowStart := now.Add(-rl.windowSize)

	requests, exists := rl.requests[apiKey]
	if !exists {
		return limit
	}

	// Считаем активные запросы
	count := 0
	for _, t := range requests {
		if t.After(windowStart) {
			count++
		}
	}

	remaining := limit - count
	if remaining < 0 {
		return 0
	}
	return remaining
}

// GetResetTime возвращает время сброса лимита
func (rl *RateLimiter) GetResetTime() time.Time {
	return time.Now().Add(rl.windowSize).Truncate(rl.windowSize)
}

// Cleanup очищает старые записи (запускается в горутине)
func (rl *RateLimiter) Cleanup() {
	ticker := time.NewTicker(time.Hour)
	defer ticker.Stop()

	for range ticker.C {
		rl.mu.Lock()
		now := time.Now()
		windowStart := now.Add(-rl.windowSize)

		for apiKey, requests := range rl.requests {
			validRequests := make([]time.Time, 0, len(requests))
			for _, t := range requests {
				if t.After(windowStart) {
					validRequests = append(validRequests, t)
				}
			}
			if len(validRequests) == 0 {
				delete(rl.requests, apiKey)
			} else {
				rl.requests[apiKey] = validRequests
			}
		}
		rl.mu.Unlock()
	}
}

// RateLimitMiddleware middleware для rate limiting
func RateLimitMiddleware(rl *RateLimiter) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			apiKey := r.Header.Get("X-API-Key")
			tier := r.Header.Get("X-API-Key-Tier")

			if apiKey != "" && tier != "" {
				if !rl.Allow(apiKey, tier) {
					remaining := rl.GetRemaining(apiKey, tier)
					resetTime := rl.GetResetTime()

					w.Header().Set("X-RateLimit-Limit", strconv.Itoa(rl.limits[tier]))
					w.Header().Set("X-RateLimit-Remaining", strconv.Itoa(remaining))
					w.Header().Set("X-RateLimit-Reset", strconv.FormatInt(resetTime.Unix(), 10))
					w.Header().Set("Retry-After", strconv.FormatInt(resetTime.Unix()-time.Now().Unix(), 10))

					writeAPIError(w, http.StatusTooManyRequests, "RATE_LIMIT_EXCEEDED", "Too many requests")
					return
				}

				// Добавляем заголовки с информацией о лимитах
				remaining := rl.GetRemaining(apiKey, tier)
				resetTime := rl.GetResetTime()

				w.Header().Set("X-RateLimit-Limit", strconv.Itoa(rl.limits[tier]))
				w.Header().Set("X-RateLimit-Remaining", strconv.Itoa(remaining))
				w.Header().Set("X-RateLimit-Reset", strconv.FormatInt(resetTime.Unix(), 10))
			}

			next.ServeHTTP(w, r)
		})
	}
}
