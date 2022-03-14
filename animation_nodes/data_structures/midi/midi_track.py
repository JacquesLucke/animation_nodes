from typing import List
from . midi_note import MIDINote
from dataclasses import dataclass, field

@dataclass
class MIDITrack:
    name: str = ""
    index: int = 0
    notes: List[MIDINote] = field(default_factory = list)

    def evaluate(self, time, channel, noteNumber, 
        attackTime, attackInterpolation, decayTime, decayInterpolation, sustainLevel, 
        releaseTime, releaseInterpolation, velocitySensitivity):

        noteFilter = lambda note: note.channel == channel and note.noteNumber == noteNumber
        timeFilter = lambda note: note.timeOff + releaseTime >= time >= note.timeOn
        filteredNotes = filter(lambda note: noteFilter(note) and timeFilter(note), self.notes)
        arguments = (time, attackTime, attackInterpolation, decayTime, decayInterpolation, 
            sustainLevel, releaseTime, releaseInterpolation, velocitySensitivity)
        return max((note.evaluate(*arguments) for note in filteredNotes), default = 0.0)

    def evaluateAll(self, time, channel, 
        attackTime, attackInterpolation, decayTime, decayInterpolation, sustainLevel,
        releaseTime, releaseInterpolation, velocitySensitivity):
        channelFilter = lambda note: note.channel == channel
        timeFilter = lambda note: note.timeOff + releaseTime >= time >= note.timeOn
        filteredNotes = list(filter(lambda note: channelFilter(note) and timeFilter(note), self.notes))
        arguments = (time, attackTime, attackInterpolation, decayTime, decayInterpolation, 
            sustainLevel, releaseTime, releaseInterpolation, velocitySensitivity)
        noteValues = []
        for i in range(128):
            filteredByNumberNotes = filter(lambda note: note.noteNumber == i, filteredNotes)
            value = max((note.evaluate(*arguments) for note in filteredByNumberNotes), default = 0.0)
            noteValues.append(value)
        return noteValues

    def copy(self):
        return MIDITrack(self.name, self.index, [n.copy() for n in self.notes])
