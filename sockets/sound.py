import bpy
from bpy.props import *
from .. events import propertyChanged
from .. utils.enum_items import enumItemsFromDicts
from .. base_types.socket import AnimationNodeSocket
from .. utils.sequence_editor import getSoundSequences
from .. nodes.sound.sound_from_sequences import SequencesEvaluator

soundTypeItems = [
    ("SINGLE", "Single", "Only one strength per frame per sequence", "NONE", 0),
    ("EQUALIZER", "Equalizer", "Multiple strengths for different frequencies", "NONE", 1) ]

@enumItemsFromDicts
def getBakeDataItems(self, context):
    items = []
    for sequenceIndex, sequence in enumerate(getSoundSequences()):
        sound = sequence.sound
        for bakeIndex, data in enumerate(sound.bakeData):
            items.append({
                "id" : data.identifier,
                "value" : "{}_{}".format(sequenceIndex, bakeIndex),
                "name" : "#{} - {}".format(bakeIndex, sequence.name),
                "description" : "Low: {}  High: {}  Attack: {:.3f}  Release: {:.3f}".format(data.low, data.high, data.attack, data.release)
            })
    return items

class SoundSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_SoundSocket"
    bl_label = "Sound Socket"
    dataType = "Sound"
    allowedInputTypes = ["Sound"]
    drawColor = (0.9, 0.7, 0.4, 1)

    type = EnumProperty(default = "SINGLE", items = soundTypeItems)
    bakeData = EnumProperty(name = "Bake Data", items = getBakeDataItems)

    def drawProperty(self, layout, text):
        layout.prop(self, "bakeData", text = text)

    def getValue(self):
        try:
            sequenceIndex, bakeIndex = self.bakeData.split("_")
            sequence = bpy.context.scene.sequence_editor.sequences[int(sequenceIndex)]
            evaluator = SequencesEvaluator([sequence], int(bakeIndex))
            return evaluator
        except: return None
