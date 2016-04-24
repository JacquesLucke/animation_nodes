import bpy
from ... base_types.template import Template

class SoundEqualizerTemplate(bpy.types.Operator, Template):
    bl_idname = "an.sound_equalizer_template"
    bl_label = "Sound Equalizer"
    nodeOffset = (-500, 150)

    def insert(self):
        soundBakeNode = self.newNode("an_SoundBakeNode", x = 0, y = 0)

        instancerNode = self.newNode("an_ObjectInstancerNode", x = 400, y = 0)
        instancerNode.inputs[0].value = 5
        evaluateSoundNode = self.newNode("an_EvaluateSoundNode", x = 400, y = -220)
        evaluateSoundNode.soundType = "EQUALIZER"
        invokeSubprogramNode = self.newNode("an_InvokeSubprogramNode", x = 713, y = -52)

        loopInputNode = self.newNode("an_LoopInputNode", x = 50, y = -450)
        loopInputNode.newIterator("Object List", name = "Object")
        loopInputNode.newParameter("Float List", name = "Equalizer Data")

        calcMixFactorNode = self.newNode("an_FloatMathNode", x = 340, y = -600)
        calcMixFactorNode.operation = "DIVIDE"

        mixFloatListNode = self.newNode("an_MixDataListNode", x = 560, y = -600)
        interpolationSocket = mixFloatListNode.inputs["Interpolation"]
        interpolationSocket.category = "QUADRATIC"
        interpolationSocket.easeIn = interpolationSocket.easeOut = True

        calcHeightNode = self.newNode("an_FloatMathNode", x = 790, y = -600)
        calcOffsetNode = self.newNode("an_FloatMathNode", x = 790, y = -380)
        combineVectorNode = self.newNode("an_CombineVectorNode", x = 1000, y = -380)
        transformsOutputNode = self.newNode("an_ObjectTransformsOutputNode", x = 1210, y = -415)
        transformsOutputNode.useLocation = [True, True, True]

        invokeSubprogramNode.subprogramIdentifier = loopInputNode.identifier
        self.updateSubprograms()

        self.newLink(instancerNode.outputs[0], invokeSubprogramNode.inputs[0])
        self.newLink(evaluateSoundNode.outputs[1], invokeSubprogramNode.inputs[1])
        self.newLink(loopInputNode.outputs[2], transformsOutputNode.inputs[0])
        self.newLink(loopInputNode.outputs[0], calcOffsetNode.inputs[0])
        self.newLink(combineVectorNode.outputs[0], transformsOutputNode.inputs[1])
        self.newLink(loopInputNode.outputs[4], mixFloatListNode.inputs[1])
        self.newLink(loopInputNode.outputs[0], calcMixFactorNode.inputs[0])
        self.newLink(loopInputNode.outputs[1], calcMixFactorNode.inputs[1])
        self.newLink(calcMixFactorNode.outputs[0], mixFloatListNode.inputs[0])
        self.newLink(mixFloatListNode.outputs[0], calcHeightNode.inputs[0])
        self.newLink(calcHeightNode.outputs[0], combineVectorNode.inputs[2])
        self.newLink(calcOffsetNode.outputs[0], combineVectorNode.inputs[0])

        bpy.context.scene.sync_mode = "AUDIO_SYNC"
