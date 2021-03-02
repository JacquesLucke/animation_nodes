import bpy
from ... math import Vector
from ... base_types import AnimationNode
from ... utils.depsgraph import getEvaluatedID
from ... data_structures import (
    Color,
    LongList,
    ColorList,
    DoubleList,
    BooleanList,
    Vector2DList,
    Vector3DList,
)

class GetCustomAttributeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetCustomAttributeNode"
    bl_label = "Get Custom Attribute"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Text", "Attribute Name", "attName", value = "AN-Att")
        self.newOutput("Generic", "Value", "data")

    def execute(self, object, attName):
        if object is None: return None
        if attName == "": self.raiseErrorMessage("Attribute name can't be empty.")

        evaluatedObject = getEvaluatedID(object)
        attribute = evaluatedObject.data.attributes.get(attName)
        if attribute is None:
            self.raiseErrorMessage(f"""Object does not have attribute with name '{attName}'.\nAvailable: {evaluatedObject.data.attributes.keys()}""")

        if attribute.domain == "POINT":
            amount = len(evaluatedObject.data.vertices)
        elif attribute.domain == "EDGE":
            amount = len(evaluatedObject.data.edges)
        elif attribute.domain == "CORNER":
            amount = len(evaluatedObject.data.loops)
        else:
            amount = len(evaluatedObject.data.polygons)

        if attribute.data_type == "FLOAT":
            data = DoubleList(length = amount)
        elif attribute.data_type == "INT":
            data = LongList(length = amount)
        elif attribute.data_type == "FLOAT2":
            data = Vector2DList(length = amount)
        elif attribute.data_type == "FLOAT_VECTOR":
            data = Vector3DList(length = amount)
        elif attribute.data_type in ["FLOAT_COLOR", "BYTE_COLOR"]:
            data = ColorList(length = amount)
        else:
            data = BooleanList(False, length = amount)

        if attribute.data_type in["FLOAT", "INT", "BOOLEAN"]:
            attribute.data.foreach_get("value", data.asNumpyArray())
        elif attribute.data_type in ["FLOAT2", "FLOAT_VECTOR"]:
            attribute.data.foreach_get("vector", data.asNumpyArray())
        else:
            attribute.data.foreach_get("color", data.asNumpyArray())

        return data
