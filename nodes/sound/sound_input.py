import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... utils.enum_items import enumItemsFromDicts
from ... utils.sequence_editor import getSoundSequences
from . cache import getStrengthOfSequence

@enumItemsFromDicts
def getSequenceSoundEnumItems(self, context):
    items = []
    for sequence in getSoundSequences():
        for i, bakeData in enumerate(sequence.sound.bakeData):
            items.append({"id" : "{}{}".format(sequence.name, i), "value" : "{}#-#{}".format(sequence.name, i), "name" : "{}; Low: {}; High: {}; Attack: {:.3f}; Release: {:.3f}".format(sequence.name, bakeData.low, bakeData.high, bakeData.attack, bakeData.release)})
    return items

class SoundInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SoundInputNode"
    bl_label = "Sound Input"

    bakeData = EnumProperty(items = getSequenceSoundEnumItems)

    def create(self):
        self.outputs.new("an_FloatSocket", "Strength", "strength")

    def draw(self, layout):
        layout.prop(self, "bakeData", text = "")

    def execute(self):
        sequenceName, strIndex = self.bakeData.split("#-#")
        frame = bpy.context.scene.frame_current
        sequence = bpy.context.scene.sequence_editor.sequences[sequenceName]
        return getStrengthOfSequence(sequence, int(strIndex), frame)
