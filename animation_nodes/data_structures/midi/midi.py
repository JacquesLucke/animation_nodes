
class MIDINote_Class:

    # Channel initializations
    def __init__(self, channel, note, time_on, time_off, velocity):
        # Parameters
        self.channel = channel      # channel
        self.note = note            # number
        self.time_on = time_on      # note on time
        self.time_off = time_off    # note off time
        self.velocity = velocity    # note on velocity

        return


class MIDITrack_Class:

    # Channel initializations
    def __init__(self, TrackIndex, TrackName):
        self.Index = TrackIndex         # Channel index number
        self.Name = TrackName           # mean the name or description
        self.Notes = []                 # ListMemorize all events

        return

    # Add an new midi note
    def add_note(self, channel, note, time_on, time_off, velocity):
        self.Notes.append(MIDINote_Class(channel, note, time_on, time_off, velocity))

        return
