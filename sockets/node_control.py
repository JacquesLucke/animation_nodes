import bpy
from bpy.props import *
from .. base_types.socket import AnimationNodeSocket

class NodeControlSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_NodeControlSocket"
    bl_label = "Node Control Socket"
    dataType = "Node Control"
    allowedInputTypes = ["None"]
    drawColor = (0.0, 0.0, 0.0, 0.0)
    storable = False
    hashable = False

    margin = FloatProperty(default = 0.0001, min = 0.0001)

    def draw(self, context, layout, node, text):
        col = layout.column()
        subcol = col.column()
        subcol.label("")
        subcol.scale_y = self.margin

        node.drawControlSocket(col, self)

        subcol = col.column()
        subcol.label("")
        subcol.scale_y = self.margin
