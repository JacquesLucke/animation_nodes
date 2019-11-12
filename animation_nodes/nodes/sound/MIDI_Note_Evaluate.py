import bpy
from ... base_types import AnimationNode, ListTypeSelectorSocket, VectorizedSocket
from ... data_structures import DoubleList

def FilterByNote(self, notesIn, number, time, attack_time, attack_interpolation, release_time, release_interpolation):
    if self.useNumberList:
        # Filter by note list
        # notesTmp = unique note founded in time and from list number (list(set()) mean distinct)
        notesInTime = [note for note in notesIn for n in number if (time >= note.time_on and time <= (note.time_off + release_time) and note.number == n)]
        notesTmp = list(set([note.number for note in notesInTime]))
        # If no note founded return a liste of 0.0
        if len(notesTmp) == 0:
            numberTmp = [0.0 for n in number]
            return DoubleList.fromValues(numberTmp)
        # Else fill numberTmp one number by one
        numberTmp = []
        for n in number:
            # Extract noteTested just for note number n
            noteTested = [notenum for notenum in notesTmp if notenum == n]
            if len(noteTested) != 0:
                # if played
                noteplayed = [note for note in notesInTime if note.number == n]
                noteplayed = noteplayed[0]
                if time >= (noteplayed.time_on + attack_time) and time <= noteplayed.time_off:
                    numberTmp.append(1.0)  # Play full
                elif time >= noteplayed.time_on and time <= (noteplayed.time_on + attack_time):
                    value = (time - noteplayed.time_on) / attack_time
                    value = attack_interpolation(value)
                    numberTmp.append(value)  # Play intermediate start
                elif time >= noteplayed.time_off and time <= (noteplayed.time_off + release_time):
                    value = 1-((time - noteplayed.time_off) / release_time)
                    value = release_interpolation(value)
                    numberTmp.append(value)  # Play intermediate end
            else:
                # if not played
                numberTmp.append(0.0)  # Play nothing
        return DoubleList.fromValues(numberTmp)
    else:
        # Filter by note
        notesTmp = [note for note in notesIn if (note.number == number and time >= note.time_on and time <= note.time_off)]
        return (len(notesTmp) != 0) * 1.0

class MidiNoteEvaluateNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiNoteEvaluateNode"
    bl_label = "MIDI Note Evaluate"
    bl_width_default = 180

    useNumberList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("MIDINoteList", "Notes", "notesIn")
        self.newInput("Integer", "Channel", "channel")
        self.newInput(VectorizedSocket("Integer", "useNumberList",
            ("number", "number"), ("numbers", "numbers")))
        self.newInput("Float", "Time", "time")
        self.newInput("Float", "Attack Time", "attack_time")
        self.newInput("Interpolation", "Attack Interpolation", "attack_interpolation")
        self.newInput("Float", "Release Time", "release_time")
        self.newInput("Interpolation", "Release Interpolation", "release_interpolation")
        self.newOutput(VectorizedSocket("Float", "useNumberList",
            ("noteplayed", "note played"), ("notesplayed", "notes played")))

    def execute(self, notesIn, channel, number, time, attack_time, attack_interpolation, release_time, release_interpolation):
        notesChannel = [note for note in notesIn if note.channel == channel]
        return FilterByNote(self, notesChannel, number, time, attack_time, attack_interpolation, release_time, release_interpolation)
