import bpy
from mathutils.bvhtree import BVHTree
from .. base_types.socket import AnimationNodeSocket

class BVHTreeSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_BVHTreeSocket"
    bl_label = "BVHTree Socket"
    dataType = "BVHTree"
    allowedInputTypes = ["BVHTree"]
    drawColor = (0.18, 0.32, 0.32, 1)
    hashable = True
    storable = True

    def getValue(self):
        return BVHTree.FromPolygons(vertices = [], polygons = [])
