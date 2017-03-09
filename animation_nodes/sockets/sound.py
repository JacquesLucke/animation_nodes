import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types import AnimationNodeSocket
from .. algorithms.hashing import strToEnumItemID
from .. utils.nodes import newNodeAtCursor, invokeTranslation
from .. nodes.sound.sound_from_sequences import (SingleSoundEvaluator,
                                                 SpectrumSoundEvaluator)

soundTypeItems = [
    ("SINGLE", "Single", "Only one strength per frame per sequence", "NONE", 0),
    ("SPECTRUM", "Spectrum", "Multiple strengths for different frequencies", "NONE", 1)]

def getBakeDataItems(self, context):
    items = []
    sequences = getattr(self.nodeTree.scene.sequence_editor, "sequences", [])
    for sequenceIndex, sequence in enumerate(sequences):
        if sequence.type != "SOUND": continue
        sound = sequence.sound

        for bakeIndex, data in enumerate(sound.singleData):
            items.append((
                "SINGLE_{}_{}".format(sequenceIndex, bakeIndex),
                "#{} - {} - Single".format(bakeIndex, sequence.name),
                "Low: {}  High: {}  Attack: {:.3f}  Release: {:.3f}".format(
                    data.low, data.high, data.attack, data.release),
                strToEnumItemID(data.identifier)))

        for bakeIndex, data in enumerate(sound.spectrumData):
            items.append((
                "SPECTRUM_{}_{}".format(sequenceIndex, bakeIndex),
                "#{} - {} - Spectrum".format(bakeIndex, sequence.name),
                "Attack: {:.3f}  Release: {:.3f}".format(data.attack, data.release),
                strToEnumItemID(data.identifier)))

    if len(items) == 0:
        return [("None", "None", "")]
    return items

class SoundSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_SoundSocket"
    bl_label = "Sound Socket"
    dataType = "Sound"
    allowedInputTypes = ["Sound"]
    drawColor = (0.9, 0.7, 0.4, 1)
    storable = False
    comparable = False

    bakeData = EnumProperty(name = "Bake Data", items = getBakeDataItems,
        update = propertyChanged)

    def drawProperty(self, layout, text, node):
        row = layout.row(align = True)
        row.prop(self, "bakeData", text = text)
        if self.bakeData == "None":
            self.invokeFunction(row, node, "createSoundBakeNode", icon = "PLUS",
                description = "Create sound bake node")

    def getValue(self):
        try:
            soundType, sequenceIndex, bakeIndex = self.bakeData.split("_")
            sequence = self.nodeTree.scene.sequence_editor.sequences[int(sequenceIndex)]
            evaluatorClass = SingleSoundEvaluator if soundType == "SINGLE" else SpectrumSoundEvaluator
            return evaluatorClass([sequence], int(bakeIndex))
        except:
            return None

    def setProperty(self, data):
        self.bakeData, self.type = data

    def getProperty(self):
        return self.bakeData, self.type

    def updateProperty(self):
        self.bakeData = self.bakeData

    def createSoundBakeNode(self):
        newNodeAtCursor("an_SoundBakeNode")
        invokeTranslation()

    @classmethod
    def getDefaultValue(cls):
        return None

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, (SingleSoundEvaluator, SpectrumSoundEvaluator)) or value is None:
            return value, 0
        return cls.getDefaultValue(), 2
