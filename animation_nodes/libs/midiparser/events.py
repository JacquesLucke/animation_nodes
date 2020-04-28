import struct
from dataclasses import dataclass

@dataclass
class NoteOnEvent:
    deltaTime: int
    channel: int
    note: int
    velocity: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, channel, memoryMap):
        note = struct.unpack("B", memoryMap.read(1))[0]
        velocity = struct.unpack("B", memoryMap.read(1))[0]
        return cls(deltaTime, channel, note, velocity)

@dataclass
class NoteOffEvent:
    deltaTime: int
    channel: int
    note: int
    velocity: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, channel, memoryMap):
        note = struct.unpack("B", memoryMap.read(1))[0]
        velocity = struct.unpack("B", memoryMap.read(1))[0]
        return cls(deltaTime, channel, note, velocity)

@dataclass
class NotePressureEvent:
    deltaTime: int
    channel: int
    note: int
    pressure: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, channel, memoryMap):
        note = struct.unpack("B", memoryMap.read(1))[0]
        pressure = struct.unpack("B", memoryMap.read(1))[0]
        return cls(deltaTime, channel, note, pressure)

@dataclass
class ControllerEvent:
    deltaTime: int
    channel: int
    controller: int
    value: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, channel, memoryMap):
        controller = struct.unpack("B", memoryMap.read(1))[0]
        value = struct.unpack("B", memoryMap.read(1))[0]
        return cls(deltaTime, channel, controller, value)

@dataclass
class ProgramEvent:
    deltaTime: int
    channel: int
    program: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, channel, memoryMap):
        program = struct.unpack("B", memoryMap.read(1))[0]
        return cls(deltaTime, channel, program)

@dataclass
class ChannelPressureEvent:
    deltaTime: int
    channel: int
    pressure: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, channel, memoryMap):
        pressure = struct.unpack("B", memoryMap.read(1))[0]
        return cls(deltaTime, channel, pressure)

@dataclass
class PitchBendEvent:
    deltaTime: int
    channel: int
    lsb: int
    msb: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, channel, memoryMap):
        lsb = struct.unpack("B", memoryMap.read(1))[0]
        msb = struct.unpack("B", memoryMap.read(1))[0]
        return cls(deltaTime, channel, lsb, msb)

@dataclass
class SequenceNumberEvent:
    deltaTime: int
    sequenceNumber: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        sequenceNumber = struct.unpack(">H", memoryMap.read(2))[0]
        return cls(deltaTime, sequenceNumber)

@dataclass
class TextEvent:
    deltaTime: int
    text: str

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        text = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
        return cls(deltaTime, text)

@dataclass
class CopyrightEvent:
    deltaTime: int
    copyright: str

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        copyright = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
        return cls(deltaTime, copyright)

@dataclass
class TrackNameEvent:
    deltaTime: int
    name: str

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        name = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
        return cls(deltaTime, name)

@dataclass
class InstrumentNameEvent:
    deltaTime: int
    name: str

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        name = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
        return cls(deltaTime, name)

@dataclass
class LyricEvent:
    deltaTime: int
    lyric: str

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        lyric = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
        return cls(deltaTime, lyric)

@dataclass
class MarkerEvent:
    deltaTime: int
    marker: str

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        marker = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
        return cls(deltaTime, marker)

@dataclass
class CuePointEvent:
    deltaTime: int
    cuePoint: str

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        cuePoint = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
        return cls(deltaTime, cuePoint)

@dataclass
class ProgramNameEvent:
    deltaTime: int
    name: str

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        name = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
        return cls(deltaTime, name)

@dataclass
class DeviceNameEvent:
    deltaTime: int
    name: str

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        name = struct.unpack(f"{length}s", memoryMap.read(length))[0].decode("latin_1")
        return cls(deltaTime, name)

@dataclass
class MidiChannelPrefixEvent:
    deltaTime: int
    prefix: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        prefix = struct.unpack("B", memoryMap.read(1))[0]
        return cls(deltaTime, prefix)

@dataclass
class MidiPortEvent:
    deltaTime: int
    port: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        port = struct.unpack("B", memoryMap.read(1))[0]
        return cls(deltaTime, port)

@dataclass
class EndOfTrackEvent:
    deltaTime: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        return cls(deltaTime)

@dataclass
class TempoEvent:
    deltaTime: int
    tempo: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        tempo = struct.unpack(">I", b"\x00" + memoryMap.read(3))[0]
        return cls(deltaTime, tempo)

@dataclass
class SmpteOffsetEvent:
    deltaTime: int
    hours: int
    minutes: int
    seconds: int
    fps: int
    fractionalFrames: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        hours = struct.unpack("B", memoryMap.read(1))[0]
        minutes = struct.unpack("B", memoryMap.read(1))[0]
        seconds = struct.unpack("B", memoryMap.read(1))[0]
        fps = struct.unpack("B", memoryMap.read(1))[0]
        fractionalFrames = struct.unpack("B", memoryMap.read(1))[0]
        return cls(deltaTime, hours, minutes, seconds, fps, fractionalFrames)

@dataclass
class TimeSignatureEvent:
    deltaTime: int
    numerator: int
    denominator: int
    clocksPerClick: int
    thirtySecondPer24Clocks: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        numerator = struct.unpack("B", memoryMap.read(1))[0]
        denominator = struct.unpack("B", memoryMap.read(1))[0]
        clocksPerClick = struct.unpack("B", memoryMap.read(1))[0]
        thirtySecondPer24Clocks = struct.unpack("B", memoryMap.read(1))[0]
        return cls(deltaTime, numerator, denominator, clocksPerClick, thirtySecondPer24Clocks)

@dataclass
class KeySignatureEvent:
    deltaTime: int
    flatsSharps: int
    majorMinor: int

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        flatsSharps = struct.unpack("B", memoryMap.read(1))[0]
        majorMinor = struct.unpack("B", memoryMap.read(1))[0]
        return cls(deltaTime, flatsSharps, majorMinor)

@dataclass
class SequencerEvent:
    deltaTime: int
    data: bytes

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        data = struct.unpack(f"{length}s", memoryMap.read(length))[0]
        return cls(deltaTime, data)

@dataclass
class SysExEvent:
    deltaTime: int
    data: bytes

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        data = struct.unpack(f"{length}s", memoryMap.read(length))[0]
        return cls(deltaTime, data)

@dataclass
class EscapeSequenceEvent:
    deltaTime: int
    data: bytes

    @classmethod
    def fromMemoryMap(cls, deltaTime, length, memoryMap):
        data = struct.unpack(f"{length}s", memoryMap.read(length))[0]
        return cls(deltaTime, data)

