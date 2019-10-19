import bpy
from bpy.props import *
from ... sockets.info import isBase, toBaseDataType
from ... events import propertyChanged
from ... base_types import AnimationNode, ListTypeSelectorSocket, VectorizedSocket
from ... data_structures import DoubleList

class MidiNoteEvaluate2Node(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiNoteEvaluate2Node"
    bl_label = "MIDI Note Evaluate 2"
    bl_width_default = 180

    usefilterByChannel: BoolProperty(name = "Channel Filter", default = False,
        update = AnimationNode.refresh)
    usefilterByNote: BoolProperty(name = "Note Filter", default = False,
        update = AnimationNode.refresh)

    useList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("MIDINoteList", "Notes", "notesIn")
        if self.usefilterByChannel:
            self.newInput("Integer", "Channel", "channel")
        if self.usefilterByNote:
            # self.newInput("Integer", "Note", "number")
            self.newInput(VectorizedSocket("Integer", "useList",
                ("number", "number"), ("numbers", "numbers")))
        # self.newOutput("Float", "Note(s) Played", "notesplayed")
        self.newInput("Float", "Time", "time")
        self.newOutput(VectorizedSocket("Float", "useList",
            ("noteplayed", "note played"), ("notesplayed", "notes played")))

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

    def execute_FilterByChannelAndNote(self, notesIn, channel, number, time):
        notesTmp = [note for note in notesIn if note.channel == channel]
        if self.useList:
            # Filter by note list
            notesTmp = list(set([note.number for note in notesTmp for n in number if (time >= note.time_on and time <= note.time_off and note.number == n)]))
            numberTmp = []
            for n in number:
                tmp = [notenum for notenum in notesTmp if notenum == n]
                if len(tmp) != 0:
                    numberTmp.append(1.0)
                else:
                    numberTmp.append(0.0)
            return DoubleList.fromValues(numberTmp)
        else:
            # Filter by note
            notesTmp = [note for note in notesTmp if (note.number == number and time >= note.time_on and time <= note.time_off)]
            return (len(notesTmp) != 0) * 1.0

    def execute_FilterByNote(self, notesIn, number, time):
        if self.useList:
            # Filter by note list
            # notesTmp = unique note founded in time and from list number
            notesTmp = list(set([note.number for note in notesIn for n in number if (time >= note.time_on and time <= note.time_off and note.number == n)]))
            numberTmp = []
            for n in number:
                tmp = [notenum for notenum in notesTmp if notenum == n]
                if len(tmp) != 0:
                    numberTmp.append(1.0)
                else:
                    numberTmp.append(0.0)
            return DoubleList.fromValues(numberTmp)
        else:
            # Filter by note
            notesTmp = [note for note in notesIn if (note.number == number and time >= note.time_on and time <= note.time_off)]
            return (len(notesTmp) != 0) * 1.0

    def execute_FilterByChannel(self, notesIn, channel, time):
        notesTmp = [note for note in notesIn if note.channel == channel]
        return (len(notesTmp) != 0) * 1.0

    def execute_NoFilter(self, notesIn, time):
        notesTmp = [note for note in notesIn if (time >= note.time_on and time <= note.time_off)]
        return (len(notesTmp) != 0) * 1.0
