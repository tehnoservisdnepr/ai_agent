from ai_engine import analyze_news  # или как там называется функция в ai_engine.py

test_text = "Вышел новый драйвер для JK BMS под Linux и интеграция с Home Assistant"
print("Запрос к Джарвису...")
result = analyze_news(test_text)
print(f"Вердикт: {result}")