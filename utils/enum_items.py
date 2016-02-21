from . hash import hashStringToNumber as hashText

# itemData is a list of dicts
# the dicts have at least an 'id' key
def enumItemsFromDicts(itemData):
    items = []
    for data in itemData:
        if "value" not in data: raise Exception("'value' key is missing")
        if "name" not in data: data["name"] = data["value"]
        if "description" not in data: data["description"] = ""
        if "icon" not in data: data["icon"] = "NONE"
        number = hashText(data["id"]) if "id" in data else hashText(data["value"])
        items.append((data["value"], data["name"], data["description"], data["icon"], number))
    if len(items) == 0:
        items = [("NONE", "NONE", "")]
    return items

def enumItemsFromList(itemData):
    items = []
    for element in itemData:
        items.append((element, element, "", "NONE", hashText(element)))
    if len(items) == 0:
        items = [("NONE", "NONE", "")]
    return items
