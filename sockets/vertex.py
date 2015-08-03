import bpy
from .. data_structures.mesh import Vertex
from .. base_types.socket import AnimationNodeSocket

class VertexSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_VertexSocket"
    bl_label = "Vertex Socket"
    dataType = "Vertex"
    allowedInputTypes = ["Vertex"]
    drawColor = (0.6, 0.8, 0.36, 1)

    def drawInput(self, layout, node, text):
        layout.label(text)

    def getValue(self):
        return Vertex()
