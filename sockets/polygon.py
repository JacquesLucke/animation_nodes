import bpy
from mathutils import Vector
from .. data_structures.mesh import Polygon
from .. base_types.socket import AnimationNodeSocket

class PolygonSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_PolygonSocket"
    bl_label = "Polygon Socket"
    dataType = "Polygon"
    allowedInputTypes = ["Polygon"]
    drawColor = (0.4, 0.7, 0.3, 1)
    storable = True
    comparable = False

    def getValue(self):
        return Polygon(vertexLocations = [Vector((-1, 0, 0)), Vector((1, 0, 0)), Vector((0, 1, 0))],
                       normal = Vector((0, 0, 1)),
                       center = Vector((0, 1/3, 0)),
                       area = 2,
                       materialIndex = 0)

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"


class PolygonListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_PolygonListSocket"
    bl_label = "Polygon List Socket"
    dataType = "Polygon List"
    allowedInputTypes = ["Polygon List"]
    drawColor = (0.4, 0.7, 0.3, 0.5)
    storable = True
    comparable = False

    def getValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"
