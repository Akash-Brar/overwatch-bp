from bs4 import BeautifulSoup
import requests
import json
import re
import time
import os

INCLUDE_PREVIOUS_BATTLE_PASSES = False


def loadJSON(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as jsonFile:
                return json.load(jsonFile)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}


def dumpToJSON(data, filename):
    with open(filename, "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)


def merge_bp_data(existing_data, new_data):
    for hero, hero_info in new_data.items():
        if hero not in existing_data:
            existing_data[hero] = hero_info
            continue

        for key, value in hero_info.items():
            # Merge season entries
            if isinstance(value, dict) and "free" in value and "paid" in value:
                if key not in existing_data[hero]:
                    existing_data[hero][key] = {"free": [], "paid": []}

                for item in value["free"]:
                    if item not in existing_data[hero][key]["free"]:
                        existing_data[hero][key]["free"].append(item)

                for item in value["paid"]:
                    if item not in existing_data[hero][key]["paid"]:
                        existing_data[hero][key]["paid"].append(item)
            else:
                # Only add non-season fields if missing
                if key not in existing_data[hero]:
                    existing_data[hero][key] = value

    return existing_data


def checkIfInt(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def getRole(role):
    if 'Tank' in role:
        return 'Tank'
    elif 'Damage' in role:
        return 'Damage'
    elif 'Support' in role:
        return 'Support'
    return role


def getHeroName(hrefLink):
    if ("/wiki/" in hrefLink) and ("/Cosmetics" in hrefLink):
        hrefSplit = hrefLink.split("/")
        if len(hrefSplit) < 4:
            return None
        heroName = hrefSplit[2]
        heroName = heroName.replace("_", " ")
        heroName = requests.utils.unquote(heroName)
        return heroName
    return None


def normalize_season_name(season_name, page_title=None):
    overrides = {
        ("Battle_Pass", "Season 20"): "2026 Season 1",
    }
    return overrides.get((page_title, season_name), season_name)


def getSeasonName(headerText, page_title=None, fallback=None):
    text = " ".join(headerText.split())

    year_season_match = re.search(r'((?:20\d{2}).*?Season\s+\d+)', text, re.IGNORECASE)
    if year_season_match:
        season_name = year_season_match.group(1).strip()
        return normalize_season_name(season_name, page_title)

    season_match = re.search(r'(Season\s+\d+)', text, re.IGNORECASE)
    if season_match:
        season_name = season_match.group(1).strip()
        season_name = season_name[0].upper() + season_name[1:]
        return normalize_season_name(season_name, page_title)

    if fallback:
        return normalize_season_name(fallback, page_title)

    return normalize_season_name(text, page_title)


def addItemsToHeroData(heroData, items, season_key, freeOrPaid):
    for item in items:
        hero = item["hero"]

        if hero not in heroData:
            heroData[hero] = {}

        if season_key not in heroData[hero]:
            heroData[hero][season_key] = {"free": [], "paid": []}

        existing_items = heroData[hero][season_key][freeOrPaid]
        item_exists = False

        for existing_item in existing_items:
            if (
                existing_item['name'] == item['name'] and
                existing_item['type'] == item['type']
            ):
                item_exists = True
                break

        if not item_exists:
            heroData[hero][season_key][freeOrPaid].append({
                'name': item['name'],
                'type': item['type']
            })

    return heroData


def getItemDetails(itemText, heroName):
    itemInfo = itemText.split(" - ")
    itemName = itemInfo[0].strip()
    itemType = itemInfo[1].replace(heroName, "").strip()
    return itemName, itemType


def getItemInCell(itemCell):
    item = []
    itemLinks = itemCell.find_all('a')
    for link in itemLinks:
        itemText = link.text.strip()
        if itemText and not checkIfInt(itemText):
            heroName = getHeroName(link['href'])
            if heroName:
                itemName, itemType = getItemDetails(itemText, heroName)
                item.append({
                    'hero': heroName,
                    'name': itemName,
                    'type': itemType
                })
    return item


def clearTotals(heroData):
    for hero in heroData:
        keys_to_remove = []
        for key in heroData[hero]:
            if key == "totalItems" or key.startswith("total_"):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del heroData[hero][key]

    return heroData


def getTotalItems(heroData):
    for hero in heroData:
        totalItems = 0
        for key in heroData[hero]:
            if (
                isinstance(heroData[hero][key], dict)
                and 'free' in heroData[hero][key]
                and 'paid' in heroData[hero][key]
            ):
                totalItems += len(heroData[hero][key]['free']) + len(heroData[hero][key]['paid'])
        heroData[hero]['totalItems'] = totalItems
    return heroData


def getItemCountByType(heroData):
    itemTypes = getAllItemTypes(heroData)
    for itemType in itemTypes:
        for hero in heroData:
            typeCount = 0
            for key in heroData[hero]:
                if (
                    isinstance(heroData[hero][key], dict)
                    and 'free' in heroData[hero][key]
                    and 'paid' in heroData[hero][key]
                ):
                    for item in heroData[hero][key]['free']:
                        if item['type'] == itemType:
                            typeCount += 1
                    for item in heroData[hero][key]['paid']:
                        if item['type'] == itemType:
                            typeCount += 1
            heroData[hero][f'total_{itemType}'] = typeCount
    return heroData


def getAllItemTypes(heroData):
    itemTypes = set()
    for hero in heroData:
        for key in heroData[hero]:
            if (
                isinstance(heroData[hero][key], dict)
                and 'free' in heroData[hero][key]
                and 'paid' in heroData[hero][key]
            ):
                for item in heroData[hero][key]['free']:
                    itemTypes.add(item['type'])
                for item in heroData[hero][key]['paid']:
                    itemTypes.add(item['type'])
    return list(itemTypes)


def get_wiki_page_html(page_title):
    """Fetch page HTML using Fandom API"""
    api_url = "https://overwatch.fandom.com/api.php"

    params = {
        'action': 'parse',
        'format': 'json',
        'page': page_title,
        'prop': 'text',
        'formatversion': 2
    }

    headers = {
        'User-Agent': 'OverwatchBPDataCollector/1.0 (https://github.com/yourusername/overwatch-bp-scraper)',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        if 'parse' in data and 'text' in data['parse']:
            return data['parse']['text']
        else:
            print(f"Could not get content for {page_title}")
            return None
    except Exception as e:
        print(f"API Error for {page_title}: {e}")
        return None


def parse_battle_pass_tables(html_content, hero_data, page_title, is_old_bp=False):
    """Parse battle pass tables from HTML content"""
    if not html_content:
        return hero_data

    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table', class_='fandom-table')

    if not tables:
        print("No tables found in HTML")
        return hero_data

    for index, table in enumerate(tables, start=1):
        rows = table.find_all('tr')
        if not rows:
            continue

        header_text = rows[0].get_text(" ", strip=True)
        season_key = getSeasonName(header_text, page_title=page_title, fallback=f"Season Table {index}")

        data_rows = rows[2:]
        for row in data_rows:
            cells = row.find_all('td')[1:]
            if len(cells) == 2:
                free_items = getItemInCell(cells[0])
                paid_items = getItemInCell(cells[1])

                hero_data = addItemsToHeroData(hero_data, free_items, season_key, "free")
                hero_data = addItemsToHeroData(hero_data, paid_items, season_key, "paid")

        if is_old_bp:
            time.sleep(0.1)

    return hero_data


def fetch_heroes_from_api():
    """Fetch hero data from OverFast API"""
    url = "https://overfast-api.tekrop.fr/heroes"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        heroes_data = response.json()

        heroes = {}
        for hero in heroes_data:
            role = hero['role']
            if role == 'damage':
                role = 'Damage'
            elif role == 'tank':
                role = 'Tank'
            elif role == 'support':
                role = 'Support'

            heroes[hero['name']] = {
                'img': hero['portrait'],
                'role': role
            }
        return heroes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching heroes from API: {e}")
        return {}


if __name__ == "__main__":
    output_file = "bpData.json"

    print("Fetching hero data from OverFast API...")
    hero_data = fetch_heroes_from_api()
    print(f"Found {len(hero_data)} heroes")

    if INCLUDE_PREVIOUS_BATTLE_PASSES:
        print("\nFetching previous battle passes from Fandom API...")
        prev_bp_html = get_wiki_page_html("List_of_previous_Battle_Passes/2022-2026")

        if prev_bp_html:
            hero_data = parse_battle_pass_tables(
                prev_bp_html,
                hero_data,
                page_title="List_of_previous_Battle_Passes/2022-2026",
                is_old_bp=True
            )
            print("Successfully parsed previous battle passes")
        else:
            print("Failed to fetch previous battle passes")

        time.sleep(1)
    else:
        print("\nSkipping previous battle passes")

    print("\nFetching current battle pass from Fandom API...")
    current_bp_html = get_wiki_page_html("Battle_Pass")

    if current_bp_html:
        hero_data = parse_battle_pass_tables(
            current_bp_html,
            hero_data,
            page_title="Battle_Pass",
            is_old_bp=False
        )
        print("Successfully parsed current battle pass")
    else:
        print("Failed to fetch current battle pass")

    print("\nMerging with existing JSON data...")
    existing_data = loadJSON(output_file)
    hero_data = merge_bp_data(existing_data, hero_data)

    print("\nCalculating totals...")
    hero_data = clearTotals(hero_data)
    hero_data = getTotalItems(hero_data)
    hero_data = getItemCountByType(hero_data)

    dumpToJSON(hero_data, output_file)
    print(f"\nData successfully saved to {output_file}")

    total_items = sum(
        hero_data[hero]['totalItems']
        for hero in hero_data
        if 'totalItems' in hero_data[hero]
    )
    print(f"Total heroes processed: {len(hero_data)}")
    print(f"Total battle pass items collected: {total_items}")