import bpy
from ... base_types import AnimationNode

class MIDITrackInfoNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_MIDITrackInfoNode"
    bl_label = "MIDI Track Info"

    def create(self):
        self.newInput("MIDI Track", "Track", "track")

        self.newOutput("MIDI Note List", "Notes", "notes")
        self.newOutput("Text", "Name", "name")
        self.newOutput("Integer", "Index", "index")

    def execute(self, track):
        return track.notes, track.name, track.index
