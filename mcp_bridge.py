from flask import Flask, jsonify
from analyze import get_weather_analysis
import asyncio

app = Flask(__name__)

@app.route('/weather', methods=['GET'])
def get_weather():
    # Запускаем ваш парсинг
    data = asyncio.run(get_weather_analysis())
    return jsonify(data)

if __name__ == "__main__":
    app.run(port=5000, host='0.0.0.0')