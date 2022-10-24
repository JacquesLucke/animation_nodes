import bpy
from ... base_types import AnimationNode, VectorizedSocket

class MIDINoteInfoNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_MIDITempoEventInfoNode"
    bl_label = "MIDI Tempo Event Info"

    useTemposList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("MIDI Tempo Event", "useTemposList",
            ("Tempo Event", "tempoEvent"), ("Tempo Events", "tempoEvents")))
        self.newOutput(VectorizedSocket("Float", "useTemposList",
            ("Time in Quarter Note", "timeInQuarterNotes"), ("Times in Quarter Note", "timesInQuarterNotes")))
        self.newOutput(VectorizedSocket("Float", "useTemposList",
            ("Time in seconds", "timeInSeconds"), ("Times in seconds", "timesInSeconds")))
        self.newOutput(VectorizedSocket("Integer", "useTemposList",
            ("Tempo", "tempo"), ("Tempos", "tempos")))

    def getExecutionCode(self, required):
        if not self.useTemposList:
            if "timeInQuarterNotes" in required:
                yield "timeInQuarterNotes = tempoEvent.timeInQuarterNotes"
            if "timeInSeconds" in required:
                yield "timeInSeconds = tempoEvent.timeInSeconds"
            if "tempo" in required:
                yield "tempo = tempoEvent.tempo"
        else:
            if "timesInQuarterNotes" in required:
                yield "timesInQuarterNotes = DoubleList.fromValues(tempoEvent.timeInQuarterNotes for tempoEvent in tempoEvents)"
            if "timesInSeconds" in required:
                yield "timesInSeconds = DoubleList.fromValues(tempoEvent.timeInSeconds for tempoEvent in tempoEvents)"
            if "tempos" in required:
                yield "tempos = LongList.fromValues(tempoEvent.tempo for tempoEvent in tempoEvents)"
