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

class Channel_Class:

    # Channel initializations
    def __init__(self, idx_channel, name, list_note):
        """
        Initialization of the Class Channel_Class
        IN
            See below for comment
        OUT
            The new object instanciated
        """
        # Parameters
        self.idx = idx_channel                  # Channel index number
        self.name = name                        # mean the name or description
        self.list_note = list_note              # list of note used in this channel
        self.events = []                        # Memorize all events

        return None

    # Add an new midi event related to the channel
    def add_note_msg(self, evt, second, note, velocity):
        """
        React to note event
        IN
            evt         'note_on' or 'note_off' - Not really used for now
            frame       frame number
            note        note number
            velocity    velocity
        OUT
            None
        """
        event = []
        event.append(note)
        event.append(evt)
        event.append(second)
        event.append(velocity)
        self.events.append(event)

        return None

def MIDI_ReadFile(filemid, useChannel):

    # If use_channel = True then manage separate channel as usual, wherever the tracks where the channel event are
    # If use_channel = False then MIDI File don't use channel info and we use 1 track = 1 channel

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

    # Dictionnary of Channel <= receive object Channel_Class
    ChannelList = {}

    l_channel = []
    channel_name = {}
    l_channel_notes = {}
    # Fill l_channel with all channels found in all tracks
    # and set some channel parameters
    if useChannel:
        for current_track, track in enumerate(mid.tracks):
            for msg in track:
                if msg.type == ('note_on'):
                    if msg.channel not in l_channel:
                        l_channel.append(msg.channel)
                        channel_name[msg.channel] = track.name
                        l_channel_notes[msg.channel] = []
                    if msg.note not in l_channel_notes[msg.channel]:
                        l_channel_notes[msg.channel].append(msg.note)
        l_channel = sorted(l_channel)
    else:
        for current_track, track in enumerate(mid.tracks):
            l_channel.append(current_track)
            channel_name[current_track] = track.name
            l_channel_notes[current_track] = []
            for msg in track:
                if msg.type == ('note_on'):
                    if msg.note not in l_channel_notes[current_track]:
                        l_channel_notes[current_track].append(msg.note)
        l_channel = sorted(l_channel)

    # Add one object per channel
    for cur_chan in l_channel:
        l_channel_notes[cur_chan] = sorted(l_channel_notes[cur_chan])
        ChannelList[cur_chan] = Channel_Class(cur_chan, channel_name[cur_chan], l_channel_notes[cur_chan])

    # Main LOOP to "play" and memorize MIDI msg in their realtime
    for current_track, track in enumerate(mid.tracks):

    #   Initialize the time cumul in ticks and second for the track
        time_in_ticks_cumul = 0

        # Parse midi message for the current track
        for msg in track:

            # Ignore sysex and sysex not participate to delta time
            if msg.type == "sysex":
                continue

            time_in_ticks_cumul += msg.time

            # ignore meta msg
            if msg.is_meta:
                continue

            # Check if note_on with velocity 0 will become note_off
            if (msg.type == 'note_on') and (msg.velocity == 0):
                msgtype = 'note_off'
            else:
                msgtype = msg.type

            # Check real channel following the value of lag useChannel
            if useChannel:
                current_channel = msg.channel
            else:
                current_channel = current_track

            # If note_on or note_off event
            if msgtype in ('note_on', 'note_off'):
                # Evaluate the current time following Tempo MAP
                current_time = time_map.get_realtime(time_in_ticks_cumul, ppq)
                velocity = msg.velocity * (msgtype == 'note_on')  # to avoid note_off with velocity != 0
                ChannelList[current_channel].add_note_msg(msgtype, current_time, msg.note, velocity)

    return ChannelList
