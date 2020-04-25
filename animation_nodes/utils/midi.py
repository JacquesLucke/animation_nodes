from ..libs.midiparser.parser import MidiFile
from ..libs.midiparser.events import NoteOnEvent,NoteOffEvent,TrackNameEvent,TempoEvent,SysExEvent
from ..data_structures.midi.midi_track import midiTrack
from ..data_structures.midi.midi_note import midiNote

class Tempo:
    def __init__(self, trackToAnalyze, ppq):
        self.tempoMap = [[]]
        self.ppq = ppq
        timeInTicksCumul = 0
        ticksPrevious = 0
        tempoPrevious = 0
        tempoCount = 0
        secCumul = 0
        for event in trackToAnalyze.events:
            timeInTicksCumul += event.deltaTime
            if isinstance(event, TempoEvent):
                if event.tempo != 0:
                    tempoCount += 1
                    row = []
                    tempo = event.tempo
                    deltaTicks = timeInTicksCumul - ticksPrevious
                    secPerTicks = (tempoPrevious / ppq) / 1000000
                    sec = deltaTicks * secPerTicks
                    secCumul += sec
                    row.append(timeInTicksCumul)
                    row.append(tempo)
                    row.append(secCumul)
                    self.tempoMap.append(row)
                    ticksPrevious = timeInTicksCumul
                    tempoPrevious = tempo
        if tempoCount == 0:
            row = []
            row.append(0)
            row.append(500000)
            row.append(0)
            self.tempoMap.append(row)

    def getRealtime(self, ticksCumul):
        if ticksCumul == 0:
            return 0
        for row in self.tempoMap:
            if row:
                if row[0] > ticksCumul:
                    break
                else:
                    foundedRow = row
        # seconds = foundedRow[6]
        seconds = foundedRow[2]
        delta = ticksCumul - foundedRow[0]
        secPerTicks = (foundedRow[1] / self.ppq) / 1000000
        seconds += delta * secPerTicks
        return seconds


def MidiParseFile(filemid):

    # print("start parse file")
    midi = MidiFile.fromFile(filemid)
    # print(midi)
    newTracks = []
    for trackIndex, track in enumerate(midi.tracks):
        if midi.midiFormat == 2:
            timeMap = Tempo(track, midi.ppqn)
        else:
            timeMap = Tempo(midi.tracks[0], midi.ppqn)

        newTrack = midiTrack(trackIndex, "undefined")
        timeInTicksCumul = 0
        lastNoteOn = {}
        for event in track.events:

            if isinstance(event, SysExEvent): continue

            msgType = 'not evalued'
            timeInTicksCumul += event.deltaTime
            # if msg.is_meta: continue

            if isinstance(event, TrackNameEvent):
                newTrack.name = event.name
                continue

            if isinstance(event, NoteOnEvent):
                if event.velocity == 0:
                    msgType = 'note_off'
                else:
                    msgType = 'note_on'
            if isinstance(event, NoteOffEvent):
                msgType = 'note_off'

            if msgType == 'note_on':
                currentTime = timeMap.getRealtime(timeInTicksCumul)
                key = str(event.channel) + "/" + str(event.note)
                lastNoteOn[key] = [currentTime, event.velocity / 127]
                # lastNoteOn[event.note] = [event.channel, currentTime, event.velocity / 127]
            if msgType == 'note_off':
                currentTime = timeMap.getRealtime(timeInTicksCumul)
                key = str(event.channel) + "/" + str(event.note)
                if key in lastNoteOn:
                    # print(key, event.channel, event.note, lastNoteOn[key][0], currentTime, lastNoteOn[key][1])
                    newTrack.addNote(midiNote(event.channel, event.note, lastNoteOn[key][0], currentTime, lastNoteOn[key][1]))
                    # newTrack.addNote(midiNote(event.channel, event.note, lastNoteOn[event.note][1], currentTime, lastNoteOn[event.note][2]))
                    lastNoteOn.pop(key, None)
                else:
                    print("no noteOn for ", event.channel, event.note)
        newTracks.append(newTrack)
        # print("+++++++++++++++++++")
        # print(midi.midiFormat, newTrack.index, newTrack.name)
        # print("-------------------")
    return newTracks
