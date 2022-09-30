import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... data_structures import DoubleList

dataTypeItems = [
    ("INT", "Integer", "", "NONE", 0),
    ("FLOAT", "Float", "", "NONE", 1),
    ("FLOAT2", "Float2", "", "NONE", 2),
    ("FLOAT_VECTOR", "Vector", "", "NONE", 3),
    ("FLOAT_COLOR", "Color", "", "NONE", 4),
    ("BYTE_COLOR", "Byte Color", "", "NONE", 5),
    ("BOOLEAN", "Boolean", "", "NONE", 6),
]

class GetCustomAttributeNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_GetCustomAttributeNode"
    bl_label = "Get Custom Attribute"
    errorHandlingType = "EXCEPTION"

    dataType: EnumProperty(name = "Data Type", default = "FLOAT",
        items = dataTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Text", "Name", "attributeName", value = "")

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

        attribute = mesh.getCustomAttribute(attributeName)
        if attribute is None:
            self.raiseErrorMessage(
                    f"Object does not have attribute with name '{attributeName}'."
                    f"\nAvailable: {mesh.getAllCustomAttributeNames()}"
            )

        if self.dataType != attribute.getListTypeAsString():
            self.raiseErrorMessage(
                f"Wrong output data type. Attribute is of type '{attribute.getListTypeAsString()}'.")

        if self.dataType == "FLOAT":
            return DoubleList.fromValues(attribute.data), attribute.getTypeAsString(), attribute.getDomainAsString(), self.dataType
        return attribute.data, attribute.getTypeAsString(), attribute.getDomainAsString(), self.dataType
