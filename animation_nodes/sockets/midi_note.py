import bpy
from .. base_types import AnimationNodeSocket, PythonListSocket

class MIDINoteSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MIDINoteSocket"
    bl_label = "MIDI Note Socket"
    dataType = "MIDINote"
    drawColor = (0.9, 0.7, 0.4, 1)
    storable = True
    comparable = False

    def getCurrentDataType(self):
        linkedDataTypes = tuple(self.linkedDataTypes)
        if len(linkedDataTypes) == 0:
            return "MIDINote"
        else:
            return linkedDataTypes[0]

    @classmethod
    def getDefaultValue(cls):
        return None

    @classmethod
    def getDefaultValueCode(cls):
        return "None"

    @classmethod
    def correctValue(cls, value):
        return value, 0

class MIDINoteListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_MIDINoteListSocket"
    bl_label = "MIDINoteListSocket"
    dataType = "MIDINoteList"
    baseType = MIDINoteSocket
    drawColor = (0.9, 0.7, 0.4, 1)
    storable = True
    comparable = False

    @classmethod
    def correctValue(cls, value):
        return value, 0
