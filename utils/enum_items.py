
# the decorated function should return a list of dicts
# the dicts have at least an 'id' key
def enumItemsFromDicts(function):
    """
    the decorated function should return a list of dicts
    the dicts have at least an 'id' key
    """
    def wrapper(self, context):
        items = []
        for data in function(self, context):
            if "id" not in data: raise Exception("'id' key is missing")
            if "name" not in data: data["name"] = data["id"]
            if "description" not in data: data["description"] = ""
            if "icon" not in data: data["icon"] = "NONE"
            if "number" not in data: data["number"] = hashText(data["id"])
            items.append((data["id"], data["name"], data["description"], data["icon"], data["number"]))
        if len(items) == 0:
            items = [("NONE", "NONE", "")]
        print(items)
        return items
    return wrapper

def enumItemsFromList(function):
    def wrapper(self, context):
        items = []
        for element in function(self, context):
            items.append((element, element, "", "NONE", hashText(element)))
        if len(items) == 0:
            items = [("NONE", "NONE", "")]
        return items
    return wrapper

def hashText(text):
    return int(hash(text) % 1e9)
