import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... data_structures import DoubleList

class GetCustomAttributeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetCustomAttributeNode"
    bl_label = "Get Custom Attribute"
    errorHandlingType = "EXCEPTION"

    dataType: StringProperty(name = "Color Mode", default = "FLOAT", update = AnimationNode.refresh)

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Text", "Attribute Name", "attributeName", value = "")

        if self.dataType == "FLOAT":
            self.newOutput("Float List", "Floats", "data")
        elif self.dataType == "INT":
            self.newOutput("Integer List", "Integers", "data")
        elif self.dataType == "FLOAT2":
            self.newOutput("Vector 2D List", "Vector2Ds", "data")
        elif self.dataType == "FLOAT_VECTOR":
            self.newOutput("Vector List", "Vectors ", "data")
        elif self.dataType in ["FLOAT_COLOR", "BYTE_COLOR"]:
            self.newOutput("Color List", "Colors", "data")
        else:
            self.newOutput("Boolean List", "Booleans", "data")
        self.newOutput("Text", "Type", "type", hide = True)
        self.newOutput("Text", "Domain ", "domain", hide = True)
        self.newOutput("Text", "Data Type ", "dataType", hide = True)

    def execute(self, mesh, attributeName):
        if mesh is None: return None, None, None
        if attributeName == "": self.raiseErrorMessage("Attribute name can't be empty.")

        attributes = mesh.getAllAttributes()
        attribute = attributes.get(attributeName, None)
        if attribute is None:
            self.raiseErrorMessage(f"""Object does not have attribute with name '{attributeName}'.\nAvailable: {self.getAttributeNames(attributes)}""")

        self.dataType = attribute.getListTypeAsString()
        if self.dataType == "FLOAT":
            return DoubleList.fromValues(attribute.data), attribute.getTypeAsString(), attribute.getDomainAsString(), self.dataType
        return attribute.data, attribute.getTypeAsString(), attribute.getDomainAsString(), self.dataType

    def getAttributeNames(self, attributes):
        attributesNames = [key for key in attributes.keys()]
        return attributesNames
