import bpy
from bpy.props import *
from ... sockets.info import isBase, toBaseDataType
from ... events import propertyChanged
from ... base_types import AnimationNode, ListTypeSelectorSocket

class MidiNoteNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiNoteInfoNode"
    bl_label = "MIDI Note Info"
    bl_width_default = 180

    def create(self):
        self.newInput("MIDINote", "Note", "note")
        self.newOutput("Integer", "Channel", "channel")
        self.newOutput("Integer", "Number", "number")
        self.newOutput("Integer", "Time On", "timeon")
        self.newOutput("Integer", "Time Off", "timeoff")
        self.newOutput("Integer", "Velocity", "velocity")

    def execute(self, note):
        if note is None: return None

        return note.channel, note.note, note.time_on, note.time_off, note.velocity
