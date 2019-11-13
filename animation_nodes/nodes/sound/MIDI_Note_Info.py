import bpy
from ... base_types import AnimationNode, ListTypeSelectorSocket, VectorizedSocket

class MidiNoteNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiNoteInfoNode"
    bl_label = "MIDI Note Info"
    bl_width_default = 180

    useNotesList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("MIDINote", "useNotesList",
            ("note", "note"), ("notes", "notes")))
        self.newOutput(VectorizedSocket("Integer", "useNotesList",
            ("Channel", "channel"), ("Channels", "channels")))
        self.newOutput(VectorizedSocket("Integer", "useNotesList",
            ("note", "note"), ("notes", "notes")))
        self.newOutput(VectorizedSocket("Float", "useNotesList",
            ("Time On", "timeon"), ("Times On", "timeson")))
        self.newOutput(VectorizedSocket("Float", "useNotesList",
            ("Time Off", "timeoff"), ("Times Off", "timesoff")))
        self.newOutput(VectorizedSocket("Float", "useNotesList",
            ("Velocity", "velocity"), ("Velocities", "velocities")))

    def execute(self, note):
        if self.useNotesList:
            return [note.channel for note in note], [note.noteNumber for note in note], [note.timeOn for note in note], [note.timeOff for note in note], [note.velocity for note in note]
        else:
            if note is None:
                return 0,0,0.0,0.0,0.0
            else:
                return note.channel, note.noteNumber, note.timeOn, note.timeOff, note.velocity
