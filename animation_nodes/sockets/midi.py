import bpy
from .. base_types import AnimationNodeSocket, PythonListSocket

class MIDITrackSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MIDITrackSocket"
    bl_label = "MIDI Track Socket"
    dataType = "MIDITrack"
    drawColor = (0.2, 0.2, 0.8, 1)
    storable = True
    comparable = False

    def getCurrentDataType(self):
        linkedDataTypes = tuple(self.linkedDataTypes)
        if len(linkedDataTypes) == 0:
            return "MIDITrack"
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


class MIDITrackListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_MIDITrackListSocket"
    bl_label = "MIDITrackListSocket"
    dataType = "MIDITrackList"
    baseType = MIDITrackSocket
    drawColor = (0.2, 0.2, 0.8, 0.5)
    storable = True
    comparable = False

    @classmethod
    def correctValue(cls, value):
        return value, 0

class MIDINoteSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MIDINoteSocket"
    bl_label = "MIDI Note Socket"
    dataType = "MIDINote"
    drawColor = (0.2, 0.2, 0.8, 1)
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
    drawColor = (0.2, 0.2, 0.8, 0.5)
    storable = True
    comparable = False

    @classmethod
    def correctValue(cls, value):
        return value, 0
