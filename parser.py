import requests
from bs4 import BeautifulSoup
import json
import os

# URL с тировым листом чемпионов
URL = "https://www.wildriftfire.com/tier-list"

def get_all_tiers():
    """
    Парсит актуальный тир-лист чемпионов с сайта wildriftfire.com.
    Возвращает:
        - patch (str): текущий патч, указанный на сайте
        - champions (list): список словарей с полями name, role, tier
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        )
    }

    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Получаем текущую версию патча
    patch_tag = soup.find("span", class_="patch")
    patch = patch_tag.text.strip() if patch_tag else "Unknown"

    champions = []

    # Находим все блоки с тирами (например, Mid, Jungle и т.д.)
    tier_blocks = soup.find_all("div", class_="wf-tier-list__tiers__block")

    for block in tier_blocks:
        tier_divs = block.find_all("div", class_="tier")
        for tier_div in tier_divs:
            # Определяем название тира (S+, S, A, B, C и т.д.)
            class_names = tier_div.get("class", [])
            tier_name = next(
                (cls.replace("tier", "").upper().replace("PLUS", "+")
                 for cls in class_names
                 if cls.startswith("s") or cls in ["a", "b", "c"]),
                "Unknown"
            )

            # Получаем список чемпионов в этом тире
            champ_tags = tier_div.find_all("a", class_="ico-holder")
            for champ_tag in champ_tags:
                name = champ_tag.find("span").text.strip()
                role_img = champ_tag.find("img", class_="lane")
                role = role_img["alt"] if role_img else "Unknown"

                champions.append({
                    "name": name,
                    "role": role,
                    "tier": tier_name
                })

    return patch, champions


def save_if_changed(champions, filename="champions.json"):
    """
    Сохраняет данные о чемпионах в файл JSON, если они изменились.

    champions (list): данные, полученные с get_all_tiers()
    filename (str): имя файла (по умолчанию champions.json)
    """
    if not champions:
        print("⚠️ Нет данных для сохранения.")
        return

    if os.path.exists(filename):
        with open(filename, "r") as f:
            existing = json.load(f)
            if existing == champions:
                print("✅ champions.json не изменился")
                return

    with open(filename, "w") as f:
        json.dump(champions, f, ensure_ascii=False, indent=2)
        print(f"✅ Сохранено {len(champions)} чемпионов в {filename}")


def fetch_champions():
    """
    Вспомогательная функция для использования в Flask-приложении.
    Возвращает patch и champions.
    """
    patch, champions = get_all_tiers()
    return champions, patch


if __name__ == "__main__":
    # Тестовый запуск: парсим и сохраняем данные
    patch, champions = get_all_tiers()
    print(f"✅ Patch: {patch}")
    print(f"✅ Champions parsed: {len(champions)}")
    save_if_changed(champions)
