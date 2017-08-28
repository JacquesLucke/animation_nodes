import functools

def setattrRecursive(owner, propName, value):
    getAttributeSetter(propName)(owner, value)

def getattrRecursive(owner, propName):
    return getAttributeGetter(propName)(owner)

@functools.lru_cache(maxsize = 1024)
def getAttributeSetter(propName):
    variables = {}
    exec("def attrSetter(owner, value): owner.{} = value".format(propName), variables)
    return variables["attrSetter"]

@functools.lru_cache(maxsize = 1024)
def getAttributeGetter(propName):
    return eval("lambda owner: owner.{}".format(propName))

def hasEvaluableRepr(value):
    try: return eval(repr(value)) == value
    except: return False

def pathBelongsToArray(object, dataPath):
    if "." in dataPath:
        pathToProperty, propertyName = dataPath.rsplit(".", 1)
        pathToProperty = "." + pathToProperty
    else:
        pathToProperty = ""
        propertyName = dataPath

    try:
        amount = eval("object{}.bl_rna.properties[{}].array_length".format(pathToProperty, repr(propertyName)))
        return amount > 0
    except:
        # Means that the property has not been found
        return None
