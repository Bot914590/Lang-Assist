package main

import (
	"encoding/json"
	"net/http"
)

// ErrorCode код ошибки
type ErrorCode string

// Предопределённые коды ошибок
const (
	ErrBadRequest          ErrorCode = "BAD_REQUEST"
	ErrInvalidJSON         ErrorCode = "INVALID_JSON"
	ErrMissingParameter    ErrorCode = "MISSING_PARAMETER"
	ErrInvalidParameter    ErrorCode = "INVALID_PARAMETER"
	ErrUnauthorized        ErrorCode = "UNAUTHORIZED"
	ErrInvalidAPIKey       ErrorCode = "INVALID_API_KEY"
	ErrForbidden           ErrorCode = "FORBIDDEN"
	ErrNotFound            ErrorCode = "NOT_FOUND"
	ErrRateLimitExceeded   ErrorCode = "RATE_LIMIT_EXCEEDED"
	ErrServiceUnavailable  ErrorCode = "SERVICE_UNAVAILABLE"
	ErrInternalServer      ErrorCode = "INTERNAL_SERVER_ERROR"
	ErrHSKNotLoaded        ErrorCode = "HSK_NOT_LOADED"
	ErrEmbeddingsNotLoaded ErrorCode = "EMBEDDINGS_NOT_LOADED"
	ErrMethodNotAllowed    ErrorCode = "METHOD_NOT_ALLOWED"
)

// APIError структура ошибки API
type APIError struct {
	Error struct {
		Code       ErrorCode      `json:"code"`
		Message    string         `json:"message"`
		Details    interface{}    `json:"details,omitempty"`
		StatusCode int            `json:"status_code"`
	} `json:"error"`
}

// ErrorResponse структура ответа с ошибкой
type ErrorResponse struct {
	Error struct {
		Code       ErrorCode      `json:"code"`
		Message    string         `json:"message"`
		Details    interface{}    `json:"details,omitempty"`
		StatusCode int            `json:"-"`
	} `json:"error"`
}

// writeAPIError записывает ответ с ошибкой
func writeAPIError(w http.ResponseWriter, statusCode int, code ErrorCode, message string) {
	writeAPIErrorWithDetails(w, statusCode, code, message, nil)
}

// writeAPIErrorWithDetails записывает ответ с ошибкой и деталями
func writeAPIErrorWithDetails(w http.ResponseWriter, statusCode int, code ErrorCode, message string, details interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.WriteHeader(statusCode)

	response := ErrorResponse{}
	response.Error.Code = code
	response.Error.Message = message
	response.Error.StatusCode = statusCode
	response.Error.Details = details

	json.NewEncoder(w).Encode(response)
}

// writeSuccess записывает успешный ответ
func writeSuccess(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(data)
}

// writeCreated записывает ответ с созданным ресурсом
func writeCreated(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(data)
}

// validateSimplifyRequest валидирует запрос на упрощение
func validateSimplifyRequest(req *SimplifyRequest) *ErrorResponse {
	if req.Text == "" {
		return &ErrorResponse{Error: struct {
			Code       ErrorCode      `json:"code"`
			Message    string         `json:"message"`
			Details    interface{}    `json:"details,omitempty"`
			StatusCode int            `json:"-"`
		}{Code: ErrMissingParameter, Message: "Field 'text' is required", StatusCode: http.StatusBadRequest}}
	}

	if req.TargetLevel < 1 || req.TargetLevel > 6 {
		return &ErrorResponse{Error: struct {
			Code       ErrorCode      `json:"code"`
			Message    string         `json:"message"`
			Details    interface{}    `json:"details,omitempty"`
			StatusCode int            `json:"-"`
		}{Code: ErrInvalidParameter, Message: "Field 'target_level' must be between 1 and 6", StatusCode: http.StatusBadRequest}}
	}

	return nil
}

// validateAnalyzeRequest валидирует запрос на анализ
func validateAnalyzeRequest(req *AnalyzeRequest) *ErrorResponse {
	if req.Text == "" {
		return &ErrorResponse{Error: struct {
			Code       ErrorCode      `json:"code"`
			Message    string         `json:"message"`
			Details    interface{}    `json:"details,omitempty"`
			StatusCode int            `json:"-"`
		}{Code: ErrMissingParameter, Message: "Field 'text' is required", StatusCode: http.StatusBadRequest}}
	}

	if req.UserLevel < 0 || req.UserLevel > 6 {
		return &ErrorResponse{Error: struct {
			Code       ErrorCode      `json:"code"`
			Message    string         `json:"message"`
			Details    interface{}    `json:"details,omitempty"`
			StatusCode int            `json:"-"`
		}{Code: ErrInvalidParameter, Message: "Field 'user_level' must be between 0 and 6", StatusCode: http.StatusBadRequest}}
	}

	return nil
}
