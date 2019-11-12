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
            return [note.channel for note in note], [note.number for note in note], [note.time_on for note in note], [note.time_off for note in note], [note.velocity for note in note]
        else:
            if note is None:
                return 0,0,0.0,0.0,0.0
            else:
                return note.channel, note.number, note.time_on, note.time_off, note.velocity
