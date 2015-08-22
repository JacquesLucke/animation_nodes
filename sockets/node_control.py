import bpy
from bpy.props import *
from .. base_types.socket import AnimationNodeSocket

class NodeControlSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_NodeControlSocket"
    bl_label = "Node Control Socket"
    dataType = "Node Control"
    allowedInputTypes = []
    drawColor = (0.0, 0.0, 0.0, 0.0)

    drawNameOnly = BoolProperty(default = True)
    drawCallback = StringProperty()

    def draw(self, context, layout, node, text):
        if self.drawNameOnly:
            layout.label(self.name)
        else:
            function = getattr(node, self.drawCallback)
            function(layout)
