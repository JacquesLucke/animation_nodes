from mido import MidiFile
from ..data_structures.midi.midi_track import MIDITrack
from ..data_structures.midi.midi_note import MIDINote

class Tempo_Class:
    def __init__(self, trackToAnalyze, ppq):
        self.track = trackToAnalyze
        self.tempoMap = [[]]
        timeInTicksCumul = 0
        ticksPrevious = 0
        tempoPrevious = 0
        secCumul = 0
        for msg in self.track:
            timeInTicksCumul += msg.time
            if msg.type == 'set_tempo':
                if msg.tempo != 0:
                    row = []
                    tempo = msg.tempo
                    bpm = int(60000/(tempo/1000))
                    deltaTicks = timeInTicksCumul - ticksPrevious
                    secPerTicks = (tempoPrevious / ppq) / 1000000
                    sec = deltaTicks * secPerTicks
                    secCumul += sec
                    row.append(timeInTicksCumul)
                    row.append(tempo)
                    row.append(bpm)
                    row.append(deltaTicks)
                    row.append(secPerTicks)
                    row.append(sec)
                    row.append(secCumul)
                    self.tempoMap.append(row)
                    ticksPrevious = timeInTicksCumul
                    tempoPrevious = tempo

    def getRealtime(self, ticksCumul, ppq):
        if ticksCumul == 0:
            return 0
        for row in self.tempoMap:
            if row:
                if row[0] > ticksCumul:
                    break
                else:
                    foundedRow = row
        seconds = foundedRow[6]
        delta = ticksCumul - foundedRow[0]
        secPerTicks = (foundedRow[1] / ppq) / 1000000
        seconds += delta * secPerTicks
        return seconds

def MIDI_ParseFile(filemid):
    mid = MidiFile(filemid)
    if (mid.type == 2):
        raise RuntimeError("Only MIDI file type 0 or 1, type 2 is not yet supported")
    ppq = mid.ticks_per_beat
    timeMap = Tempo_Class(mid.tracks[0], ppq)
    tracks = []
    for trackIndex, curTracks in enumerate(mid.tracks):
        track = MIDITrack(trackIndex, curTracks.name)
        timeInTicksCumul = 0
        lastNoteOn = {}
        for msg in curTracks:
            if msg.type == "sysex": continue
            timeInTicksCumul += msg.time
            if msg.is_meta: continue
            if (msg.type == 'note_on') and (msg.velocity == 0):
                msgType = 'note_off'
            else:
                msgType = msg.type
            currentTime = timeMap.getRealtime(timeInTicksCumul, ppq)
            if msgType == 'note_on':
                lastNoteOn[msg.note] = [msg.channel, currentTime, msg.velocity / 127]
            if msgType == 'note_off':
                track.add_note(msg.channel, msg.note, lastNoteOn[msg.note][1], currentTime, lastNoteOn[msg.note][2])
        tracks.append(track)
    return tracks
