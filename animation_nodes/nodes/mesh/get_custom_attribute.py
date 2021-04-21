import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... data_structures import DoubleList, AttributeType

dataTypeItems = [
    ("INT", "Integer", "", "NONE", 0),
    ("FLOAT", "Float", "", "NONE", 1),
    ("FLOAT2", "Float2", "", "NONE", 2),
    ("FLOAT_VECTOR", "Vector", "", "NONE", 3),
    ("FLOAT_COLOR", "Color", "", "NONE", 4),
    ("BYTE_COLOR", "Byte Color", "", "NONE", 5),
    ("BOOLEAN", "Boolean", "", "NONE", 6),
]

class GetCustomAttributeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetCustomAttributeNode"
    bl_label = "Get Custom Attribute"
    errorHandlingType = "EXCEPTION"

    dataType: EnumProperty(name = "Data Type", default = "FLOAT",
        items = dataTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Text", "Attribute Name", "attributeName", value = "")

        if self.dataType == "FLOAT":
            self.newOutput("Float List", "Values", "data")
        elif self.dataType == "INT":
            self.newOutput("Integer List", "Values", "data")
        elif self.dataType == "FLOAT2":
            self.newOutput("Vector 2D List", "Vectors 2D", "data")
        elif self.dataType == "FLOAT_VECTOR":
            self.newOutput("Vector List", "Vectors", "data")
        elif self.dataType in ("FLOAT_COLOR", "BYTE_COLOR"):
            self.newOutput("Color List", "Colors", "data")
        else:
            self.newOutput("Boolean List", "Values", "data")
        self.newOutput("Text", "Type", "type", hide = True)
        self.newOutput("Text", "Domain ", "domain", hide = True)
        self.newOutput("Text", "Data Type ", "dataType", hide = True)

    def draw(self, layout):
        layout.prop(self, "dataType", text = "")

    def execute(self, mesh, attributeName):
        if mesh is None: return None, None, None, None
        if attributeName == "": self.raiseErrorMessage("Attribute name can't be empty.")

        attribute = self.getPossibleAttribute(attributeName, mesh)
        if self.dataType != attribute.getListTypeAsString():
            self.raiseErrorMessage("Wrong output data type.")

        if self.dataType == "FLOAT":
            return DoubleList.fromValues(attribute.data), attribute.getTypeAsString(), attribute.getDomainAsString(), self.dataType
        return attribute.data, attribute.getTypeAsString(), attribute.getDomainAsString(), self.dataType

    def getPossibleAttribute(self, attributeName, mesh):
        attribute = mesh.getAttribute(attributeName, AttributeType.CUSTOM)
        if attribute is not None: return attribute

        attribute = mesh.getAttribute(attributeName, AttributeType.UV_MAP)
        if attribute is not None: return attribute

        attribute = mesh.getAttribute(attributeName, AttributeType.VERTEX_COLOR)
        if attribute is not None: return attribute

        self.raiseErrorMessage(f"""Object does not have attribute with name '{attributeName}'.\nAvailable: {self.getAttributeNames(mesh)}""")

    def getAttributeNames(self, mesh):
        attributeNames = list()
        for (meshAttributes, _) in mesh.getMeshAttributes():
            attributeNames.extend(meshAttributes.keys())
        return attributeNames
