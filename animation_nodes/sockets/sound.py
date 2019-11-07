import os
import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types import AnimationNodeSocket
from .. algorithms.hashing import strToEnumItemID
from .. data_structures import Sound, SoundSequence
from .. utils.sequence_editor import getOrCreateSequencer, getEmptyChannel

def getSoundSequenceItems(self, context):
    items = []
    for scene in bpy.data.scenes:
        if scene.sequence_editor is not None:
            for strip in scene.sequence_editor.sequences_all:
                if strip.type == "SOUND":
                    items.append((strip.name, strip.name, "", strToEnumItemID(strip.name)))
    items.append(("NONE", "Empty Sound", "", 0))
    return items

class SoundSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_SoundSocket"
    bl_label = "Sound Socket"
    dataType = "Sound"
    drawColor = (0.9, 0.7, 0.4, 1)
    storable = False
    comparable = False

    soundSequence: EnumProperty(name = "Sound Sequence", items = getSoundSequenceItems,
        update = propertyChanged)

    def drawProperty(self, layout, text, node):
        row = layout.row(align = True)
        row.prop(self, "soundSequence", text = "")
        self.invokeSelector(row, "PATH", node, "loadSound", icon = "PLUS")

    def getValue(self):
        if self.soundSequence == "NONE" or self.soundSequence == "": return Sound([])
        for scene in bpy.data.scenes:
            if scene.sequence_editor is not None:
                sequence = scene.sequence_editor.sequences_all.get(self.soundSequence)
                if sequence is not None:
                    soundSequence = SoundSequence.fromSequence(sequence)
                    return Sound([soundSequence]) if soundSequence is not None else Sound([])

    def setProperty(self, data):
        try: self.soundSequence = data
        except: pass

    def getProperty(self):
        return self.soundSequence

    def loadSound(self, path):
        editor = getOrCreateSequencer(self.nodeTree.scene)
        channel = getEmptyChannel(editor)
        sequence = editor.sequences.new_sound(
            name = os.path.basename(path),
            filepath = path,
            channel = channel,
            frame_start = bpy.context.scene.frame_start)
        self.soundSequence = sequence.name

    @classmethod
    def getDefaultValue(cls):
        return Sound([])

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, Sound) or value is None:
            return value, 0
        return cls.getDefaultValue(), 2
