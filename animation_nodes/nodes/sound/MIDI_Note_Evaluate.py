import bpy
from bpy.props import *
from ... sockets.info import isBase, toBaseDataType
from ... events import propertyChanged
from ... base_types import AnimationNode, ListTypeSelectorSocket

class MidiNoteEvaluateNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiNoteEvaluateNode"
    bl_label = "MIDI Note Evaluate"
    bl_width_default = 180

    def create(self):
        self.newInput("MIDINoteList", "Notes", "notesIn")
        self.newInput("Float", "Time", "time")
        self.newOutput("Float", "Note(s) Played", "notesplayed")

    def execute(self, notesIn, time):
        notesTmp = [note for note in notesIn if (time >= note.time_on and time <= note.time_off)]
        return (len(notesTmp) != 0) * 1.0
