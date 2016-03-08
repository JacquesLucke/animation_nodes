import bpy
from mathutils import Vector
from .. data_structures.mesh import Polygon
from .. base_types.socket import AnimationNodeSocket

class FCurveSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_FCurveSocket"
    bl_label = "FCurve Socket"
    dataType = "FCurve"
    allowedInputTypes = ["FCurve"]
    drawColor = (0.2, 0.26, 0.19, 1)
    storable = True
    comparable = True

    def getValueCode(self):
        return "None"
