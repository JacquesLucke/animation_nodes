import bpy

# How to install a new python module in the blender (here mido) :
# http://www.codeplastic.com/2019/03/12/how-to-install-python-modules-in-blender/
# Mido is a library for working with MIDI messages and ports.
# It’s designed to be as straight forward and Pythonic as possible:
# https://mido.readthedocs.io/en/latest/installing.html
from mido import MidiFile

# ********************************************************************
# Midi_To_Blend
# version = 1.011
# Blender version = 2.8
# Author = Patrick Mauger
# Web Site = docouatzat.com
# Mail = docouatzat@gmail.com
#
# Licence used = Creative Commons CC BY
# Check licence here : https://creativecommons.org
#
# Generate 3D objects animated from midifile
# ********************************************************************

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

    # Return the second calculated with absolute time in seconds from ticks cumul provided
    def second(self, ticks_cumul, ppq):

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

        # Internal use
        self.events = []                        # Memorize all events

        return

    # Add an new midi event related to the channel
    def add_note_evt(self, evt, second, note, velocity):
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
        event.append(second)
        event.append(evt)
        event.append(note)
        event.append(velocity)
        self.events.append(event)

        return None

    # get all note value for any second
    def get_notes_value(self, second):
        """
        Sort all notes for track/channel value at frame
        IN
            frame       frame number
        OUT
            list of track/value
        """
        listvalues = []
        for note in self.list_note:
            listvalues.append(note)
            value += event.velocity

        return listvalues


def create_MIDI(filemid):

    # path and name of midi file - temporary => replaced when this become an add-on
    # path = "C:\\tmp\\MTB\\data"
    path = "D:\\OneDrive\\Blog\\MTB\\data"
    filename = "T1_take5"
    # If use_channel = True then manage separate channel as usual, wherever the tracks where the channel event are
    # If use_channel = False then MIDI File don't use channel info and we use 1 track = 1 channel
    use_channel = True
    # filemid = path + "\\" + filename + ".mid"

    # Open log file for append
    # flog = open(filelog, "w+")

    # Open MIDIFile with the module MIDO
    mid = MidiFile(filemid)

    # type = 0 - (single track): all messages are in one track and use the same tempo and start at the same time
    # type = 1 - (synchronous): all messages are in separated tracks and use the same tempo and start at the same time
    # type = 2 - (asynchronous): each track is independent of the others for tempo and for start - not yet supported
    if (mid.type == 2):
        raise RuntimeError("Only type 0 or 1, type 2 is not yet supported")

    """ STEP 1 - Prepare """

    # Set pulsation per quarter note (ppq)
    # Mean the number of pulsation per round note / 4 = black note
    ppq = mid.ticks_per_beat

    # Init Max frame number founded for all channel, mean the end of animation
    max_num_frame = 0

    # take the framerate directly from blender
    # framerate = bpy.context.scene.render.fps
    framerate = 24

    # For type 0 and 1 midifile
    # instanciate single time_map
    time_map = Tempo_Class(mid.tracks[0], ppq)

    """ STEP 2 - Creating the 3D channel vizualisation objects """

    # Dictionnary of Channel <= receive object Channel_Class
    ChannelList = {}

    l_channel = []
    channel_name = {}
    l_channel_notes = {}
    # Fill l_channel with all channels found in all tracks
    # and set some channel parameters
    if use_channel:
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

    # Create one vizualisation object per channel
    for cur_chan in l_channel:
        l_channel_notes[cur_chan] = sorted(l_channel_notes[cur_chan])
        ChannelList[cur_chan] = Channel_Class(cur_chan, channel_name[cur_chan], l_channel_notes[cur_chan])

    """ STEP 3 - Main LOOP to memorize event in time """
    for current_track, track in enumerate(mid.tracks):

    #   Initialize the time cumul in ticks and second for the track
        time_in_ticks_cumul = 0

        # Parse midi message for the current track
        for msg in track:

            if msg.type == "sysex":
                continue

            time_in_ticks_cumul += msg.time

            if msg.is_meta:
                continue

            # Check if note_on with velocity 0 will become note_off
            if (msg.type == 'note_on') and (msg.velocity == 0):
                msgtype = 'note_off'
            else:
                msgtype = msg.type

            # Check real channel following the value of lag use_channel
            if use_channel:
                current_channel = msg.channel
            else:
                current_channel = current_track

            # If note_on or note_off event
            if msgtype in ('note_on', 'note_off'):
                # Evaluate the current frame following Tempo MAP
                current_second = time_map.second(time_in_ticks_cumul, ppq)
                velocity = msg.velocity * (msgtype == 'note_on')  # to avoid note_off with velocity != 0
                ChannelList[current_channel].add_note_evt(msgtype, current_second, msg.note, velocity)
            # if pitchwheel event
            # elif msg.type == 'pitchwheel':
            #     ChannelList[current_channel].add_pitchwheel_evt(current_frame, msg.pitch)
            # elif msg.type == 'aftertouch':
            #     ChannelList[current_channel].add_aftertouch_evt(current_frame, msg.value)
            # elif msg.type == 'control_change':
            #     ChannelList[current_channel].add_ctrlchange_evt(current_frame, msg.control, msg.value)

    return ChannelList


def execute_MIDI(channel, frame, fps):
    """
    IN
        channel     channel data
        second      second for evt
    OUT
        List of velocity, one for each note
    """

    listvalues = []
    velnote = {}
    events = channel.events
    # print(events)
    second = frame / fps
    range = 10 / fps
    range_min = second - range
    range_max = second + range

    # print(str(second)+","+str(range_min)+","+str(range_max))

    for event in events:
        # print(event)
        if (event[0] >= range_min) and (event[0] <= range_max):
            velnote[event[2]] = event[3]

    for note in channel.list_note:
        # print("note = "+str(note))
        if note not in velnote:
            listvalues.append(0)  # maybe having a cache from value predecessor if the good idea
        else:
            listvalues.append(velnote[note])

    return listvalues

        # 0 event.append(second)
        # 1 event.append(evt)
        # 2 event.append(note)
        # 3 event.append(velocity)
