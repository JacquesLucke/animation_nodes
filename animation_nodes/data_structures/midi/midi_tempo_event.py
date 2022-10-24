from dataclasses import dataclass

@dataclass
class MIDITempoEvent:
    timeInTicks: int = 0
    timeInQuarterNotes: float = 0
    timeInSeconds: float = 0
    tempo: int = 0 # MIDI default - microseconds per beat

    def copy(self):
        return MIDITempoEvent(self.timeInTicks, self.timeInQuarterNotes,
                              self.timeInSeconds,
                              self.tempo)
