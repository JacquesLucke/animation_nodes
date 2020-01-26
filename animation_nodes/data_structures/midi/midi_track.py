from . midi_note import MIDINote

class MIDITrack:
    def __init__(self, trackIndex, trackName):
        self.index = trackIndex
        self.name = trackName
        self.notes = []

    def addNote(self, note):
        self.notes.append(note)
