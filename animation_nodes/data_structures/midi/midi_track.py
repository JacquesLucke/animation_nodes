from typing import List
from . midi_note import MIDINote
from dataclasses import dataclass, field

@dataclass
class MIDITrack:
    name: str = ""
    index: int = 0
    notes: List[MIDINote] = field(default_factory = list)

    def evaluate(self, time, channel, noteNumber, attackTime, attackInterpolation, releaseTime, releaseInterpolation):
        noteFilter = lambda note: note.channel == channel and note.noteNumber == noteNumber
        timeFilter = lambda note: note.timeOff + releaseTime >= time >= note.timeOn
        filteredNotes = filter(lambda note: noteFilter(note) and timeFilter(note), self.notes)
        arguments = (time, attackTime, attackInterpolation, releaseTime, releaseInterpolation)
        return max((note.evaluate(*arguments) for note in filteredNotes), default = 0)

    def evaluateAll(self, time, channel, attackTime, attackInterpolation, releaseTime, releaseInterpolation):
        channelFilter = lambda note: note.channel == channel
        timeFilter = lambda note: note.timeOff + releaseTime >= time >= note.timeOn
        filteredNotes = list(filter(lambda note: channelFilter(note) and timeFilter(note), self.notes))
        arguments = (time, attackTime, attackInterpolation, releaseTime, releaseInterpolation)
        noteValues = []
        for i in range(128):
            filteredByNumberNotes = filter(lambda note: note.noteNumber == i, filteredNotes)
            value = max((note.evaluate(*arguments) for note in filteredByNumberNotes), default = 0)
            noteValues.append(value)
        return noteValues

    def copy(self):
        return MIDITrack([n.copy() for n in self.notes], self.name, self.index)
