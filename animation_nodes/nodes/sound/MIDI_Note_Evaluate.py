import bpy
from ... data_structures import DoubleList
from ... base_types import AnimationNode, ListTypeSelectorSocket, VectorizedSocket

class MidiNoteEvaluateNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiNoteEvaluateNode"
    bl_label = "MIDI Note Evaluate"
    bl_width_default = 180

    useNoteNumberList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("MIDINoteList", "Notes", "notesIn")
        self.newInput("Integer", "Channel", "channel")
        self.newInput(VectorizedSocket("Integer", "useNoteNumberList",
            ("noteNumber", "noteNumber"), ("numbers", "numbers")))
        self.newInput("Float", "Time", "time")
        self.newInput("Float", "Attack Time", "attackTime")
        self.newInput("Interpolation", "Attack Interpolation", "attackInterpolation")
        self.newInput("Float", "Release Time", "releaseTime")
        self.newInput("Interpolation", "Release Interpolation", "releaseInterpolation")
        self.newOutput(VectorizedSocket("Float", "useNoteNumberList",
            ("notePlayed", "note played"), ("notesplayed", "notes played")))

    def execute(self, notesIn, channel, noteNumber, time, attackTime,
        attackInterpolation, releaseTime, releaseInterpolation):

        if self.useNoteNumberList:
            notesFiltered = [note for note in notesIn if note.channel == channel and
                time >= note.timeOn and time <= note.timeOff + releaseTime and
                note.noteNumber in noteNumber]
        else:
            notesFiltered = [note for note in notesIn if note.channel == channel and
                time >= note.timeOn and time <= note.timeOff + releaseTime and
                note.noteNumber == noteNumber]

        def noteP(N):
            noteTested = [note for note in notesFiltered if note.noteNumber == N]
            if len(noteTested) == 0:
                return 0.0
            noteTested = noteTested[0]
            if time >= (noteTested.timeOn + attackTime) and time <= noteTested.timeOff:
                return 1.0
            elif time >= noteTested.timeOn and time <= (noteTested.timeOn + attackTime):
                value = (time - noteTested.timeOn) / attackTime
                value = attackInterpolation(value)
                return value
            elif time >= noteTested.timeOff and time <= (noteTested.timeOff + releaseTime):
                value = 1-((time - noteTested.timeOff) / releaseTime)
                value = releaseInterpolation(value)
                return value
            return 0.0

        if self.useNoteNumberList:
            return DoubleList.fromValues([noteP(N) for N in noteNumber])
        else:
            return noteP(noteNumber)
