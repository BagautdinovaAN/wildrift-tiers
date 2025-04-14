from flask import Flask, render_template
import json
import os
from parser import get_all_tiers, save_if_changed

# Инициализация Flask-приложения
app = Flask(__name__)

@app.route("/")
def index():
    """
    Главная страница приложения.
    Загружает список чемпионов и текущий патч.
    Если champions.json отсутствует или пуст — запускается парсинг.
    """
    # Если файл с чемпионами не существует или пуст — парсим заново
    if not os.path.exists("champions.json") or os.stat("champions.json").st_size == 0:
        patch, champions = get_all_tiers()
        save_if_changed(champions)
    else:
        # Загружаем сохранённый список чемпионов
        with open("champions.json", "r") as f:
            champions = json.load(f)
        # Парсим сайт ещё раз только ради получения актуального патча
        patch, _ = get_all_tiers()

    # Преобразуем список чемпионов в JSON для передачи в JavaScript
    champions_json = json.dumps(champions)

    # Рендерим HTML-шаблон с данными
    return render_template(
        "index.html",
        patch=patch,
        champions=champions,
        champions_json=champions_json
    )


if __name__ == "__main__":
    # Запускаем Flask-приложение в режиме отладки
    app.run(debug=True)
