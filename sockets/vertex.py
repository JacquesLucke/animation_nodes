import bpy
from mathutils import Vector
from .. data_structures.mesh import Vertex
from .. base_types.socket import AnimationNodeSocket

class VertexSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_VertexSocket"
    bl_label = "Vertex Socket"
    dataType = "Vertex"
    allowedInputTypes = ["Vertex"]
    drawColor = (0.55, 0.61, 0.32, 1)
    storable = True
    comparable = False

    def getValue(self):
        return Vertex(location = Vector((0, 0, 0)),
                      normal = Vector((0, 0, 1)),
                      groupWeights = [])

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"


class VertexListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_VertexListSocket"
    bl_label = "Vertex List Socket"
    dataType = "Vertex List"
    allowedInputTypes = ["Vertex List"]
    drawColor = (0.55, 0.61, 0.32, 0.5)
    storable = True
    comparable = False

    def getValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"
