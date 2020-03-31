from . midi_note import midiNote
from ... data_structures import DoubleList

class midiTrack:
    def __init__(self, trackIndex, trackName):
        self.index = trackIndex
        self.name = trackName
        self.notes = []

    def addNote(self, note):
        self.notes.append(note)

    def evaluate(self, channel, useNoteNumberList, noteNumber, time, attackTime,
           attackInterpolation, releaseTime, releaseInterpolation):

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

        if useNoteNumberList:
            notesFiltered = [note for note in self.notes if note.channel == channel and
                time >= note.timeOn and time <= note.timeOff + releaseTime and
                note.noteNumber in noteNumber]
            return DoubleList.fromValues([noteP(N) for N in noteNumber])
        else:
            notesFiltered = [note for note in self.notes if note.channel == channel and
                time >= note.timeOn and time <= note.timeOff + releaseTime and
                note.noteNumber == noteNumber]
            return noteP(noteNumber)

