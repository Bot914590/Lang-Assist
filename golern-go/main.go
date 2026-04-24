package main

import (
	"encoding/json"
	"flag"
	"io"
	"log"
	"math"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"sync"
	"unicode"
)

// ==================== Request/Response структуры ====================

// AnalyzeRequest запрос на анализ текста
type AnalyzeRequest struct {
	Text      string `json:"text"`
	Language  string `json:"lang"`
	UserLevel int    `json:"user_level"`
}

// Token токен с метаданными
type Token struct {
	Value     string `json:"value"`
	Lemma     string `json:"lemma,omitempty"`
	Frequency int    `json:"frequency"`
	Positions []int  `json:"positions,omitempty"`
	HSK       int    `json:"hsk,omitempty"`
	IsKnown   bool   `json:"is_known,omitempty"`
}

// AnalyzeResponse ответ анализа текста
type AnalyzeResponse struct {
	Status      string  `json:"status"`
	TextID      int     `json:"text_id,omitempty"`
	TokensCount int     `json:"tokens_count"`
	Tokens      []Token `json:"tokens"`
}

// SimplifyRequest запрос на упрощение текста
type SimplifyRequest struct {
	Text        string `json:"text"`
	Language    string `json:"lang,omitempty"`
	TargetLevel int    `json:"target_level"`
}

// SimplifyResponse ответ упрощения текста
type SimplifyResponse struct {
	Status         string            `json:"status"`
	OriginalText   string            `json:"original_text"`
	SimplifiedText string            `json:"simplified_text"`
	Replacements   []WordReplacement `json:"replacements"`
	TargetLevel    int               `json:"target_level"`
	TotalTokens    int               `json:"total_tokens"`
	ReplacedCount  int               `json:"replaced_count"`
}

// WordReplacement замена слова
type WordReplacement struct {
	Original    string  `json:"original"`
	Replacement string  `json:"replacement"`
	Reason      string  `json:"reason"`
	HSKLevel    int     `json:"hsk_level"`
	Similarity  float32 `json:"similarity"`
}

// ==================== Глобальные переменные ====================

var (
	hskDict       map[string]int
	hskEntries    []HSKEntry
	embeddings    map[string][]float32
	vectorSize    int
	embeddingsErr error
	initOnce      sync.Once
	dataDir       string
	cacheDir      string
	noEmbeddings  bool
	maxHSKLevel   int
)

// ==================== Инициализация ====================

// initData инициализирует все данные (HSK + эмбеддинги)
func initData() {
	initOnce.Do(func() {
		// Определяем директорию с данными
		dataDir = getDataDir()
		cacheDir = filepath.Join(dataDir, "cache")
		
		log.Printf("Data directory: %s", dataDir)
		log.Printf("Cache directory: %s", cacheDir)
		log.Printf("Load embeddings: %v", !noEmbeddings)
		log.Printf("Max HSK level: %d", maxHSKLevel)

		// Загружаем HSK словарь
		log.Println("Loading HSK dictionary...")
		var err error
		hskDict, hskEntries, err = LoadHSK(dataDir)
		if err != nil {
			embeddingsErr = err
			log.Printf("Error loading HSK: %v", err)
			return
		}
		log.Printf("HSK dictionary loaded: %d entries", len(hskDict))

		// Загружаем эмбеддинги если нужно
		if !noEmbeddings {
			embPath := filepath.Join(dataDir, "light_Tencent_AILab_ChineseEmbedding.bin")
			cachePath := filepath.Join(cacheDir, "embeddings_hsk"+string(rune(maxHSKLevel+'0'))+".gob")
			
			log.Printf("Loading embeddings (max HSK %d)...", maxHSKLevel)
			embeddings, vectorSize, err = LoadEmbeddingsWithCache(embPath, cachePath, hskDict, maxHSKLevel)
			if err != nil {
				log.Printf("Warning: Failed to load embeddings: %v", err)
				log.Println("Continuing without embeddings (simplified mode)")
				embeddings = nil
				vectorSize = 0
			} else {
				log.Printf("Embeddings loaded: %d words (vector size: %d)", len(embeddings), vectorSize)
			}
		} else {
			log.Println("Skipping embeddings (no-embeddings flag)")
			embeddings = nil
			vectorSize = 0
		}
	})
}

// getDataDir определяет директорию с данными
func getDataDir() string {
	// 1. Проверяем переменную окружения
	if dir := os.Getenv("DATA_DIR"); dir != "" {
		return dir
	}

	// 2. Проверяем относительно исполняемого файла
	execPath, err := os.Executable()
	if err == nil {
		dir := filepath.Join(filepath.Dir(execPath), "data")
		if _, err := os.Stat(filepath.Join(dir, "hsk.json")); err == nil {
			return dir
		}
	}

	// 3. Проверяем относительно рабочей директории
	if _, err := os.Stat("data/hsk.json"); err == nil {
		return "data"
	}

	// 4. Проверяем относительно golern-go
	if _, err := os.Stat("golern-go/data/hsk.json"); err == nil {
		return "golern-go/data"
	}

	return "data"
}

// ==================== HTTP Handlers ====================

func main() {
	// Парсим флаги
	validate := flag.Bool("validate", false, "Validate embeddings file and exit")
	preload := flag.Bool("preload", false, "Preload and cache embeddings")
	flag.BoolVar(&noEmbeddings, "no-embeddings", false, "Don't load embeddings (faster startup)")
	flag.IntVar(&maxHSKLevel, "max-hsk", 4, "Max HSK level for embeddings (1-6)")
	flag.Parse()

	// Валидация файла
	if *validate {
		dataDir := getDataDir()
		embPath := filepath.Join(dataDir, "light_Tencent_AILab_ChineseEmbedding.bin")
		log.Printf("Validating: %s", embPath)
		if err := ValidateEmbeddingsFileCmd(embPath); err != nil {
			log.Fatalf("Validation failed: %v", err)
		}
		log.Println("Validation successful!")
		return
	}

	// Предзагрузка кэша
	if *preload {
		dataDir := getDataDir()
		cacheDir := filepath.Join(dataDir, "cache")
		cachePath := filepath.Join(cacheDir, "embeddings_hsk"+strconv.Itoa(maxHSKLevel)+".gob")
		
		// Загружаем HSK
		log.Println("Loading HSK dictionary...")
		hskDict, _, err := LoadHSK(dataDir)
		if err != nil {
			log.Fatalf("Failed to load HSK: %v", err)
		}
		log.Printf("HSK loaded: %d entries", len(hskDict))

		// Загружаем эмбеддинги
		embPath := filepath.Join(dataDir, "light_Tencent_AILab_ChineseEmbedding.bin")
		log.Printf("Preloading embeddings (max HSK %d)...", maxHSKLevel)
		embeddings, vectorSize, err := LoadEmbeddingsWithCache(embPath, cachePath, hskDict, maxHSKLevel)
		if err != nil {
			log.Fatalf("Failed to load embeddings: %v", err)
		}
		log.Printf("Preloaded %d embeddings (vector size: %d)", len(embeddings), vectorSize)
		log.Printf("Cache saved to: %s", cachePath)
		return
	}

	// Инициализируем данные
	initData()

	port := os.Getenv("PORT")
	if port == "" {
		port = ":8080"
	}

	log.Printf("Go Simplifier Service starting on port %s", port)
	
	// Создаём mux для регистрации handlers
	mux := http.NewServeMux()
	mux.HandleFunc("/health", healthHandler)
	mux.HandleFunc("/analyze", analyzeHandler)
	mux.HandleFunc("/simplify", simplifyHandler)
	mux.HandleFunc("/word/info", wordInfoHandler)
	mux.HandleFunc("/word/similar", wordSimilarHandler)
	
	log.Fatal(http.ListenAndServe(port, corsMiddleware(mux)))
}

// corsMiddleware добавляет CORS заголовки
func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"status":"ok"}`))
}

func analyzeHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	if r.Method == http.MethodOptions {
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

func simplifyHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	if r.Method == http.MethodOptions {
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

	var req SimplifyRequest
	if err := json.Unmarshal(body, &req); err != nil {
		http.Error(w, `{"error":"Invalid JSON"}`, http.StatusBadRequest)
		return
	}

	// Проверяем инициализацию
	if hskDict == nil {
		http.Error(w, `{"error":"HSK dictionary not loaded"}`, http.StatusInternalServerError)
		return
	}

	// Упрощаем текст
	result := simplifyTextWithDict(req.Text, req.TargetLevel)

	response := SimplifyResponse{
		Status:         "ok",
		OriginalText:   result.OriginalText,
		SimplifiedText: result.SimplifiedText,
		Replacements:   result.Replacements,
		TargetLevel:    result.TargetLevel,
		TotalTokens:    result.TotalTokens,
		ReplacedCount:  result.ReplacedCount,
	}

	if err := json.NewEncoder(w).Encode(response); err != nil {
		http.Error(w, `{"error":"Failed to encode response"}`, http.StatusInternalServerError)
		return
	}
}

func wordInfoHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusOK)
		return
	}

	if r.Method != http.MethodGet {
		http.Error(w, `{"error":"Method not allowed"}`, http.StatusMethodNotAllowed)
		return
	}

	word := r.URL.Query().Get("word")
	if word == "" {
		http.Error(w, `{"error":"Missing 'word' parameter"}`, http.StatusBadRequest)
		return
	}

	if hskDict == nil {
		http.Error(w, `{"error":"HSK dictionary not loaded"}`, http.StatusInternalServerError)
		return
	}

	info := getWordInfo(word)
	json.NewEncoder(w).Encode(info)
}

func wordSimilarHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusOK)
		return
	}

	if r.Method != http.MethodGet {
		http.Error(w, `{"error":"Method not allowed"}`, http.StatusMethodNotAllowed)
		return
	}

	word := r.URL.Query().Get("word")
	maxLevel := r.URL.Query().Get("max_level")
	topK := r.URL.Query().Get("top_k")

	if word == "" {
		http.Error(w, `{"error":"Missing 'word' parameter"}`, http.StatusBadRequest)
		return
	}

	if embeddings == nil {
		http.Error(w, `{"error":"Embeddings not loaded"}`, http.StatusServiceUnavailable)
		return
	}

	level := maxHSKLevel
	if maxLevel != "" {
		if _, err := strconv.Atoi(maxLevel); err == nil {
			level, _ = strconv.Atoi(maxLevel)
		}
	}

	k := 10
	if topK != "" {
		if _, err := strconv.Atoi(topK); err == nil {
			k, _ = strconv.Atoi(topK)
		}
	}

	similar := FindSimplerWords(word, level, k)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"word":      word,
		"similar":   similar,
		"max_level": level,
	})
}

// ==================== Упрощение текста ====================

// SimplifyResult результат упрощения
type SimplifyResult struct {
	OriginalText   string
	SimplifiedText string
	Replacements   []WordReplacement
	TargetLevel    int
	TotalTokens    int
	ReplacedCount  int
}

// simplifyTextWithDict упрощает текст используя HSK словарь и эмбеддинги
func simplifyTextWithDict(text string, targetLevel int) *SimplifyResult {
	var tokens []string
	var replacements []WordReplacement

	// Токенизация китайского текста
	runes := []rune(text)
	i := 0

	log.Printf("Simplifying text: %s (target level: %d)", text, targetLevel)

	for i < len(runes) {
		if unicode.IsSpace(runes[i]) || (runes[i] <= 127 && unicode.IsPunct(runes[i])) {
			i++
			continue
		}

		// Пытаемся найти слово в словаре (максимальное совпадение)
		found := false
		maxLen := len(runes) - i
		if maxLen > 6 {
			maxLen = 6
		}
		for length := maxLen; length >= 1; length-- {
			word := string(runes[i : i+length])
			if level, ok := hskDict[word]; ok {
				tokens = append(tokens, word)

				// Если слово сложнее целевого уровня
				if level > targetLevel {
					// Пытаемся найти замену через эмбеддинги
					replacement := ""
					similarity := float32(0)

					if embeddings != nil {
						replacement, similarity = FindSimplerWord(word, targetLevel)
					}

					if replacement != "" && similarity >= 0.55 {
						// Нашли замену
						replacements = append(replacements, WordReplacement{
							Original:    word,
							Replacement: replacement,
							Reason:      "HSK level too high",
							HSKLevel:    level,
							Similarity:  similarity,
						})
						tokens[len(tokens)-1] = replacement
					} else {
						// Не нашли замену, помечаем
						replacements = append(replacements, WordReplacement{
							Original:    word,
							Replacement: "[COMPLEX:" + strconv.Itoa(level) + "]",
							Reason:      "HSK level too high, no similar word found",
							HSKLevel:    level,
							Similarity:  0,
						})
					}
				}

				i += length
				found = true
				break
			}
		}

		if !found {
			tokens = append(tokens, string(runes[i]))
			i++
		}
	}

	return &SimplifyResult{
		OriginalText:   text,
		SimplifiedText: strings.Join(tokens, ""),
		Replacements:   replacements,
		TargetLevel:    targetLevel,
		TotalTokens:    len(tokens),
		ReplacedCount:  len(replacements),
	}
}

// ==================== Анализ текста ====================

func analyzeText(text string, lang string, userLevel int) AnalyzeResponse {
	var rawTokens []string

	if strings.HasPrefix(strings.ToLower(lang), "zh") {
		rawTokens = tokenizeChineseSimple(text)
	} else {
		rawTokens = tokenizeEuropean(text)
	}

	freqMap := make(map[string]int)
	posMap := make(map[string][]int)

	for i, token := range rawTokens {
		freqMap[token]++
		posMap[token] = append(posMap[token], i)
	}

	tokens := make([]Token, 0, len(freqMap))
	for value, frequency := range freqMap {
		token := Token{
			Value:     value,
			Lemma:     getLemma(value, lang),
			Frequency: frequency,
			Positions: posMap[value],
			HSK:       getHSKLevel(value),
			IsKnown:   isKnownWord(value, userLevel),
		}
		tokens = append(tokens, token)
	}

	return AnalyzeResponse{
		Status:      "ok",
		TokensCount: len(rawTokens),
		Tokens:      tokens,
	}
}

func tokenizeChineseSimple(text string) []string {
	var tokens []string
	for _, r := range text {
		if unicode.IsSpace(r) {
			continue
		}
		if r <= 127 && (unicode.IsPunct(r) || unicode.IsSymbol(r)) {
			continue
		}
		tokens = append(tokens, string(r))
	}
	return tokens
}

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

func getLemma(token string, lang string) string {
	if strings.HasPrefix(strings.ToLower(lang), "zh") {
		return token
	}

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

func getHSKLevel(word string) int {
	if hskDict == nil {
		return 0
	}
	if level, ok := hskDict[word]; ok {
		return level
	}
	return 0
}

func isKnownWord(word string, userLevel int) bool {
	hskLevel := getHSKLevel(word)
	return hskLevel > 0 && hskLevel <= userLevel
}

func getWordInfo(word string) map[string]interface{} {
	info := make(map[string]interface{})
	info["word"] = word

	if hskDict != nil {
		if level, ok := hskDict[word]; ok {
			info["hsk_level"] = level
		} else {
			info["hsk_level"] = 0
		}
	}

	if embeddings != nil {
		info["has_embedding"] = embeddings[word] != nil
	}

	// Добавляем информацию из HSK entries
	for _, entry := range hskEntries {
		if entry.Hanzi == word {
			info["pinyin"] = entry.Pinyin
			info["translations"] = entry.Translations
			info["strokes"] = entry.Strokes
			break
		}
	}

	return info
}

// ==================== Семантический поиск ====================

// WordSimilarity представляет слово и его сходство
type WordSimilarity struct {
	Word       string  `json:"word"`
	Similarity float32 `json:"similarity"`
	HSKLevel   int     `json:"hsk_level"`
}

// CosineSimilarity вычисляет косинусное сходство между двумя векторами
func CosineSimilarity(vec1, vec2 []float32) float32 {
	if len(vec1) != len(vec2) || len(vec1) == 0 {
		return 0.0
	}

	var dotProduct float32
	var norm1 float32
	var norm2 float32

	for i := range vec1 {
		dotProduct += vec1[i] * vec2[i]
		norm1 += vec1[i] * vec1[i]
		norm2 += vec2[i] * vec2[i]
	}

	if norm1 == 0 || norm2 == 0 {
		return 0.0
	}

	return dotProduct / (float32(math.Sqrt(float64(norm1))) * float32(math.Sqrt(float64(norm2))))
}

// FindSimplerWord находит более простое слово с максимальным семантическим сходством
func FindSimplerWord(word string, maxLevel int) (string, float32) {
	if embeddings == nil {
		return "", 0.0
	}

	targetEmbedding := embeddings[word]
	if targetEmbedding == nil {
		return "", 0.0
	}

	wordLevel := getHSKLevel(word)
	if wordLevel == 0 || wordLevel <= maxLevel {
		return "", 0.0
	}

	var bestWord string
	var bestSimilarity float32 = 0.0

	for candidate, embedding := range embeddings {
		candidateLevel := getHSKLevel(candidate)

		// Пропускаем слова без HSK или слишком сложные
		if candidateLevel == 0 || candidateLevel > maxLevel {
			continue
		}

		sim := CosineSimilarity(targetEmbedding, embedding)
		if sim > bestSimilarity && sim >= 0.55 {
			bestSimilarity = sim
			bestWord = candidate
		}
	}

	return bestWord, bestSimilarity
}

// FindSimplerWords возвращает несколько вариантов замены для слова
func FindSimplerWords(word string, maxLevel int, topK int) []WordSimilarity {
	if embeddings == nil {
		return nil
	}

	targetEmbedding := embeddings[word]
	if targetEmbedding == nil {
		return nil
	}

	var simplerWords []WordSimilarity

	for candidate, embedding := range embeddings {
		candidateLevel := getHSKLevel(candidate)

		// Пропускаем слова без HSK или слишком сложные
		if candidateLevel == 0 || candidateLevel > maxLevel {
			continue
		}

		sim := CosineSimilarity(targetEmbedding, embedding)
		if sim >= 0.5 {
			simplerWords = append(simplerWords, WordSimilarity{
				Word:       candidate,
				Similarity: sim,
				HSKLevel:   candidateLevel,
			})
		}
	}

	// Сортируем по убыванию сходства
	sort.Slice(simplerWords, func(i, j int) bool {
		return simplerWords[i].Similarity > simplerWords[j].Similarity
	})

	// Возвращаем top K
	if len(simplerWords) > topK {
		return simplerWords[:topK]
	}
	return simplerWords
}
