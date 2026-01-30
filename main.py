import requests
import json
import functions

class Program:
    def __init__(self):
        self.resources = {}
        try:
            with open("resources.json", "r", encoding="utf-8") as file:
                self.resources = json.loads(file)
        except FileNotFoundError:
            with open("resources.json", "w", encoding="utf-8") as file:
                request = requests.get("https://api.warframe.market/v2/orders/item/atlas_prime_set")
                file.write(json.dumps(request))
                self.resources = request

    def new_request(self, name, crossplatform, platform):



