import bpy
from ... base_types import AnimationNode

class CopyLocationWithOffsetNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiNode"
    bl_label = "MIDI"

    def create(self):
        self.newInput("Object", "Source", "source")
        self.newInput("Object", "Target", "target")
        self.newInput("Vector", "Offset", "offset")

    def execute(self, source, target, offset):
        if source is None or target is None:
            return

        target.location = source.location + offset
