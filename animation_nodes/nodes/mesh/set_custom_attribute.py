import bpy
from bpy.props import *
from ... math import Vector
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import (
    Color,
    FloatList,
    VirtualLongList,
    VirtualColorList,
    VirtualDoubleList,
    VirtualBooleanList,
    VirtualVector2DList,
    VirtualVector3DList,
)

domainItems = [
    ("POINT", "Point", "", "NONE", 0),
    ("EDGE", "Edge", "", "NONE", 1),
    ("FACE", "Face", "NONE", 2),
    ("CORNER", "Corner", "", "NONE", 3),
]

dataTypeItems = [
    ("INT", "Integer", "", "NONE", 0),
    ("FLOAT", "Float", "", "NONE", 1),
    ("FLOAT2", "Float2", "", "NONE", 2),
    ("FLOAT_VECTOR", "Vector", "", "NONE", 3),
    ("FLOAT_COLOR", "Color", "", "NONE", 4),
    ("BYTE_COLOR", "Byte Color", "", "NONE", 5),
    ("BOOLEAN", "Boolean", "", "NONE", 6),
]

class SetCustomAttributeNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_SetCustomAttributeNode"
    bl_label = "Set Custom Attribute"
    errorHandlingType = "EXCEPTION"

    domain: EnumProperty(name = "Domain", default = "POINT",
        items = domainItems, update = AnimationNode.refresh)

    dataType: EnumProperty(name = "Data Type", default = "FLOAT",
        items = dataTypeItems, update = AnimationNode.refresh)

    useDataList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Text", "Name", "customAttributeName", value = "AN-Att")
        if self.dataType == "INT":
            self.newInput(VectorizedSocket("Integer", "useDataList",
            ("Value", "data"), ("Values", "data")))
        elif self.dataType == "FLOAT":
            self.newInput(VectorizedSocket("Float", "useDataList",
            ("Value", "data"), ("Values", "data")))
        elif self.dataType == "FLOAT2":
            self.newInput(VectorizedSocket("Vector 2D", "useDataList",
            ("Vector 2D", "data"), ("Vectors 2D", "data")))
        elif self.dataType == "FLOAT_VECTOR":
            self.newInput(VectorizedSocket("Vector", "useDataList",
            ("Vector", "data"), ("Vectors", "data")))
        elif self.dataType in ("FLOAT_COLOR", "BYTE_COLOR"):
            self.newInput(VectorizedSocket("Color", "useDataList",
            ("Color", "data"), ("Colors", "data")))
        else:
            self.newInput(VectorizedSocket("Boolean", "useDataList",
            ("Value", "data"), ("Values", "data")))

        self.newOutput("Object", "Object", "object")

    def draw(self, layout):
        layout.prop(self, "domain", text = "")
        layout.prop(self, "dataType", text = "")

    def execute(self, object, customAttributeName, data):
        if object is None: return object
        if object.type != "MESH": self.raiseErrorMessage("Object should be Mesh type.")
        if customAttributeName == "": self.raiseErrorMessage("Attribute name can't be empty.")

        attribute = object.data.attributes.get(customAttributeName)
        if attribute is None:
            attribute = object.data.attributes.new(customAttributeName, self.dataType, self.domain)
        elif attribute.data_type != self.dataType or attribute.domain != self.domain:
            object.data.attributes.remove(attribute)
            attribute = object.data.attributes.new(customAttributeName, self.dataType, self.domain)

        if self.domain == "POINT":
            amount = len(object.data.vertices)
        elif self.domain == "EDGE":
            amount = len(object.data.edges)
        elif self.domain == "FACE":
            amount = len(object.data.polygons)
        else:
            amount = len(object.data.loops)

        if self.dataType == "INT":
            _data = VirtualLongList.create(data, 0).materialize(amount)
        elif self.dataType == "FLOAT":
            _data = FloatList.fromValues(VirtualDoubleList.create(data, 0).materialize(amount))
        elif attribute.data_type == "FLOAT2":
            _data = VirtualVector2DList.create(data, Vector((0, 0))).materialize(amount)
        elif self.dataType == "FLOAT_VECTOR":
            _data = VirtualVector3DList.create(data, Vector((0, 0, 0))).materialize(amount)
        elif self.dataType in ("FLOAT_COLOR", "BYTE_COLOR"):
            _data = VirtualColorList.create(data, Color((0, 0, 0, 0))).materialize(amount)
        else:
            _data = VirtualBooleanList.create(data, False).materialize(amount)

        if self.dataType in ("FLOAT", "INT", "BOOLEAN"):
            attribute.data.foreach_set("value", _data.asMemoryView())
        elif self.dataType in ("FLOAT2", "FLOAT_VECTOR"):
            attribute.data.foreach_set("vector", _data.asMemoryView())
        else:
            attribute.data.foreach_set("color", _data.asMemoryView())

        attribute.data.update()
        return object
