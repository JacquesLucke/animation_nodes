import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... base_types import AnimationNode, AutoSelectVectorization

keyDataTypeItems = [
    ("Transforms", "Transforms", "", "NONE", 0),
    ("Text", "Text", "", "NONE", 1),
    ("Integer", "Integer", "", "NONE", 2),
    ("Float", "Float", "", "NONE", 3)
]

class ObjectIDKeyNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectIDKeyNode"
    bl_label = "Object ID Key"
    bl_width_default = 160

    keyDataType = EnumProperty(name = "Key Data Type",
        items = keyDataTypeItems, update = AnimationNode.updateSockets)
    keyName = StringProperty(name = "Key Name", update = AnimationNode.updateSockets)

    useList = BoolProperty(default = False, update = AnimationNode.updateSockets)

    def create(self):
        self.newInputGroup(self.useList,
            ("Object", "Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Object List", "Objects", "objects"))

        if self.keyName != "":
            if self.keyDataType == "Transforms":
                self.newOutputGroup(self.useList,
                    ("Vector", "Location", "location"),
                    ("Vector List", "Locations", "locations"))
                self.newOutputGroup(self.useList,
                    ("Euler", "Rotation", "rotation"),
                    ("Euler List", "Rotations", "rotations"))
                self.newOutputGroup(self.useList,
                    ("Vector", "Scale", "scale"),
                    ("Vector List", "Scales", "scales"))
                self.newOutputGroup(self.useList,
                    ("Matrix", "Matrix", "matrix"),
                    ("Matrix List", "Matrices", "matrices"))
            elif self.keyDataType == "Text":
                self.newOutputGroup(self.useList,
                    ("Text", "Text", "text"),
                    ("Text List", "Texts", "texts"))
            elif self.keyDataType == "Integer":
                self.newOutputGroup(self.useList,
                    ("Integer", "Number", "number"),
                    ("Integer List", "Numbers", "numbers"))
            elif self.keyDataType == "Float":
                self.newOutputGroup(self.useList,
                    ("Float", "Number", "number"),
                    ("Float List", "Numbers", "numbers"))

            self.newOutputGroup(self.useList,
                ("Boolean", "Exists", "exists", dict(hide = True)),
                ("Boolean List", "Exists", "exists", dict(hide = True)))

        vectorization = AutoSelectVectorization()
        vectorization.add(self, "useList", list(self.inputs) + list(self.outputs))
        self.newSocketEffect(vectorization)

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
        return
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

        if dataType == "Text":
            yield "text = data"

        if dataType in ("Integer", "Float"):
            yield "number = data"
