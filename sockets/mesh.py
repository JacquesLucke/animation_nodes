import bpy
import bmesh
from .. base_types.socket import AnimationNodeSocket

class MeshSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MeshSocket"
    bl_label = "Mesh Socket"
    dataType = "Mesh"
    allowedInputTypes = ["Mesh"]
    drawColor = (0.1, 1.0, 0.1, 1)

    def getValue(self):
        return bmesh.new()

    def getCopyStatement(self):
        return "value.copy()"
