import bpy
from .. data_structures import MIDITrack
from .. base_types import AnimationNodeSocket, PythonListSocket

class MIDITrackSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MIDITrackSocket"
    bl_label = "MIDI Track Socket"
    dataType = "MIDI Track"
    drawColor = (0.75, 0.6, 0.45, 1)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return MIDITrack()

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, MIDITrack):
            return value, 0
        return cls.getDefaultValue(), 2

class MIDITrackListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_MIDITrackListSocket"
    bl_label = "MIDI Track List Socket"
    dataType = "MIDI Track List"
    baseType = MIDITrackSocket
    drawColor = (0.75, 0.6, 0.45, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "[track.copy() for track in value]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, MIDITrack) for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
