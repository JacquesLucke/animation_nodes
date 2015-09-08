import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

class SoundSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_SoundSocket"
    bl_label = "Sound Socket"
    dataType = "Sound"
    allowedInputTypes = ["Sound"]
    drawColor = (0.9, 0.7, 0.4, 1)

    def getValueCode(self):
        return "None"
