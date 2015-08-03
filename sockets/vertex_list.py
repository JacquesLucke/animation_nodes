import bpy
from .. base_types.socket import AnimationNodeSocket

class VertexListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_VertexListSocket"
    bl_label = "Vertex List Socket"
    dataType = "Vertex List"
    allowedInputTypes = ["Vertex List"]
    drawColor = (0.3, 1.0, 0.4, 1.0)

    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return []
