import bpy
from .. data_structures import MIDITempoEvent
from .. base_types import AnimationNodeSocket, PythonListSocket

class MIDITempoEventSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MIDITempoEventSocket"
    bl_label = "MIDI Tempo Event Socket"
    dataType = "MIDI Tempo Event"
    drawColor = (0.6, 0.75, 0.45, 1)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return MIDITempoEvent()

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, MIDITempoEvent):
            return value, 0
        return cls.getDefaultValue(), 2

class MIDINoteListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_MIDITempoEventListSocket"
    bl_label = "MIDI Tempo Event List Socket"
    dataType = "MIDI Tempo Event List"
    baseType = MIDITempoEventSocket
    drawColor = (0.6, 0.75, 0.45, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "[tempoEvent.copy() for tempoEvent in value]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, MIDITempoEvent) for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
