from dataclasses import dataclass

@dataclass
class MIDINote:
    channel: int = 0
    noteNumber: int = 0
    timeOn: float = 0
    timeOff: float = 0
    velocity: float = 0

    def evaluate(self, time, attackTime, attackInterpolation, releaseTime, releaseInterpolation):
        peakTime = self.timeOn + attackTime
        endTime = self.timeOff + releaseTime
        if self.timeOff >= time >= peakTime:
            return 1
        elif peakTime > time >= self.timeOn:
            if attackTime == 0: return 1
            return attackInterpolation((time - self.timeOn) / attackTime)
        elif endTime >= time > self.timeOff:
            if releaseTime == 0: return 1
            return releaseInterpolation(1 - ((time - self.timeOff) / releaseTime))
        return 0.0

    def copy(self):
        return MIDINote(self.channel, self.noteNumber, self.timeOn, self.timeOff, self.velocity)
