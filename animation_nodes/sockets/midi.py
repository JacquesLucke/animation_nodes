import bpy
from .. base_types import AnimationNodeSocket, PythonListSocket

class MIDITracksSocket(bpy.types.NodeSocket, AnimationNodeSocket):
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


class MIDITracksSocketListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_MIDITrackListSocket"
    bl_label = "MIDITrackListSocket"
    dataType = "MIDITrackList"
    baseType = MIDITracksSocket
    drawColor = (0.2, 0.2, 0.8, 0.5)
    storable = True
    comparable = False

    @classmethod
    def correctValue(cls, value):
        return value, 0
