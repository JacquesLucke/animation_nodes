import bpy
from mathutils import Vector
from .. data_structures.mesh import Vertex
from .. base_types.socket import AnimationNodeSocket

class VertexSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_VertexSocket"
    bl_label = "Vertex Socket"
    dataType = "Vertex"
    allowedInputTypes = ["Vertex"]
    drawColor = (0.6, 0.8, 0.36, 1)

    def getValue(self):
        return Vertex(
            location = Vector((0, 0, 0)),
            normal = Vector((0, 0, 1)),
            groupWeights = [])

    def getCopyExpression(self):
        return "value.copy()"
