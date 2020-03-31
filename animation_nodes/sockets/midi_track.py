import bpy
from .. base_types import AnimationNodeSocket, PythonListSocket

class MIDITrackSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MIDITrackSocket"
    bl_label = "MIDI Track Socket"
    dataType = "midiTrack"
    drawColor = (0.9, 0.7, 0.4, 1)
    storable = True
    comparable = False

    def getCurrentDataType(self):
        linkedDataTypes = tuple(self.linkedDataTypes)
        if len(linkedDataTypes) == 0:
            return "midiTrack"
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
    drawColor = (0.9, 0.7, 0.4, 1)
    storable = True
    comparable = False

    @classmethod
    def correctValue(cls, value):
        return value, 0
