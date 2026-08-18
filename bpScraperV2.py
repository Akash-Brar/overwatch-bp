from bs4 import BeautifulSoup
import requests
import re
import json

HEROS_URL = "https://overwatch.weirdgloop.org/w/Heroes"
ITEM_TYPES_URL = "https://overwatch.weirdgloop.org/w/Cosmetics"
PRE_2026_BP_URL = "https://overwatch.weirdgloop.org/w/List_of_previous_Battle_Passes/2022-2026"
POST_2026_BP_URL = "https://overwatch.weirdgloop.org/w/List_of_previous_Battle_Passes/2026"

def get_heros():
    response = requests.get(HEROS_URL)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch heroes. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")
    heros_table = soup.find("table", class_="navbox").find("tbody").find_all("li")

    heros_data = {}
    current_role = None
    current_sub_role = None
    for hero in reversed(heros_table):
        hero_name = hero.text.strip()

        if "[" in hero_name:
            hero_name, role_info = hero_name.split("[", 1)
            match = re.search(r'Sub-Role\s+(\w+)\s+(\w+)', role_info)
            if match:
                current_role = match.group(1)
                current_sub_role = match.group(2)

        heros_data[hero_name] = {
            "role": current_role,
            "sub_role": current_sub_role
        }

    return heros_data

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

def get_2022_to_2026_bp_items(bp_data):
    response = requests.get(PRE_2026_BP_URL)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch 2022-2026 BP items. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")
    bp_tables = soup.find_all("table", class_="wikitable")

    for table in bp_tables:
        table = table.find("tbody")
        season = table.find_all("th")[0].text.strip()
        
  

if __name__ == "__main__":
    # item_types = get_item_types()
    # get_2022_to_2026_bp_items()
    heros = get_heros()
    print(heros)