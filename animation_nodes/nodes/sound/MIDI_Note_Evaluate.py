import bpy
from ... data_structures import DoubleList
from ... base_types import AnimationNode, ListTypeSelectorSocket, VectorizedSocket

def filterByNote(self, notesIn, noteNumber, time, attackTime, attackInterpolation, releaseTime, releaseInterpolation):
    if self.useNoteNumberList:
        notesInTime = [note for note in notesIn for n in noteNumber if
            (time >= note.timeOn and time <= (note.timeOff + releaseTime) and note.noteNumber == n)]
        notesTmp = list(set([note.noteNumber for note in notesInTime]))
        if len(notesTmp) == 0:
            numberTmp = [0.0 for n in noteNumber]
            return DoubleList.fromValues(numberTmp)
        numberTmp = []
        for n in noteNumber:
            noteTested = [notenum for notenum in notesTmp if notenum == n]
            if len(noteTested) != 0:
                notePlayed = [note for note in notesInTime if note.noteNumber == n]
                notePlayed = notePlayed[0]
                if time >= (notePlayed.timeOn + attackTime) and time <= notePlayed.timeOff:
                    numberTmp.append(1.0)
                elif time >= notePlayed.timeOn and time <= (notePlayed.timeOn + attackTime):
                    value = (time - notePlayed.timeOn) / attackTime
                    value = attackInterpolation(value)
                    numberTmp.append(value)
                elif time >= notePlayed.timeOff and time <= (notePlayed.timeOff + releaseTime):
                    value = 1-((time - notePlayed.timeOff) / releaseTime)
                    value = releaseInterpolation(value)
                    numberTmp.append(value)
            else:
                numberTmp.append(0.0)
        return DoubleList.fromValues(numberTmp)
    else:
        notesTmp = [note for note in notesIn if
            (note.noteNumber == noteNumber and time >= note.timeOn and time <= note.timeOff)]
        return (len(notesTmp) != 0) * 1.0

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
        notesChannel = [note for note in notesIn if note.channel == channel]
        return filterByNote(self, notesChannel, noteNumber, time, attackTime,
            attackInterpolation, releaseTime, releaseInterpolation)
