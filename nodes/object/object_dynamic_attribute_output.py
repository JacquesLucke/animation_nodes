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
        try:
            setAttribute = getSetFunction(object, path)
            setAttribute(object, arrayIndex, value)
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

def createSetFunction(object, attribute):
    data = {}
    try:
        eval("object.{}[0]".format(attribute))
        exec(setAttributeWithIndex.replace("attribute", attribute), data, data)
        return data["setAttributeWithIndex"]
    except:
        try:
            eval("object." + attribute)
            exec(setAttributeWithoutIndex.replace("attribute", attribute), data, data)
            return data["setAttributeWithoutIndex"]
        except: pass
    return None

setAttributeWithIndex = '''
def setAttributeWithIndex(object, index, value):
    object.attribute[index] = value
'''

setAttributeWithoutIndex = '''
def setAttributeWithoutIndex(object, index, value):
    object.attribute = value
'''
