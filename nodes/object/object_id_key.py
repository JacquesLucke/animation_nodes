import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

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

    def keyDataTypeChanged(self, context):
        self.recreateOutputs()

    keyDataType = EnumProperty(name = "Key Data Type",
        items = keyDataTypeItems, update = keyDataTypeChanged)
    keyName = StringProperty(name = "Key Name", update = executionCodeChanged)

    def create(self):
        self.newInput("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
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
        self.newOutput("an_BooleanSocket", "Exists", "exists")

        dataType = self.keyDataType

        if dataType == "Transforms":
            self.newOutput("an_VectorSocket", "Location", "location")
            self.newOutput("an_EulerSocket", "Rotation", "rotation")
            self.newOutput("an_VectorSocket", "Scale", "scale")
            self.newOutput("an_MatrixSocket", "Matrix", "matrix")

        if dataType == "String":
            self.newOutput("an_StringSocket", "Text", "text")

        if dataType in ("Integer", "Float"):
            self.newOutput("an_IntegerSocket", "Number", "number")
