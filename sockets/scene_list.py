import bpy
from .. base_types.socket import AnimationNodeSocket

class SceneListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_SceneListSocket"
    bl_label = "Scene List Socket"
    dataType = "Scene List"
    allowedInputTypes = ["Scene List"]
    drawColor = (0.2, 0.3, 0.4, 0.5)
    storable = False
    hashable = False

    def getValue(self):
        return [self.nodeTree.scene]

    def getCopyExpression(self):
        return "value[:]"
