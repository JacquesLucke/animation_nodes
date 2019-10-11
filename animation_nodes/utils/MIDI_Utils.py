from mido import MidiFile

class Tempo_Class:

    # Channel initializations
    def __init__(self, track_to_analyze, ppq):
        """
        Initialization of the Class Tempo_MAP
        IN
            Track carrying the tempo instructions
        OUT
            The new object instanciated
            The tempo MAP is initialized with instanciation
        """
        # Parameters
        self.track = track_to_analyze       # track to analyze, always the track 0 for midi type 0 & 1
        self.tempo_map = [[]]               # 2D Matrice contain usefull data

        time_in_ticks_cumul = 0
        ticks_previous = 0
        tempo_previous = 0
        sec_cumul = 0

        # Generate the tempo MAP for the track
        for msg in self.track:
            time_in_ticks_cumul += msg.time
            if msg.type == 'set_tempo':
                if msg.tempo != 0:
                    row = []
                    tempo = msg.tempo
                    bpm = int(60000/(tempo/1000))
                    delta_ticks = time_in_ticks_cumul - ticks_previous
                    sec_per_ticks = (tempo_previous / ppq) / 1000000
                    sec = delta_ticks * sec_per_ticks
                    sec_cumul += sec

                    # memorize tempo MAP
                    row.append(time_in_ticks_cumul)     # 0
                    row.append(tempo)                   # 1
                    row.append(bpm)                     # 2
                    row.append(delta_ticks)             # 3
                    row.append(sec_per_ticks)           # 4
                    row.append(sec)                     # 5
                    row.append(sec_cumul)               # 6
                    self.tempo_map.append(row)

                    ticks_previous = time_in_ticks_cumul
                    tempo_previous = tempo

        return None

    # Return the real time in second
    def get_realtime(self, ticks_cumul, ppq):

        if ticks_cumul == 0:
            return 0

        # Search from the nearest cumul ticks in the past into tempo_map
        for row in self.tempo_map:
            if row:
                if row[0] > ticks_cumul:
                    break
                else:
                    founded_row = row

        seconds = founded_row[6]
        delta = ticks_cumul - founded_row[0]
        sec_per_ticks = (founded_row[1] / ppq) / 1000000
        seconds += delta * sec_per_ticks

        return seconds

class MIDINote_Class:

    # Channel initializations
    def __init__(self, channel, note, time_on, time_off, velocity):
        # Parameters
        self.channel = channel      # channel
        self.note = note            # number
        self.time_on = time_on      # note on time
        self.time_off= time_off     # note off time
        self.velocity = velocity    # note on velocity

        return

class MIDITrack_Class:

    # Channel initializations
    def __init__(self, TrackIndex, TrackName):
        self.Index = TrackIndex         # Channel index number
        self.Name = TrackName           # mean the name or description
        self.Notes = []                 # ListMemorize all events

        return None

    # Add an new midi note
    def add_note(self, channel, note, time_on, time_off, velocity):
        self.Notes.append(MIDINote_Class(channel, note, time_on, time_off, velocity))

        return None

def MIDI_ParseFile(filemid):

    # Open MIDIFile with the module MIDO
    mid = MidiFile(filemid)

    # type = 0 - (single track): all messages are in one track and use the same tempo and start at the same time
    # type = 1 - (synchronous): all messages are in separated tracks and use the same tempo and start at the same time
    # type = 2 - (asynchronous): each track is independent of the others for tempo and for start - not yet supported
    if (mid.type == 2):
        raise RuntimeError("Only MIDI file type 0 or 1, type 2 is not yet supported")

    # Set pulsation per quarter note (ppq)
    # Mean the number of pulsation per round note / 4
    ppq = mid.ticks_per_beat

    # For type 0 and 1 midifile instanciate single time_map
    time_map = Tempo_Class(mid.tracks[0], ppq)

    Tracks = []
    # Main LOOP to "play" and memorize MIDI msg in their realtime
    for TrackIndex, curTracks in enumerate(mid.tracks):
        Track = MIDITrack_Class(TrackIndex,curTracks.name)

        # Initialize the time cumul in ticks
        time_in_ticks_cumul = 0

        lastNoteOn = {}
        # Parse midi message for the current track
        for msg in curTracks:

            # Ignore sysex and sysex not participate to delta time
            if msg.type == "sysex": continue

            time_in_ticks_cumul += msg.time

            # ignore meta msg
            if msg.is_meta: continue

            # Check if note_on with velocity 0 will become note_off
            if (msg.type == 'note_on') and (msg.velocity == 0):
                msgtype = 'note_off'
            else:
                msgtype = msg.type

            current_time = time_map.get_realtime(time_in_ticks_cumul, ppq)
            # If note_on then memorize til note_off become
            if msgtype == 'note_on':
                lastNoteOn[msg.note] = [msg.channel, current_time, msg.velocity]

            # If note_off then create the note with note_on memorized
            # This is a naive think who take for sure all notes are in order in time and never cross off/on
            if msgtype == 'note_off':
                Track.add_note(msg.channel, msg.note, lastNoteOn[msg.note][1], current_time, lastNoteOn[msg.note][2])

        Tracks.append(Track)

    return Tracks
