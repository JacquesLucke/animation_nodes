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

@functools.lru_cache(maxsize = 1024)
def getMultiAttibuteSetter(propNames):
    code = "def setter(owner, values):\n"
    for i, prop in enumerate(propNames):
        lines = getAttributeSetterLines("owner", prop, "values[{}]".format(i))
        code += ''.join("    " + line + "\n" for line in lines)
    code += "    pass"
    variables = {}
    exec(code, variables)
    return variables["setter"]

def getAttributeSetterLines(objectName, propName, valueName):
    if propName.startswith('['):
        # Path is a named attribute
        path = "{}{}".format(objectName, propName)
    else:
        path = "{}.{}".format(objectName, propName)

    return (
        'try: {} = type({})({}) # Try to cast to existing property type'.format(path, path, valueName),
        'except: {} = {} # Property does not exist; default to new float'.format(path, valueName)
    )

def hasEvaluableRepr(value):
    try: return eval(repr(value)) == value
    except: return False

pathArrayCache = {}
def pathBelongsToArray(object, dataPath):
    inputHash = hash((object, dataPath))
    if inputHash not in pathArrayCache:
        result = _pathBelongsToArray(object, dataPath)
        if result is not None:
            pathArrayCache[inputHash] = result
    return pathArrayCache.get(inputHash, None)

def _pathBelongsToArray(object, dataPath):
    if not dataPath.startswith("[") and not dataPath.startswith("."):
        dataPath = "." + dataPath

    try:
        data = eval("object{}".format(dataPath))
        if isinstance(data, str):
            return False # Strings have len() but aren't arrays
        return len(data) > 0
    except:
        # Path not found
        return None
