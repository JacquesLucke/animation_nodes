import bpy
from ... base_types import AnimationNode, VectorizedSocket

class MIDINoteInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MIDINoteInfoNode"
    bl_label = "MIDI Note Info"

    useNotesList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("MIDI Note", "useNotesList",
            ("note", "note"), ("notes", "notes")))
        self.newOutput(VectorizedSocket("Integer", "useNotesList",
            ("Channel", "channel"), ("Channels", "channels")))
        self.newOutput(VectorizedSocket("Integer", "useNotesList",
            ("Note Number", "noteNumber"), ("Note Numbers", "noteNumbers")))
        self.newOutput(VectorizedSocket("Float", "useNotesList",
            ("Time On", "timeOn"), ("Times On", "timesOn")))
        self.newOutput(VectorizedSocket("Float", "useNotesList",
            ("Time Off", "timeOff"), ("Times Off", "timesOff")))
        self.newOutput(VectorizedSocket("Float", "useNotesList",
            ("Velocity", "velocity"), ("Velocities", "velocities")))

    def getExecutionCode(self, required):
        if not self.useNotesList:
            if "channel" in required:
                yield "channel = note.channel"
            if "noteNumber" in required:
                yield "noteNumber = note.noteNumber"
            if "timeOn" in required:
                yield "timeOn = note.timeOn"
            if "timeOff" in required:
                yield "timeOff = note.timeOff"
            if "velocity" in required:
                yield "velocity = note.velocity"
        else:
            if "channels" in required:
                yield "channels = LongList.fromValues(note.channel for note in notes)"
            if "noteNumbers" in required:
                yield "noteNumbers = LongList.fromValues(note.noteNumber for note in notes)"
            if "timesOn" in required:
                yield "timesOn = DoubleList.fromValues(note.timeOn for note in notes)"
            if "timesOff" in required:
                yield "timesOff = DoubleList.fromValues(note.timeOff for note in notes)"
            if "velocities" in required:
                yield "velocities = DoubleList.fromValues(note.velocity for note in notes)"
