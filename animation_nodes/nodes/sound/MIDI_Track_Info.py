import bpy
from ... base_types import AnimationNode, ListTypeSelectorSocket

class MidiTrackNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiTrackInfoNode"
    bl_label = "MIDI Track Info"
    bl_width_default = 180

    def create(self):
        self.newInput("MIDITrack", "Track", "track")
        self.newOutput("MIDINoteList", "Notes", "notes")

    def execute(self, track):
        if track is None: return None
        return track.notes
