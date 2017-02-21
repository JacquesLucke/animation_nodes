import bpy
from bpy.props import *
from ... base_types import AnimationNode, AutoSelectVectorization

class ComposeMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ComposeMatrixNode"
    bl_label = "Compose Matrix"

    useTranslationList = BoolProperty(update = AnimationNode.refresh)
    useRotationList = BoolProperty(update = AnimationNode.refresh)
    useScaleList = BoolProperty(update = AnimationNode.refresh)

    def create(self):
        self.newInputGroup(self.useTranslationList,
            ("Vector", "Translation", "translation"),
            ("Vector List", "Translations", "translations"))

        self.newInputGroup(self.useRotationList,
            ("Euler", "Rotation", "rotation"),
            ("Euler List", "Rotations", "rotations"))

        self.newInputGroup(self.useScaleList,
            ("Vector", "Scale", "scale", {"value" : (1, 1, 1)}),
            ("Vector List", "Scales", "scales"))

        self.newOutputGroup(self.generateList,
            ("Matrix", "Matrix", "matrix"),
            ("Matrix List", "Matrices", "matrices"))

        vectorization = AutoSelectVectorization()
        vectorization.input(self, "useTranslationList", self.inputs[0])
        vectorization.input(self, "useRotationList", self.inputs[1])
        vectorization.input(self, "useScaleList", self.inputs[2])
        vectorization.output(self,
            [("useTranslationList", "useRotationList", "useScaleList")],
            self.outputs[0])
        self.newSocketEffect(vectorization)

    def getExecutionFunctionName(self):
        if self.generateList:
            return "execute_List"

    def getExecutionCode(self):
        yield "matrix = animation_nodes.utils.math.composeMatrix(translation, rotation, scale)"

    def execute_List(self, translations, rotations, scales):
        from . list_operation_utils import composeMatrices
        return composeMatrices(translations, rotations, scales)

    @property
    def generateList(self):
        return self.useTranslationList or self.useRotationList or self.useScaleList
