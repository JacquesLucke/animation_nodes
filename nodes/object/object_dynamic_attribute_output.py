import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class DynamicObjectAttributeOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DynamicObjectAttributeOutputNode"
    bl_label = "Dynamic Object Attribute Output"

    errorMessage = StringProperty()

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_StringSocket", "Path", "path")
        self.inputs.new("an_IntegerSocket", "Array Index", "arrayIndex")
        self.inputs.new("an_GenericSocket", "Value", "value")
        self.outputs.new("an_ObjectSocket", "Object", "object")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawAdvanced(self, layout):
        self.invokeFunction(layout, "clearCache", text = "Clear Cache")

    def execute(self, object, path, arrayIndex, value):
        if object is None: return object
        setAttributeFunction = getSetFunction(object, path)
        if setAttributeFunction is None: return object
        try:
            setAttributeFunction(object, arrayIndex, value)
            self.errorMessage = ""
        except:
            self.errorMessage = "Error"
        return object

    def clearCache(self):
        cache.clear()

cache = {}

def getSetFunction(object, attribute):
    if attribute in cache: return cache[attribute]

    function = createSetFunction(object, attribute)
    cache[attribute] = function
    return function

def createSetFunction(object, dataPath):
    needsIndex = dataPathBelongsToArray(object, dataPath)
    if needsIndex is None: return None
    data = {}
    if needsIndex:
        exec(setAttributeWithIndex.replace("#dataPath#", dataPath), data, data)
        return data["setAttributeWithIndex"]
    else:
        exec(setAttributeWithoutIndex.replace("#dataPath#", dataPath), data, data)
        return data["setAttributeWithoutIndex"]

setAttributeWithIndex = '''
def setAttributeWithIndex(object, index, value):
    object.#dataPath#[index] = value
'''

setAttributeWithoutIndex = '''
def setAttributeWithoutIndex(object, index, value):
    object.#dataPath# = value
'''

def dataPathBelongsToArray(object, dataPath):
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
