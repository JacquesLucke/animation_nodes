import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... base_types import AnimationNode

keyDataTypeItems = [
    ("Transforms", "Transforms", "", "NONE", 0),
    ("String", "String", "", "NONE", 1),
    ("Integer", "Integer", "", "NONE", 2),
    ("Float", "Float", "", "NONE", 3)
]

class ObjectIDKeyNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectIDKeyNode"
    bl_label = "Object ID Key"
    bl_width_default = 160

    def keyChanged(self, context):
        self.recreateOutputs()

    keyDataType = EnumProperty(name = "Key Data Type",
        items = keyDataTypeItems, update = keyChanged)
    keyName = StringProperty(name = "Key Name", update = keyChanged)

    def create(self):
        self.newInput("Object", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.recreateOutputs()

    def drawAdvanced(self, layout):
        col = layout.column()
        col.prop(self, "keyDataType", text = "Type")
        col.prop(self, "keyName", text = "Name")

    def draw(self, layout):
        col = layout.column()
        col.scale_y = 1.5
        text = "Choose ID Key" if self.keyName == "" else repr(self.keyName)
        self.invokeIDKeyChooser(col, "assignIDKey", text = text, icon = "VIEWZOOM")

    def assignIDKey(self, dataType, name):
        self.keyDataType = dataType
        self.keyName = name

    def getExecutionCode(self):
        if self.keyName == "":
            return
            
        yield "exists = animation_nodes.id_keys.doesIDKeyExist(object, {}, {})".format(repr(self.keyDataType), repr(self.keyName))
        yield "data = animation_nodes.id_keys.getIDKeyData(object, {}, {})".format(repr(self.keyDataType), repr(self.keyName))

        dataType = self.keyDataType
        isLinked = self.getLinkedOutputsDict()

        if dataType == "Transforms":
            yield "location, rotation, scale = data"
            if isLinked["matrix"]:
                yield "matrix = animation_nodes.utils.math.composeMatrix(location, rotation, scale)"

        if dataType == "String":
            yield "text = data"

        if dataType in ("Integer", "Float"):
            yield "number = data"

    @keepNodeLinks
    def recreateOutputs(self):
        self.outputs.clear()
        if self.keyName == "":
            return

        dataType = self.keyDataType
        self.newOutput("Boolean", "Exists", "exists")

        if dataType == "Transforms":
            self.newOutput("Vector", "Location", "location")
            self.newOutput("Euler", "Rotation", "rotation")
            self.newOutput("Vector", "Scale", "scale")
            self.newOutput("Matrix", "Matrix", "matrix")

        if dataType == "String":
            self.newOutput("String", "Text", "text")

        if dataType in ("Integer", "Float"):
            self.newOutput("Integer", "Number", "number")
