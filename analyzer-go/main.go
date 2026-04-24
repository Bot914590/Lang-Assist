package main

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"unicode"
)

// Входные данные
type AnalyzeRequest struct {
	Text      string `json:"text"`
	Language  string `json:"lang"`
	UserLevel int    `json:"user_level"`
}

// Токен с полной информацией
type Token struct {
	Value     string `json:"value"`
	Lemma     string `json:"lemma,omitempty"`
	Frequency int    `json:"frequency"`
	Positions []int  `json:"positions,omitempty"`
	HSK       int    `json:"hsk,omitempty"`
	IsKnown   bool   `json:"is_known,omitempty"`
}

// Ответ API
type AnalyzeResponse struct {
	Status      string  `json:"status"`
	TextID      int     `json:"text_id,omitempty"`
	TokensCount int     `json:"tokens_count"`
	Tokens      []Token `json:"tokens"`
}

// HSK словарь (заглушка для MVP)
var hskDict = map[string]int{
	"我": 1, "你": 1, "他": 1, "她": 1, "是": 1, "的": 1, "了": 1, "在": 1, "有": 1, "这": 1,
	"个": 1, "中": 1, "大": 1, "来": 1, "上": 1, "国": 1, "到": 1, "们": 1, "以": 1, "后": 1,
	"好": 2, "学": 2, "生": 2, "日": 2, "月": 2, "年": 2, "人": 2, "工": 2, "作": 2, "活": 2,
	"喜欢": 3, "学习": 3, "朋": 3, "友": 3, "时": 3, "间": 3, "问": 3, "题": 3, "现": 3,
}

func main() {
	http.HandleFunc("/analyze", analyzeHandler)
	http.HandleFunc("/health", healthHandler)

	port := os.Getenv("PORT")
	if port == "" {
		port = ":8080"
	} else {
		port = ":" + port
	}
	log.Println("Go Analyzer Service is running on port", port)
	log.Fatal(http.ListenAndServe(port, nil))
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

func analyzeHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	if r.Method == http.MethodOptions {
		w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		w.WriteHeader(http.StatusOK)
		return
	}

	if r.Method != http.MethodPost {
		http.Error(w, `{"error":"Method not allowed"}`, http.StatusMethodNotAllowed)
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, `{"error":"Failed to read request body"}`, http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	var req AnalyzeRequest
	if err := json.Unmarshal(body, &req); err != nil {
		http.Error(w, `{"error":"Invalid JSON"}`, http.StatusBadRequest)
		return
	}

	response := analyzeText(req.Text, req.Language, req.UserLevel)

	if err := json.NewEncoder(w).Encode(response); err != nil {
		http.Error(w, `{"error":"Failed to encode response"}`, http.StatusInternalServerError)
		return
	}
}

func analyzeText(text string, lang string, userLevel int) AnalyzeResponse {
	var rawTokens []string

	// Токенизация в зависимости от языка
	if strings.HasPrefix(strings.ToLower(lang), "zh") {
		rawTokens = tokenizeChinese(text)
	} else {
		rawTokens = tokenizeEuropean(text)
	}

	// Подсчёт частотности и позиций
	freqMap := make(map[string]int)
	posMap := make(map[string][]int)

	for i, token := range rawTokens {
		freqMap[token]++
		posMap[token] = append(posMap[token], i)
	}

	// Формирование токенов с метаданными
	tokens := make([]Token, 0, len(freqMap))
	for value, frequency := range freqMap {
		token := Token{
			Value:     value,
			Lemma:     getLemma(value, lang),
			Frequency: frequency,
			Positions: posMap[value],
			HSK:       getHSKLevel(value, lang),
			IsKnown:   isKnownWord(value, userLevel, lang),
		}
		tokens = append(tokens, token)
	}

	return AnalyzeResponse{
		Status:      "ok",
		TokensCount: len(rawTokens),
		Tokens:      tokens,
	}
}

// Токенизация китайского текста (посимвольная для MVP)
func tokenizeChinese(text string) []string {
	var tokens []string
	for _, r := range text {
		if unicode.IsSpace(r) {
			continue
		}
		// Пропускаем ASCII пунктуацию
		if r <= 127 && (unicode.IsPunct(r) || unicode.IsSymbol(r)) {
			continue
		}
		tokens = append(tokens, string(r))
	}
	return tokens
}

// Токенизация европейских языков (по пробелам)
func tokenizeEuropean(text string) []string {
	var tokens []string
	words := strings.Fields(text)
	for _, word := range words {
		clean := strings.TrimSpace(word)
		clean = strings.Trim(clean, ".,;:?!@#$%^&*()_+-=[]{}|\\/<>~`\"'")
		if clean != "" {
			tokens = append(tokens, clean)
		}
	}
	return tokens
}

// Получение леммы (заглушка для MVP)
func getLemma(token string, lang string) string {
	// Для китайского лемма = токен (нет склонений)
	if strings.HasPrefix(strings.ToLower(lang), "zh") {
		return token
	}
	// Простая эвристика для английского (окончания -s, -ed, -ing)
	lower := strings.ToLower(token)
	if strings.HasSuffix(lower, "ing") && len(token) > 4 {
		return lower[:len(lower)-3]
	}
	if strings.HasSuffix(lower, "ed") && len(token) > 3 {
		return lower[:len(lower)-2]
	}
	if strings.HasSuffix(lower, "s") && !strings.HasSuffix(lower, "ss") && len(token) > 2 {
		return lower[:len(lower)-1]
	}
	return token
}

// Получение уровня HSK (заглушка)
func getHSKLevel(token string, lang string) int {
	if !strings.HasPrefix(strings.ToLower(lang), "zh") {
		return 0
	}
	if level, ok := hskDict[token]; ok {
		return level
	}
	return 0 // Не в словаре HSK
}

// Проверка, известно ли слово пользователю
func isKnownWord(token string, userLevel int, lang string) bool {
	if !strings.HasPrefix(strings.ToLower(lang), "zh") {
		return false
	}
	hskLevel := getHSKLevel(token, lang)
	return hskLevel > 0 && hskLevel <= userLevel
}
