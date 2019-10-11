import bpy
from bpy.props import *
from ... sockets.info import isBase, toBaseDataType
from ... events import propertyChanged
from ... base_types import AnimationNode, ListTypeSelectorSocket

class MidiTrackNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiTrackInfoNode"
    bl_label = "MIDI Track Info"
    bl_width_default = 180

    assignedType: ListTypeSelectorSocket.newProperty(default = "Float")

    def create(self):
        self.newInput("Generic", "Track", "track")
        self.newOutput("Generic", "Notes", "notes")

    def execute(self, track):
        if track is None: return None

        return track.Notes
