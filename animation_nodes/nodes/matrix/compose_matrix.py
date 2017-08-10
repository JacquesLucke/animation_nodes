import bpy
from bpy.props import *
from . c_utils import composeMatrices
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualList, VirtualVector3DList, VirtualEulerList

class ComposeMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ComposeMatrixNode"
    bl_label = "Compose Matrix"

    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        propertyChanged()

    useTranslation = BoolProperty(name = "Use Translation", default = False,
        update = checkedPropertiesChanged)
    useRotation = BoolProperty(name = "Use Rotation", default = False,
        update = checkedPropertiesChanged)
    useScale = BoolProperty(name = "Use Scale", default = False,
        update = checkedPropertiesChanged)

    useTranslationList = VectorizedSocket.newProperty()
    useRotationList = VectorizedSocket.newProperty()
    useScaleList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "useTranslationList",
            ("Translation", "translation"),
            ("Translations", "translations")))

        self.newInput(VectorizedSocket("Euler", "useRotationList",
            ("Rotation", "rotation"),
            ("Rotations", "rotations")))

        self.newInput(VectorizedSocket("Vector", "useScaleList",
            ("Scale", "scale", dict(value = (1, 1, 1))),
            ("Scales", "scales"),
            dict(default = (1, 1, 1))))

        self.newOutput(VectorizedSocket("Matrix",
            ["useTranslationList", "useRotationList", "useScaleList"],
            ("Matrix", "matrix"), ("Matrices", "matrices")))

    def updateSocketVisibility(self):
        self.inputs[0].hide = not self.useTranslation
        self.inputs[1].hide = not self.useRotation
        self.inputs[2].hide = not self.useScale

    def getExecutionCode(self, required):
        useList = ((self.useTranslation and self.useTranslationList) or
                   (self.useRotation and self.useRotationList) or
                   (self.useScale and self.useScaleList))

        if self.useTranslationList or self.useRotationList or self.useScaleList:
            args = ", ".join(socket.identifier for socket in self.inputs)
            yield "matrices = self.calculateMatrices({})".format(args)
        else:
            # TODO: care about activated sockets
            yield "matrix = animation_nodes.utils.math.composeMatrix(translation, rotation, scale)"

    def calculateMatrices(self, translation, rotation, scale):
        translations = VirtualVector3DList.fromListOrElement(translation)
        rotations = VirtualEulerList.fromListOrElement(rotation)
        scales = VirtualVector3DList.fromListOrElement(scale)

'''
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
'''
