package main

import (
	"bufio"
	"bytes"
	"encoding/binary"
	"encoding/gob"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// HSKEntry представляет запись из HSK словаря
type HSKEntry struct {
	Hanzi        string              `json:"hanzi"`
	ID           int                 `json:"id"`
	Level        int                 `json:"level"`
	Pinyin       string              `json:"pinyin"`
	Radicals     string              `json:"radicals"`
	Strokes      string              `json:"strokes"`
	Translations map[string][]string `json:"translations"`
}

// EmbeddingCache кэшированные данные эмбеддингов
type EmbeddingCache struct {
	Embeddings map[string][]float32
	VectorSize int
	LoadedAt   time.Time
	HSKFilter  int // Максимальный уровень HSK для фильтрации
}

// LoadEmbeddingsWithCache загружает эмбеддинги с кэшированием
func LoadEmbeddingsWithCache(binPath string, cachePath string, hskDict map[string]int, maxHSKLevel int) (map[string][]float32, int, error) {
	// Проверяем кэш
	if cache, err := loadFromCache(cachePath, maxHSKLevel); err == nil {
		log.Printf("Loaded embeddings from cache: %d words (vector size: %d)", 
			len(cache.Embeddings), cache.VectorSize)
		return cache.Embeddings, cache.VectorSize, nil
	}

	log.Printf("Cache not found or invalid, loading from binary file...")
	
	// Загружаем из бинарного файла
	embeddings, vectorSize, err := LoadEmbeddingsFromBinFiltered(binPath, hskDict, maxHSKLevel)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to load embeddings: %w", err)
	}

	// Сохраняем в кэш
	if err := saveToCache(cachePath, embeddings, vectorSize, maxHSKLevel); err != nil {
		log.Printf("Warning: Failed to save cache: %v", err)
	}

	return embeddings, vectorSize, nil
}

// loadFromCache загружает из gob кэша
func loadFromCache(cachePath string, maxHSKLevel int) (*EmbeddingCache, error) {
	// Проверяем существование файла
	info, err := os.Stat(cachePath)
	if err != nil {
		return nil, err
	}

	// Проверяем возраст кэша (не старше 24 часов)
	if time.Since(info.ModTime()) > 24*time.Hour {
		return nil, fmt.Errorf("cache too old")
	}

	file, err := os.Open(cachePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var cache EmbeddingCache
	decoder := gob.NewDecoder(file)
	if err := decoder.Decode(&cache); err != nil {
		return nil, err
	}

	// Проверяем что кэш для того же уровня HSK
	if cache.HSKFilter != maxHSKLevel {
		return nil, fmt.Errorf("cache HSK filter mismatch")
	}

	return &cache, nil
}

// saveToCache сохраняет в gob кэш
func saveToCache(cachePath string, embeddings map[string][]float32, vectorSize int, maxHSKLevel int) error {
	// Создаём директорию если нет
	dir := filepath.Dir(cachePath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}

	cache := &EmbeddingCache{
		Embeddings: embeddings,
		VectorSize: vectorSize,
		LoadedAt:   time.Now(),
		HSKFilter:  maxHSKLevel,
	}

	file, err := os.Create(cachePath)
	if err != nil {
		return err
	}
	defer file.Close()

	encoder := gob.NewEncoder(file)
	return encoder.Encode(cache)
}

// LoadEmbeddingsFromBinFiltered загружает эмбеддинги с фильтрацией по HSK
func LoadEmbeddingsFromBinFiltered(path string, hskDict map[string]int, maxHSKLevel int) (map[string][]float32, int, error) {
	startTime := time.Now()
	
	f, err := os.Open(path)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to open file: %w", err)
	}
	defer f.Close()

	reader := bufio.NewReader(f)

	// Читаем заголовок
	header, err := reader.ReadString('\n')
	if err != nil {
		return nil, 0, fmt.Errorf("failed to read header: %w", err)
	}

	parts := strings.Fields(header)
	if len(parts) < 2 {
		return nil, 0, fmt.Errorf("invalid header format: %s", header)
	}

	totalWords, err := strconv.Atoi(parts[0])
	if err != nil {
		return nil, 0, fmt.Errorf("invalid word count: %s", parts[0])
	}

	vectorSize, err := strconv.Atoi(parts[1])
	if err != nil {
		return nil, 0, fmt.Errorf("invalid vector size: %s", parts[1])
	}

	log.Printf("Loading embeddings: %d total words, vector size: %d, max HSK: %d", 
		totalWords, vectorSize, maxHSKLevel)

	embeddings := make(map[string][]float32)
	loadedCount := 0
	skippedCount := 0
	byteBuffer := make([]byte, vectorSize*4) // Переиспользуемый буфер

	// Прогресс
	progressInterval := 50000
	lastProgress := 0

	for {
		// Читаем слово
		word, err := readWord(reader)
		if err != nil {
			if err == io.EOF {
				break
			}
			return nil, 0, fmt.Errorf("error reading word: %w", err)
		}

		// Читаем вектор
		vector, err := readVector(reader, byteBuffer, vectorSize)
		if err != nil {
			if err == io.EOF {
				break
			}
			return nil, 0, fmt.Errorf("error reading vector for word '%s': %w", word, err)
		}

		// Фильтрация по HSK
		if hskLevel, ok := hskDict[word]; ok && hskLevel <= maxHSKLevel {
			embeddings[word] = vector
			loadedCount++
		} else {
			skippedCount++
		}

		// Прогресс
		if loadedCount+skippedCount-lastProgress >= progressInterval {
			elapsed := time.Since(startTime)
			rate := float64(loadedCount+skippedCount-lastProgress) / elapsed.Seconds()
			log.Printf("Progress: %d/%d words (%d loaded, %d skipped), rate: %.0f words/sec",
				loadedCount+skippedCount, totalWords, loadedCount, skippedCount, rate)
			lastProgress = loadedCount + skippedCount
		}
	}

	elapsed := time.Since(startTime)
	log.Printf("Loaded %d embeddings in %v (skipped %d, rate: %.0f words/sec)",
		loadedCount, elapsed, skippedCount, float64(loadedCount+skippedCount)/elapsed.Seconds())

	return embeddings, vectorSize, nil
}

// readWord читает слово из бинарного файла
func readWord(reader *bufio.Reader) (string, error) {
	var wordBytes []byte
	
	for {
		b, err := reader.ReadByte()
		if err != nil {
			if len(wordBytes) == 0 {
				return "", io.EOF
			}
			return "", fmt.Errorf("unexpected EOF: %w", err)
		}
		
		// Пробел или newline - конец слова
		if b == 0x20 || b == 0x0A || b == 0x0D {
			break
		}
		
		wordBytes = append(wordBytes, b)
	}
	
	if len(wordBytes) == 0 {
		return "", io.EOF
	}
	
	return string(wordBytes), nil
}

// readVector читает вектор из бинарного файла
func readVector(reader *bufio.Reader, buffer []byte, vectorSize int) ([]float32, error) {
	// Читаем все байты вектора
	_, err := io.ReadFull(reader, buffer)
	if err != nil {
		return nil, err
	}

	vector := make([]float32, vectorSize)
	buf := bytes.NewBuffer(buffer)
	
	for i := 0; i < vectorSize; i++ {
		if err := binary.Read(buf, binary.LittleEndian, &vector[i]); err != nil {
			return nil, err
		}
	}

	return vector, nil
}

// ValidateEmbeddingsFile проверяет целостность файла эмбеддингов
func ValidateEmbeddingsFile(path string) error {
	f, err := os.Open(path)
	if err != nil {
		return err
	}
	defer f.Close()

	// Проверяем размер файла
	info, err := f.Stat()
	if err != nil {
		return err
	}

	log.Printf("Embeddings file size: %.2f MB", float64(info.Size())/1024/1024)

	reader := bufio.NewReader(f)

	// Читаем заголовок
	header, err := reader.ReadString('\n')
	if err != nil {
		return fmt.Errorf("failed to read header: %w", err)
	}

	parts := strings.Fields(header)
	if len(parts) < 2 {
		return fmt.Errorf("invalid header: %s", header)
	}

	vectorSize, err := strconv.Atoi(parts[1])
	if err != nil {
		return fmt.Errorf("invalid vector size: %s", parts[1])
	}

	log.Printf("Header: %d words, vector size: %d", parts[0], vectorSize)

	// Проверяем первые 10 слов
	log.Println("Validating first 10 words...")
	for i := 0; i < 10; i++ {
		word, err := readWord(reader)
		if err != nil {
			return fmt.Errorf("error reading word %d: %w", i, err)
		}

		vector := make([]float32, vectorSize)
		for j := 0; j < vectorSize; j++ {
			if err := binary.Read(reader, binary.LittleEndian, &vector[j]); err != nil {
				return fmt.Errorf("error reading vector for word %d (%s): %w", i, word, err)
			}
		}

		log.Printf("  Word %d: '%s' - vector[0:3] = %.4f, %.4f, %.4f", 
			i, word, vector[0], vector[1], vector[2])
	}

	log.Println("File validation passed!")
	return nil
}

// LoadHSK загружает HSK словарь из JSON файла
func LoadHSK(dataDir string) (map[string]int, []HSKEntry, error) {
	hskPath := filepath.Join(dataDir, "hsk.json")

	data, err := os.ReadFile(hskPath)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to read HSK file: %w", err)
	}

	var entries []HSKEntry
	if err := json.Unmarshal(data, &entries); err != nil {
		return nil, nil, fmt.Errorf("failed to parse HSK JSON: %w", err)
	}

	// Создаём карту слово -> уровень
	hskMap := make(map[string]int, len(entries))
	for _, entry := range entries {
		hskMap[entry.Hanzi] = entry.Level
	}

	log.Printf("Loaded %d HSK entries", len(entries))
	return hskMap, entries, nil
}

// ValidateEmbeddingsFileCmd запускает валидацию из командной строки
func ValidateEmbeddingsFileCmd(path string) error {
	return ValidateEmbeddingsFile(path)
}
