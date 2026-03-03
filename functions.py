import json
import re
import requests
from PyQt5.QtGui import QPixmap


def message_parser(ingameName: str, quantity: int, name: str, price: int) -> str:
    return f"/w {ingameName} Hi! I want to buy: {quantity} '{name}' for {price} platinum each. (warframe.market)"


# функция для преобразования текста (приведёт к нижнему регистру, основные части сетов приведёт к переводимым

def normalize(text: str) -> str:
    SYNONYMS = {
        "сет": "набор",
        "комплект": "набор",
        "bp": "blueprint",
        "чертеж": "чертёж"
    }
    text = text.lower()

# замена частей

    for k, v in SYNONYMS.items():
        text = text.replace(k, v)

    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# для создания словаря, который позволяет корректировать другие языки
# ВАЖНО ИНИЦИИРОВАТЬ КАЖДЫЙ РАЗ ПРИ ЗАПУСКЕ

def build_slug_dict():
    headers = {
        "Language": "ru"
    }

    r = requests.get("https://api.warframe.market/v2/items", headers=headers)
    data = r.json()["data"]
    slug_dict = {}
    for item in data:
        slug = item["slug"]

        for lang in item["i18n"]:
            name = item["i18n"][lang]["name"]
            slug_dict[normalize(name)] = slug

    return slug_dict

# каждый раз при запуске
ITEMS_DICT = build_slug_dict()

# через фнкц приводит текст к понимаемому запросами, после в словаре ищет соответствие и проводит замену
def warframe_to_url(text: str) -> str:
    text = normalize(text)

    if text in ITEMS_DICT:
        return ITEMS_DICT[text]

    for name, slug in ITEMS_DICT.items():
        if text in name:
            return slug
        elif text in slug:
            return slug

    return None

def get_api_icon(name: str):
    url_name = warframe_to_url(name)

    icon_url = requests.get(f"https://api.warframe.market/v2/items/{url_name}")
    icon_json = icon_url.json()
    # print(icon_json)

    # icon_path = icon_json['data']['i18n']['en']['thumb']
    # if not icon_path:
    #     return None

    data = icon_json.get('data')
    if not data:
        return None

    i18n = data.get('i18n', {}).get('en')
    if not i18n:
        return None

    icon_path = i18n.get('thumb') or i18n.get('icon')
    if not icon_path:
        return None

    return "https://warframe.market/static/assets/" + icon_path.lstrip("/")


def download_icon_bytes(url: str):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except:
        return None

def bytes_to_image(bytes: bytes):
    pixmap = QPixmap()
    pixmap.loadFromData(bytes)
    return pixmap




# основная функция обработки, по частям принимает запрос, после делает вывод самого лучшего трейда
def collect_data_parts(name: str, type: str, platform: str, quantity: int = 1, want_platinum: int = 1, crossplay=True):
    url_name = warframe_to_url(name)

    if not url_name:
        print("Предмет не найден")
        return

    result = []
    r = requests.get(f"https://api.warframe.market/v2/orders/item/{url_name}/top")
    r_json = r.json()

    print(r_json)

    orders = r_json["data"][type]

    if not orders:
        # print("Нет закаZOV")
        return []

    for item in orders:
        if item["user"]["status"] == "offline":
            continue

        if crossplay != item["user"]["crossplay"]:
            if item["user"]["platform"] != platform:
                continue
        if item["user"]["status"] != "ingame":
            continue
        if item["quantity"] < quantity:
            continue
        result_item = {
            "ingameName": item["user"]["ingameName"],
            "name": url_name,
            "type": type,
            "quantity": item["quantity"],
            "price": item["platinum"],
            # "status": best_order["user"]["status"],
            "date": item["updatedAt"]
        }
        result.append(result_item)
    return result



# print(collect_data_parts("Атлас прайм сет", "sell", "pc", 1, 70))
