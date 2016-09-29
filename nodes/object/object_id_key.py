import bpy
from bpy.props import *
from ... math import composeMatrixList
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

    searchTags = [("Object Initial Transforms",
                   {"keyDataType" : repr("Transforms"),
                    "keyName" : repr("Initial Transforms")})]

    keyDataType = EnumProperty(name = "Key Data Type", default = "Transforms",
        items = keyDataTypeItems, update = AnimationNode.updateSockets)

    keyName = StringProperty(name = "Key Name", default = "",
        update = AnimationNode.updateSockets)

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
        if self.keyName == "":
            return

        keyName = repr(self.keyName)
        yield "_key = animation_nodes.id_keys.IDKeyTypes[{}]".format(repr(self.keyDataType))
        if self.useList:
            yield from self.getExecutionCode_List(keyName)
        else:
            yield from self.getExecutionCode_Base(keyName)

    def getExecutionCode_Base(self, keyName):
        dataType = self.keyDataType
        isLinked = self.getLinkedOutputsDict()

        if isLinked["exists"]:
            yield "exists = _key.exists(object, %s)" % keyName

        yield "data = _key.get(object, %s)" % keyName

        if dataType == "Transforms":
            yield "location, rotation, scale = data"
            if isLinked["matrix"]:
                yield "matrix = animation_nodes.utils.math.composeMatrix(location, rotation, scale)"
        elif dataType == "Text":
            yield "text = data"
        elif dataType in ("Integer", "Float"):
            yield "number = data"

    def getExecutionCode_List(self, keyName):
        dataType = self.keyDataType
        isLinked = self.getLinkedOutputsDict()

        if isLinked["exists"]:
            yield "exists = _key.existsList(objects, %s)" % keyName

        if dataType == "Transforms":
            useMatrices = isLinked["matrices"]
            if isLinked["locations"] or useMatrices:
                yield "locations = _key.getLocations(objects, %s)" % keyName
            if isLinked["rotations"] or useMatrices:
                yield "rotations = _key.getRotations(objects, %s)" % keyName
            if isLinked["scales"] or useMatrices:
                yield "scales = _key.getScales(objects, %s)" % keyName
            if useMatrices:
                yield "matrices = animation_nodes.math.composeMatrixList(locations, rotations, scales)"
        elif dataType == "Text":
            if isLinked["texts"]:
                yield "texts = _key.getList(objects, %s)" % keyName
        elif dataType in ("Integer", "Float"):
            if isLinked["numbers"]:
                yield "numbers = _key.getList(objects, %s)" % keyName

    def getList_Exists(self, objects):
        from animation_nodes.id_keys import doesIDKeyExist
        return [doesIDKeyExist(object, self.keyDataType, self.keyName) for object in objects]
