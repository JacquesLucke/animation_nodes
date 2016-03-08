import bpy
from mathutils.kdtree import KDTree
from .. base_types.socket import AnimationNodeSocket

class KDTreeSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_KDTreeSocket"
    bl_label = "KDTree Socket"
    dataType = "KDTree"
    allowedInputTypes = ["KDTree"]
    drawColor = (0.32, 0.32, 0.18, 1)
    comparable = True
    storable = True

    def getValue(self):
        kdTree = KDTree(0)
        kdTree.balance()
        return kdTree
