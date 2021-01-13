import os
from functools import lru_cache
from dataclasses import dataclass
from .. libs.midiparser.parser import MidiFile
from .. data_structures import MIDITrack, MIDINote
from .. libs.midiparser.events import (
    TempoEvent,
    NoteOnEvent,
    NoteOffEvent,
    TrackNameEvent,
)

def readMIDIFile(path):
    lastModification = os.stat(path).st_mtime
    return readMIDIFileCached(path, lastModification)

readMIDIFile.cache_clear = lambda: readMIDIFileCached.cache_clear()

# Notes:
# - If no tempo event was found, a default tempo event of tempo 500,000 will be
#   inserted at time 0. The same applies of no tempo event happens at time 0,
#   this is done to guarantee any channel event will be preceded by a tempo event.
# - MIDI format 1 is a special format where the first track only contains tempo
#   events that represents the tempo map of all other tracks. So the code is
#   written accordingly.

@dataclass
class TempoEventRecord:
    time: int
    tempo: int = 500_000

class TempoMap:
    def __init__(self, midiFormat, ppqn, tempoTracks):
        self.ppqn = ppqn
        self.midiFormat = midiFormat
        self.tempoTracks = tempoTracks

    @classmethod
    def fromFile(cls, midiFile):
        tempoTracks = []
        fileTracks = midiFile.tracks if midiFile.midiFormat != 1 else midiFile.tracks[0:1]
        for track in fileTracks:
            time = 0
            tempoEvents = []
            for event in track.events:
                time += event.deltaTime
                if not isinstance(event, TempoEvent): continue
                tempoEvents.append(TempoEventRecord(time, event.tempo))
            if len(tempoEvents) == 0 or tempoEvents[0].tempo != 0:
                tempoEvents.append(TempoEventRecord(0))
            tempoTracks.append(tempoEvents)
        return TempoMap(midiFile.midiFormat, midiFile.ppqn, tempoTracks)

    def ticksToSeconds(self, trackIndex, timeInTicks, ticks):
        trackIndex = trackIndex if self.midiFormat != 1 else 0
        tempoEvents = self.tempoTracks[trackIndex]
        filteredEvents = filter(lambda e: e.time <= timeInTicks, reversed(tempoEvents))
        tempo = next(filteredEvents).tempo
        microSecondsPerTick = tempo / self.ppqn
        secondsPerTick = microSecondsPerTick / 1_000_000
        seconds = ticks * secondsPerTick
        return seconds

# Notes:
# - It is possible for multiple consecutive Note On Events to happen on the same
#   channel and note number. The `numberOfNotes` member in NoteOnRecord represents
#   the number of such consecutive events. Note Off Events decrement that number
#   and are only considered when that number becomes 1.
# - The MIDI parser takes care of running status Note On Events with zero velocity
#   so the code needed check for that.

@dataclass
class NoteOnRecord:
    time: float
    velocity: float
    numberOfNotes: int = 1

class TrackState:
    def __init__(self):
        self.timeInTicks = 0
        self.timeInSeconds = 0
        self.noteOnTable = dict()

    def updateTime(self, trackIndex, tempoMap, deltaTime):
        self.timeInTicks += deltaTime
        self.timeInSeconds += tempoMap.ticksToSeconds(trackIndex, self.timeInTicks, deltaTime)

    def recordNoteOn(self, event):
        key = (event.channel, event.note)
        if key in self.noteOnTable:
            self.noteOnTable[key].numberOfNotes += 1
        else:
            self.noteOnTable[key] = NoteOnRecord(self.timeInSeconds, event.velocity / 127)

    def getCorrespondingNoteOnRecord(self, event):
        key = (event.channel, event.note)
        noteOnRecord = self.noteOnTable[key]
        if noteOnRecord.numberOfNotes == 1:
            del self.noteOnTable[key]
            return noteOnRecord
        else:
            noteOnRecord.numberOfNotes -= 1
            return None

@lru_cache(maxsize = 32)
def readMIDIFileCached(path, lastModification):
    midiFile = MidiFile.fromFile(path)
    tempoMap = TempoMap.fromFile(midiFile)
    tracks = []
    fileTracks = midiFile.tracks if midiFile.midiFormat != 1 else midiFile.tracks[1:]
    for trackIndex, track in enumerate(fileTracks):
        notes = []
        trackName = ""
        trackState = TrackState()
        for event in track.events:
            trackState.updateTime(trackIndex, tempoMap, event.deltaTime)
            if isinstance(event, TrackNameEvent):
                trackName = event.name
            elif isinstance(event, NoteOnEvent):
                trackState.recordNoteOn(event)
            elif isinstance(event, NoteOffEvent):
                noteOnRecord = trackState.getCorrespondingNoteOnRecord(event)
                if noteOnRecord is None: continue
                startTime = noteOnRecord.time
                velocity = noteOnRecord.velocity
                endTime = trackState.timeInSeconds
                notes.append(MIDINote(event.channel, event.note, startTime, endTime, velocity))
        tracks.append(MIDITrack(trackName, trackIndex, notes))
    return tracks
