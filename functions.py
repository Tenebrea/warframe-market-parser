import json

def get_prices(name: str, d: dict, type: str, crossplatform: bool, platform: str) -> list:
    result = []
    for item in d["data"]:
        if item["type"] != type:
            continue
        if item["user"]["status"] == "offline":
            continue
        if item["platform"] != platform:
            continue
        if crossplatform != item["user"]["crossplatform"]:
            continue

        result_item = {
            "name": name,
            "type": type,
            "price": item["platinum"],
            "quantity": item["quantity"],
            "ingameName": item["user"]["ingameName"],
            "date": item["updatedAt"]
        }
        result.append(result_item)
    return result

def message_parser(d: dict, quantity: int) -> str:
    return f"/w {d["ingameName"]} Hi! I want to buy: {quantity} '{d["name"]}' for {d["price"]} platinum each. (warframe.market)"

def filter_by_price(l: list, price: int) -> list:
    result = []
    for item in l:
        if item["price"] >= price:
            continue
        result.append(item)
    return result