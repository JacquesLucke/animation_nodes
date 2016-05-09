import bpy
from mathutils import Vector
from .. data_structures.mesh import Vertex
from .. base_types.socket import AnimationNodeSocket, ListSocket

class VertexSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_VertexSocket"
    bl_label = "Vertex Socket"
    dataType = "Vertex"
    allowedInputTypes = ["Vertex"]
    drawColor = (0.55, 0.61, 0.32, 1)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return Vertex(location = Vector((0, 0, 0)),
                      normal = Vector((0, 0, 1)),
                      groupWeights = [])

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, Vertex):
            return value, 0
        return cls.getDefaultValue(), 2


class VertexListSocket(bpy.types.NodeSocket, ListSocket, AnimationNodeSocket):
    bl_idname = "an_VertexListSocket"
    bl_label = "Vertex List Socket"
    dataType = "Vertex List"
    baseDataType = "Vertex"
    allowedInputTypes = ["Vertex List"]
    drawColor = (0.55, 0.61, 0.32, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, Vertex) for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
