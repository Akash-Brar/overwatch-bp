from bs4 import BeautifulSoup
import requests
import json
import re

def dumpToJSON(data, filename):
    with open(filename, 'w') as jsonFile:
        json.dump(data, jsonFile, indent=4)

def openJSON(filename):
    with open(filename, 'r') as jsonFile:
        data = json.load(jsonFile)
    return data

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

def getNewSeason(seasonText):
    season = re.findall(r'\d+', seasonText)
    if season:
        return int(season[0])
    return None

def addItemsToHeroData(heroData, items, season, freeOrPaid):
    for item in items:
        hero = item["hero"]
        
        if hero not in heroData:
            heroData[hero] = {}
        
        season_key = f"BP{season}"
        if season_key not in heroData[hero]:
            heroData[hero][season_key] = {"free": [], "paid": []}

        existing_items = heroData[hero][season_key][freeOrPaid]
        item_exists = False
        
        for existing_item in existing_items:

            if (existing_item['name'] == item['name'] and 
                existing_item['type'] == item['type']):
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
        if itemText and checkIfInt(itemText) == False:
            heroName = getHeroName(link['href'])
            if heroName:
                itemName, itemType = getItemDetails(itemText, heroName)
                item.append({
                    'hero': heroName,
                    'name': itemName,
                    'type': itemType
                })
    return item

def getTotalItems(heroData):
    for hero in heroData:
        totalItems = 0
        for key in heroData[hero]:
            if key.startswith("BP"):
                totalItems += len(heroData[hero][key]['free']) + len(heroData[hero][key]['paid'])
        heroData[hero]['totalItems'] = totalItems
    return heroData

def getItemCountByType(heroData):
    itemTypes = getAllItemTypes(heroData)
    for itemType in itemTypes:
        for hero in heroData:
            typeCount = 0
            for key in heroData[hero]:
                if key.startswith("BP"):
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
            if key.startswith("BP"):
                for item in heroData[hero][key]['free']:
                    itemTypes.add(item['type'])
                for item in heroData[hero][key]['paid']:
                    itemTypes.add(item['type'])
    return list(itemTypes)

def scrapeHTML(url, tagType, identifierType, identifierName):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    bpTablesHTML = soup.find_all(tagType, attrs={identifierType: identifierName})
    return bpTablesHTML

def parseOldBPTable(tableHTML, heroData):
    season = 1
    for table in tableHTML:
        rows = table.find_all('tr')[2:]
        for row in rows:
            cells = row.find_all('td')[1:]
            if len(cells) == 2:
                freeItems = getItemInCell(cells[0])
                paidItems = getItemInCell(cells[1])

                heroData = addItemsToHeroData(heroData, freeItems, season, "free")
                heroData = addItemsToHeroData(heroData, paidItems, season, "paid")

        season += 1
    return heroData
    
def parseHerosTable(tableHTML):
    herosData = {}
    table = tableHTML[0]
    rows = table.find_all('tr')[1:]
    for row in rows:
        cells = row.find_all('td')
        heroImg = cells[1].find('img')['data-src']
        heroName = cells[2].text.strip()
        heroRoleUnparsed = cells[3].text.strip()
        heroRole = getRole(heroRoleUnparsed)
        herosData[heroName] = {
            'img': heroImg,
            'role': heroRole
        }
    return herosData

def parseNewBPTable(tableHTML, heroData):
    table = tableHTML[0]
    header = table.find_all('tr')[0]
    season = getNewSeason(header.text)
    rows = table.find_all('tr')[2:]

    for row in rows:
        cells = row.find_all('td')[1:]
        if len(cells) == 2:
            freeItems = getItemInCell(cells[0])
            paidItems = getItemInCell(cells[1])

            heroData = addItemsToHeroData(heroData, freeItems, season, "free")
            heroData = addItemsToHeroData(heroData, paidItems, season, "paid")
    return heroData

if __name__ == "__main__":
    oldBPUrl = "https://overwatch.fandom.com/wiki/List_of_previous_Battle_Passes"
    herosUrl = "https://overwatch.fandom.com/wiki/Heroes"

    herosTableHTML = scrapeHTML(herosUrl, "table", "class", "listtable")
    herosData = parseHerosTable(herosTableHTML)

    bpTablesHTML = scrapeHTML(oldBPUrl, "table", "class", "fandom-table")
    heroData = parseOldBPTable(bpTablesHTML, herosData)


    newBPUrl = "https://overwatch.fandom.com/wiki/Battle_Pass"

    bpTableHTML = scrapeHTML(newBPUrl, 'table', 'class', 'fandom-table')
    heroData = parseNewBPTable(bpTableHTML, heroData)

    heroData = getTotalItems(heroData)
    heroData = getItemCountByType(heroData)

    dumpToJSON(heroData, "bpData.json")
