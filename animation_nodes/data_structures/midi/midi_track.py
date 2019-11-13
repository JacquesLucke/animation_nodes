from .midi_note import MIDINote

class MIDITrack:
    def __init__(self, trackIndex, trackName):
        self.index = trackIndex
        self.name = trackName
        self.notes = []

    def add_note(self, channel, noteNumber, timeOn, timeOff, velocity):
        self.notes.append(MIDINote(channel, noteNumber, timeOn, timeOff, velocity))
