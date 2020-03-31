class midiNote:
    def __init__(self, channel, noteNumber, timeOn, timeOff, velocity):
        self.channel = channel
        self.noteNumber = noteNumber
        self.timeOn = timeOn
        self.timeOff = timeOff
        self.velocity = velocity

