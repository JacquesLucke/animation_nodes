import bpy
from bpy.props import *
from ... math import Vector
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import (
    Color,
    FloatList,
    Attribute,
    AttributeType,
    AttributeDomain,
    VirtualLongList,
    VirtualColorList,
    AttributeDataType,
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
    ("FLOAT", "Float", "", "NONE", 0),
    ("INT", "Integer", "", "NONE", 1),
    ("FLOAT2", "Float2", "", "NONE", 2),
    ("FLOAT_VECTOR", "Vector", "", "NONE", 3),
    ("FLOAT_COLOR", "Color", "", "NONE", 4),
    ("BYTE_COLOR", "Byte Color", "", "NONE", 5),
    ("BOOLEAN", "Boolean", "", "NONE", 6),
]

class InsertCustomAttributeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InsertCustomAttributeNode"
    bl_label = "Insert Custom Attribute"
    errorHandlingType = "EXCEPTION"

    domain: EnumProperty(name = "Domain", default = "POINT",
        items = domainItems, update = AnimationNode.refresh)

    dataType: EnumProperty(name = "Data Type", default = "FLOAT",
        items = dataTypeItems, update = AnimationNode.refresh)

    useDataList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Text", "Attribute Name", "attributeName", value = "AN-Att")
        if self.dataType == "FLOAT":
            self.newInput(VectorizedSocket("Float", "useDataList",
            ("Value", "data"), ("Values", "data")))
        elif self.dataType == "INT":
            self.newInput(VectorizedSocket("Integer", "useDataList",
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

        self.newOutput("Mesh", "Mesh", "mesh")

    def draw(self, layout):
        layout.prop(self, "domain", text = "")
        layout.prop(self, "dataType", text = "")

    def execute(self, mesh, attributeName, data):
        if mesh is None: return mesh

        if attributeName == "":
            self.raiseErrorMessage("Attribute name can't be empty.")
        elif attributeName in mesh.getAttributeNames(AttributeType.CUSTOM):
            self.raiseErrorMessage(f"Mesh has already a vertex color layer with the name '{attributeName}'.")

        if self.domain == "POINT":
            amount = len(mesh.vertices)
        elif self.domain == "EDGE":
            amount = len(mesh.edges)
        elif self.domain == "FACE":
            amount = len(mesh.polygons)
        else:
            amount = len(mesh.polygons.indices)

        if self.dataType == "FLOAT":
            _data = FloatList.fromValues(VirtualDoubleList.create(data, 0).materialize(amount))
        elif self.dataType == "INT":
            _data = VirtualLongList.create(data, 0).materialize(amount)
        elif self.dataType == "FLOAT2":
            _data = VirtualVector2DList.create(data, Vector((0, 0))).materialize(amount)
        elif self.dataType == "FLOAT_VECTOR":
            _data = VirtualVector3DList.create(data, Vector((0, 0, 0))).materialize(amount)
        elif self.dataType in ("FLOAT_COLOR", "BYTE_COLOR"):
            _data = VirtualColorList.create(data, Color((0, 0, 0, 0))).materialize(amount)
        else:
            _data = VirtualBooleanList.create(data, False).materialize(amount)

        mesh.insertAttribute(Attribute(attributeName, AttributeType.CUSTOM, AttributeDomain[self.domain],
                                       AttributeDataType[self.dataType], _data))
        return mesh
