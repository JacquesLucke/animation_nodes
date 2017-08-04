import bpy
from . c_utils import composeMatrices
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualList, VirtualVector3DList, VirtualEulerList

class ComposeMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ComposeMatrixNode"
    bl_label = "Compose Matrix"

    useTranslationList = VectorizedSocket.newProperty()
    useRotationList = VectorizedSocket.newProperty()
    useScaleList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "useTranslationList",
            ("Translation", "translation"), ("Translations", "translations")))

        self.newInput(VectorizedSocket("Euler", "useRotationList",
            ("Rotation", "rotation"), ("Rotations", "rotations")))

        self.newInput(VectorizedSocket("Vector", "useScaleList",
            ("Scale", "scale", dict(value = (1, 1, 1))),
            ("Scales", "scales"),
            dict(default = (1, 1, 1))))

        self.newOutput(VectorizedSocket("Matrix",
            ["useTranslationList", "useRotationList", "useScaleList"],
            ("Matrix", "matrix"), ("Matrices", "matrices")))

    def getExecutionFunctionName(self):
        if self.useTranslationList or self.useRotationList or self.useScaleList:
            return "execute_List"

    def getExecutionCode(self, required):
        yield "matrix = animation_nodes.utils.math.composeMatrix(translation, rotation, scale)"

    def execute_List(self, translations, rotations, scales):
        _translations = VirtualVector3DList.fromListOrElement(translations, (0, 0, 0))
        _rotations = VirtualEulerList.fromListOrElement(rotations, (0, 0, 0))
        _scales = VirtualVector3DList.fromListOrElement(scales, (1, 1, 1))
        length = VirtualList.getMaxRealLength(_translations, _rotations, _scales)
        return composeMatrices(length, _translations, _rotations, _scales)
