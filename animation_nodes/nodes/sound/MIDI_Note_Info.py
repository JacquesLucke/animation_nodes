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
        self.newInput("MIDINote", "Note", "noteObj")
        self.newOutput("Integer", "Channel", "channel")
        self.newOutput("Integer", "Note", "number")
        self.newOutput("Float", "Time On", "timeon")
        self.newOutput("Float", "Time Off", "timeoff")
        self.newOutput("Float", "Velocity", "velocity")

    def execute(self, noteObj):
        if noteObj is None: return None

        return noteObj.channel, noteObj.number, noteObj.time_on, noteObj.time_off, noteObj.velocity
