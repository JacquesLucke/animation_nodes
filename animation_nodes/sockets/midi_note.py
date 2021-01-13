import bpy
from .. data_structures import MIDINote
from .. base_types import AnimationNodeSocket, PythonListSocket

class MIDINoteSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MIDINoteSocket"
    bl_label = "MIDI Note Socket"
    dataType = "MIDI Note"
    drawColor = (0.45, 0.6, 0.75, 1)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return MIDINote()

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, MIDINote):
            return value, 0
        return cls.getDefaultValue(), 2

class MIDINoteListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_MIDINoteListSocket"
    bl_label = "MIDI Note List Socket"
    dataType = "MIDI Note List"
    baseType = MIDINoteSocket
    drawColor = (0.45, 0.6, 0.75, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "[note.copy() for note in value]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, MIDINote) for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
