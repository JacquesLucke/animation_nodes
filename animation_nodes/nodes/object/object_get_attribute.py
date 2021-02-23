import bpy
from ... math import Vector
from ... base_types import AnimationNode
from ... data_structures import (
    Color,
    LongList,
    ColorList,
    DoubleList,
    BooleanList,
    Vector3DList,
)

class ObjectGetAttributeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectGetAttributeNode"
    bl_label = "Object Get Attribute"

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Text", "Attribute Name", "attName", value = "AN-Att")
        self.newOutput("Generic", "Value", "data")

    def execute(self, object, attName):
        if object is None: return None
        attribute = object.data.attributes.get(attName)
        if attribute is None: return None

        if attribute.domain == "POINT":
            amount = len(object.data.vertices)
        elif attribute.domain == "EDGE":
            amount = len(object.data.edges)
        else:
            amount = len(object.data.polygons)

        if attribute.data_type == "FLOAT":
            data = DoubleList(length = amount)
        elif attribute.data_type == "INT":
            data = LongList(length = amount)
        elif attribute.data_type == "FLOAT_VECTOR":
            data = Vector3DList(length = amount)
        elif attribute.data_type == "FLOAT_COLOR":
            data = ColorList(length = amount)
        else:
            data = BooleanList(False, length = amount)

        if attribute.data_type in["FLOAT", "INT", "BOOLEAN"]:
            attribute.data.foreach_get("value", data.asNumpyArray())
        elif attribute.data_type == "FLOAT_VECTOR":
            attribute.data.foreach_get("vector", data.asNumpyArray())
        else:
            attribute.data.foreach_get("color", data.asNumpyArray())

        return data
