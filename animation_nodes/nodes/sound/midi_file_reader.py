import os
import bpy
from ... utils.midi import readMIDIFile
from ... base_types import AnimationNode

class ReadMIDIFileNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_ReadMIDIFileNode"
    bl_label = "Read MIDI File"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Text", "Path", "path", showFileChooser = True)
        self.newOutput("MIDI Track List", "Tracks", "tracks")

    def draw(self, layout):
        if self.inputs[0].isUnlinked:
            name = os.path.basename(self.inputs[0].value)
            if name != "":
                layout.label(text = name, icon = "FILE_TEXT")

    def drawAdvanced(self, layout):
        self.invokeFunction(layout, "clearCache", text = "Clear Cache")

    def clearCache(self):
        readMIDIFile.cache_clear()

    def execute(self, path):
        if not os.path.exists(path):
            self.raiseErrorMessage("File does not exist.")
        elif not path.endswith(".mid"):
            self.raiseErrorMessage("File is not a MIDI file.")
        else:
            return readMIDIFile(path)
