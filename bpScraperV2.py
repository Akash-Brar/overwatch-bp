from bs4 import BeautifulSoup
import requests
import json

ITEM_TYPES_URL = "https://overwatch.weirdgloop.org/w/Cosmetics"
PRE_2026_BP_URL = "https://overwatch.weirdgloop.org/w/List_of_previous_Battle_Passes/2022-2026"
POST_2026_BP_URL = "https://overwatch.weirdgloop.org/w/List_of_previous_Battle_Passes/2026"

def get_item_types():
    response = requests.get(ITEM_TYPES_URL)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch item types. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")
    item_type_list = soup.find("div", id="content").find("div", id="bodyContent").find("div", id="mw-content-text").find("div", class_="mw-content-ltr").find_all("ul")[1]

    item_types = []
    for li in item_type_list.find_all("li"):
        a_tag = li.find("a")
        if a_tag and a_tag.has_attr("title"):
            if a_tag["title"] not in ["Player Titles", "Souvenirs", "Weapon Charms", "Weapon Variants"]:
                item_types.append(a_tag["title"])

    return item_types

if __name__ == "__main__":
    item_types = get_item_types()
    print(item_types)