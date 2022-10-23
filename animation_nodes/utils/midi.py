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
#   inserted at time 0. The same applies if no tempo event happens at time 0,
#   this is done to guarantee any channel event will be preceded by a tempo event.
# - MIDI format 1 is a special format where the first track only contains tempo
#   events that represents the tempo map of all other tracks. So the code is
#   written accordingly.

@dataclass
class TempoEventRecord:
    timeInTicks: int
    timeInQuarterNotes: float
    timeInSeconds: int
    tempo: int

class TempoMap:
    def __init__(self, midiFile):
        self.ppqn = midiFile.ppqn
        self.midiFormat = midiFile.midiFormat
        self.computeTempoTracks(midiFile)

    def computeTempoTracks(self, midiFile):
        tracks = midiFile.tracks
        if midiFile.midiFormat == 1: tracks = tracks[0:1]
        self.tempoTracks = [[] * len(tracks)]
        for trackIndex, track in enumerate(tracks):
            timeInTicks = 0
            timeInQuarterNotes = 0
            timeInSeconds = 0
            tempoEvents = self.tempoTracks[trackIndex]
            for event in track.events:
                timeInTicks += event.deltaTime
                timeInQuarterNotes += self.timeInTicksToQuarterNotes(event.deltaTime)
                timeInSeconds = self.timeInTicksToSeconds(trackIndex, timeInTicks)
                if not isinstance(event, TempoEvent): continue
                tempoEvents.append(TempoEventRecord(timeInTicks, timeInSeconds, event.tempo))
        self.TempoEvents = tempoEvents

    def timeInTicksToSeconds(self, trackIndex, timeInTicks):
        trackIndex = trackIndex if self.midiFormat != 1 else 0
        tempoEvents = self.tempoTracks[trackIndex]
        matchFunction = lambda event: event.timeInTicks <= timeInTicks
        matchedEvents = filter(matchFunction, reversed(tempoEvents))
        tempoEvent = next(matchedEvents, TempoEventRecord(0, 0, 500_000))
        microSecondsPerTick = tempoEvent.tempo / self.ppqn
        secondsPerTick = microSecondsPerTick / 1_000_000
        elapsedSeconds = (timeInTicks - tempoEvent.timeInTicks) * secondsPerTick
        return tempoEvent.timeInSeconds + elapsedSeconds
    
    def timeInTicksToQuarterNotes(self, timeInTicks):
        return timeInTicks / self.ppqn

# Notes:
# - It is possible for multiple consecutive Note On Events to happen on the same
#   channel and note number. The `numberOfNotes` member in NoteOnRecord represents
#   the number of such consecutive events. Note Off Events decrement that number
#   and are only considered when that number becomes 1.
# - The MIDI parser takes care of running-status Note On Events with zero velocity
#   so the code needn't check for that.

@dataclass
class NoteOnRecord:
    time_s: float
    time_ticks: int
    velocity: float
    numberOfNotes: int = 1

class TrackState:
    def __init__(self):
        self.timeInTicks = 0
        self.timeInSeconds = 0
        self.noteOnTable = dict()

    def updateTime(self, trackIndex, tempoMap, deltaTime):
        self.timeInTicks += deltaTime
        self.timeInSeconds = tempoMap.timeInTicksToSeconds(trackIndex, self.timeInTicks)

    def recordNoteOn(self, event):
        key = (event.channel, event.note)
        if key in self.noteOnTable:
            self.noteOnTable[key].numberOfNotes += 1
        else:
            self.noteOnTable[key] = NoteOnRecord(self.timeInSeconds, self.timeInTicks, event.velocity / 127)

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
    tempoMap = TempoMap(midiFile)
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
                startTime_s = noteOnRecord.time_s
                startTime_qn = noteOnRecord.time_ticks / midiFile.ppqn
                velocity = noteOnRecord.velocity
                endTime_s = trackState.timeInSeconds
                endTime_qn = trackState.timeInTicks / midiFile.ppqn
                notes.append(MIDINote(event.channel, event.note,
                                      startTime_s, endTime_s,
                                      startTime_qn, endTime_qn, velocity))
        tracks.append(MIDITrack(trackName, trackIndex, notes))
        #tempos = tempoMap.TempoEvents
    return tracks#, tempos
