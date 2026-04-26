# Plan pracy inżynierskiej
## Igor Czarnogłowski, s223275

---

## 1. Zdefiniowanie celów
- **Cel:** Ocena jakości LLM przy klasyfikowania przydatności wiadomości dotyczących spółek działających na giełdzie WIG (konkretnie spółki w indeksie WIG20)
- **Typ problemu:** klasyfikacja / NLP
- **Limity:** Jakość danych

## 2. Zbieranie danych
- **Źródła:** PapBiznes, Bankier, Wykop, 
- **Metoda:** Scrapowanie
- **Przewidywana wielkość:** ok. 500 rekordów tygodniowo
- **Co ile zbierane dane:** Co tydzień

## 3. Plan działania
- [ ] Pobranie danych
- [ ] EDA
- [ ] Analiza danych
- [ ] Przygotowanie danych
- [ ] Sklasyfikowanie wiadomości przez LLM
- [ ] Feature Engineering (potencjalnie)
- [ ] Modelowanie
- [ ] Ewaulacja modeli
- [ ] Wizualizacja

## 4. Przewidywane technologie
- [ ] Python 3.12
- [ ] Ollama

## 5. Przewidywane LLM
- **HuggingFace**
- [ ] Financial-RoBERTa https://huggingface.co/soleimanian/financial-roberta-large-sentiment
- [ ] finbert https://huggingface.co/ProsusAI/finbert
- [ ] financial-lora https://huggingface.co/cg1026/financial-news-sentiment-lora
- **Klasyczne LLM**
- [ ] Qwen2.5:7b
- [ ] Mistral:7b  
- [ ] DeepSeek-R1:7b 
- [ ] gpt-oss-20b

## 6. Proponowany pipeline

| Zadanie | Model |
|---|---|
| Klasyfikacja spółki | `finance-llama-8b` lub `qwen2.5:7b` |
| Ocena wpływu wiadomości (1-10) | `deepseek-r1:7b` (reasoning) lub `qwen2.5:7b` |
| Priorytet szybkości | `mistral:7b` |


## 7. Proponowane metryki ewaluacji

| Metryka | Zastosowanie | Cel |
|---|---|---|
| **Abnormal Returns / CAR** (CAPM / ARIMA) | Ocena wpływu wiadomości | Porównanie rzeczywistego zwrotu z oczekiwanym benchmarkowym |
| **Spearman Correlation** | Ocena trafności ratingu (1-10) | Sprawdzenie czy skala LLM koreluje z rzeczywistą zmianą ceny |
| **Directional Accuracy** | Ocena trafności ratingu | % przypadków, gdy wysoki rating poprawnie przewidział kierunek ruchu ceny |
| **Hit Rate** | Ocena trafności ratingu | % wiadomości z ratingiem ≥7, które wywołały istotną zmianę ceny |
| **Information Coefficient (IC)** | Siła sygnału | Standardowa miara predykcyjności sygnału w finansach ilościowych |
| **F1 / Accuracy** | Klasyfikacja spółki | Ocena poprawności przypisania wiadomości do spółki |
| **Backtest Sharpe Ratio** | Strategia oparta na ratingach | Ryzyko-zwrot symulowanej strategii inwestycyjnej |
| **Transfer Entropy** | Przepływ informacji | Czy ratingi LLM niosą informację o przyszłych zmianach cen |
| **Cox Proportional Hazards** | Analiza przeżycia informacji | Czas do wystąpienia istotnej reakcji ceny po publikacji wiadomości |
