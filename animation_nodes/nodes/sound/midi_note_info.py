import bpy
from ... base_types import AnimationNode, VectorizedSocket

class MIDINoteInfoNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_MIDINoteInfoNode"
    bl_label = "MIDI Note Info"

    useNotesList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("MIDI Note", "useNotesList",
            ("Note", "note"), ("Notes", "notes")))
        self.newOutput(VectorizedSocket("Integer", "useNotesList",
            ("Channel", "channel"), ("Channels", "channels")))
        self.newOutput(VectorizedSocket("Integer", "useNotesList",
            ("Note Number", "noteNumber"), ("Note Numbers", "noteNumbers")))
        self.newOutput(VectorizedSocket("Float", "useNotesList",
            ("Time On [s]", "timeOn_s"), ("Times On [s]", "timesOn_s")))
        self.newOutput(VectorizedSocket("Float", "useNotesList",
            ("Time Off [s]", "timeOff_s"), ("Times Off [s]", "timesOff_s")))
        self.newOutput(VectorizedSocket("Float", "useNotesList",
            ("Time On [1/4 note]", "timeOn_qn"), ("Times On [1/4] note", "timesOn_qn")))
        self.newOutput(VectorizedSocket("Float", "useNotesList",
            ("Time Off [1/4 note]", "timeOff_qn"), ("Times Off [1/4] note", "timesOff_qn")))
        self.newOutput(VectorizedSocket("Float", "useNotesList",
            ("Velocity", "velocity"), ("Velocities", "velocities")))

    def getExecutionCode(self, required):
        if not self.useNotesList:
            if "channel" in required:
                yield "channel = note.channel"
            if "noteNumber" in required:
                yield "noteNumber = note.noteNumber"
            if "timeOn_s" in required:
                yield "timeOn_s = note.timeOn_s"
            if "timeOff_s" in required:
                yield "timeOff_s = note.timeOff_s"
            if "timeOn_qn" in required:
                yield "timeOn_qn = note.timeOn_qn"
            if "timeOff_qn" in required:
                yield "timeOff_qn = note.timeOff_qn"
            if "velocity" in required:
                yield "velocity = note.velocity"
        else:
            if "channels" in required:
                yield "channels = LongList.fromValues(note.channel for note in notes)"
            if "noteNumbers" in required:
                yield "noteNumbers = LongList.fromValues(note.noteNumber for note in notes)"
            if "timesOn_s" in required:
                yield "timesOn_s = DoubleList.fromValues(note.timeOn_s for note in notes)"
            if "timesOff_s" in required:
                yield "timesOff_s = DoubleList.fromValues(note.timeOff_s for note in notes)"
            if "timesOn_qn" in required:
                yield "timesOn_qn = DoubleList.fromValues(note.timeOn_qn for note in notes)"
            if "timesOff_qn" in required:
                yield "timesOff_qn = DoubleList.fromValues(note.timeOff_qn for note in notes)"
            if "velocities" in required:
                yield "velocities = DoubleList.fromValues(note.velocity for note in notes)"
