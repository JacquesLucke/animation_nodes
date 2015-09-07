
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
            if "value" not in data: raise Exception("'value' key is missing")
            if "name" not in data: data["name"] = data["value"]
            if "description" not in data: data["description"] = ""
            if "icon" not in data: data["icon"] = "NONE"
            number = hashText(data["id"]) if "id" in data else hashText(data["value"])
            items.append((data["value"], data["name"], data["description"], data["icon"], number))
        if len(items) == 0:
            items = [("NONE", "NONE", "")]
        return items
    return wrapper

def enumItemsFromList(function):
    def wrapper(self = None, context = None):
        items = []
        for element in function(self, context):
            items.append((element, element, "", "NONE", hashText(element)))
        if len(items) == 0:
            items = [("NONE", "NONE", "")]
        return items
    return wrapper

def hashText(text):
    return int(hash(text) % 1e9)
