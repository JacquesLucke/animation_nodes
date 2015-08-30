import bpy
from .. data_structures.mesh import Polygon
from .. base_types.socket import AnimationNodeSocket

class PolygonSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_PolygonSocket"
    bl_label = "Polygon Socket"
    dataType = "Polygon"
    allowedInputTypes = ["Polygon"]
    drawColor = (0.14, 0.34, 0.19, 1)

    def getValue(self):
        return Polygon()

    def getCopyStatement(self):
        return "value.copy()"
