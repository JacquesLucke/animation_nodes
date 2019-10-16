import bpy
from bpy.props import *
from ... sockets.info import isBase, toBaseDataType
from ... events import propertyChanged
from ... base_types import AnimationNode, ListTypeSelectorSocket

class MidiNoteFilterNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiNoteFilterNode"
    bl_label = "MIDI Note Filter"
    bl_width_default = 180

    usefilterByChannel: BoolProperty(name = "Channel Filter", default = False,
        update = AnimationNode.refresh)
    usefilterByNote: BoolProperty(name = "Note Filter", default = False,
        update = AnimationNode.refresh)

    def create(self):
        self.newInput("MIDINoteList", "Notes", "notesIn")
        if self.usefilterByChannel:
            self.newInput("Integer", "Channel", "channel")
        if self.usefilterByNote:
            self.newInput("Integer", "Note", "number")
        self.newOutput("MIDINoteList", "Notes", "notesOut")

    def draw(self, layout):
        layout.prop(self, "usefilterByChannel")
        layout.prop(self, "usefilterByNote")

    def getExecutionFunctionName(self):
        if self.usefilterByChannel:
            if self.usefilterByNote:
                return "execute_FilterByChannelAndNote"
            else:
                return "execute_FilterByChannel"
        else:
            if self.usefilterByNote:
                return "execute_FilterByNote"
            else:
                return "execute_NoFilter"

    def execute_FilterByChannelAndNote(self, notesIn, channel, number):
        notesTmp = notesIn
        notesTmp = [note for note in notesTmp if note.channel == channel]
        notesTmp = [note for note in notesTmp if note.number == number]
        return notesTmp

    def execute_FilterByChannel(self, notesIn, channel):
        notesTmp = [note for note in notesIn if note.channel == channel]
        return notesTmp

    def execute_FilterByNote(self, notesIn, number):
        notesTmp = [note for note in notesIn if note.number == number]
        return notesTmp

    def execute_NoFilter(self, notesIn):
        return notesIn
