import bpy
from ... base_types.template import Template

class SimpleSoundControlerTemplate(bpy.types.Operator, Template):
    bl_idname = "an.simple_sound_controler_template"
    bl_label = "Simple Sound Controler"
    nodeOffset = (-500, 150)

    def insert(self):
        soundBakeNode = self.newNode("an_SoundBakeNode", x = 0, y = 0)

        evaluateSoundNode = self.newNode("an_EvaluateSoundNode", x = 455, y = 0)
        mathNode = self.newNode("an_FloatMathNode", x = 705, y = 0)
        combineVectorNode = self.newNode("an_CombineVectorNode", x = 925, y = 0)
        transformsOutputNode = self.newNode("an_ObjectTransformsOutputNode", x = 1135, y = 0)
        transformsOutputNode.useLocation = [True, True, True]

        self.newLink(evaluateSoundNode.outputs[0], mathNode.inputs[0])
        self.newLink(combineVectorNode.outputs[0], transformsOutputNode.inputs[1])
        self.newLink(mathNode.outputs[0], combineVectorNode.inputs[2])

        bpy.context.scene.sync_mode = "AUDIO_SYNC"
