import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import VectorizedNode
from .. falloff.invert_falloff import InvertFalloff

from ... algorithms.matrices.translation cimport translateMatrixList
from ... algorithms.matrices.rotation cimport getRotatedMatrixList
from ... algorithms.matrices.scale cimport scaleMatrixList

from ... data_structures cimport (
    Falloff,
    FalloffEvaluator,
    Matrix4x4List,
    Vector3DList,
    EulerList,
    DoubleList,
    CDefaultList
)

specifiedStateItems = [
    ("START", "Start", "", "Given matrices set the start state", 0),
    ("END", "End", "", "Given matrices set the end state", 1)
]

translationModeItems = [
    ("LOCAL_AXIS", "Local Axis", "", "NONE", 0),
    ("GLOBAL_AXIS", "Global Axis", "", "NONE", 1)
]

rotationModeItems = [
    ("LOCAL_AXIS__LOCAL_PIVOT", "Local Axis - Local Pivot", "", "NONE", 0),
    ("GLOBAL_AXIS__LOCAL_PIVOT", "Global Axis - Local Pivot", "", "NONE", 1),
    ("GLOBAL_AXIS__GLOBAL_PIVOT", "Global Axis - Global Pivot", "", "NONE", 2)
]

scaleModeItems = [
    ("LOCAL_AXIS", "Local Axis", "", "NONE", 0),
    ("GLOBAL_AXIS", "Global Axis", "", "NONE", 1),
    ("INCLUDE_TRANSLATION", "Include Translation", "", "NONE", 2),
    ("TRANSLATION_ONLY", "Translation Only", "", "NONE", 3)
]

class OffsetMatricesNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_OffsetMatricesNode"
    bl_label = "Offset Matrices"
    bl_width_default = 190

    errorMessage = StringProperty()

    specifiedState = EnumProperty(name = "Specified State", default = "START",
        description = "Specify wether the given matrices are the start or end state",
        items = specifiedStateItems, update = propertyChanged)

    useTranslation = BoolProperty(name = "Use Translation", default = False,
        update = VectorizedNode.refresh)
    useRotation = BoolProperty(name = "Use Rotation", default = False,
        update = VectorizedNode.refresh)
    useScale = BoolProperty(name = "Use Scale", default = False,
        update = VectorizedNode.refresh)

    useTranslationList = VectorizedNode.newVectorizeProperty()
    useRotationList = VectorizedNode.newVectorizeProperty()
    useScaleList = VectorizedNode.newVectorizeProperty()

    translationMode = EnumProperty(name = "Translation Mode", default = "GLOBAL_AXIS",
        items = translationModeItems, update = propertyChanged)

    rotationMode = EnumProperty(name = "Rotation Mode", default = "GLOBAL_AXIS__LOCAL_PIVOT",
        items = rotationModeItems, update = propertyChanged)

    scaleMode = EnumProperty(name = "Scale Mode", default = "LOCAL_AXIS",
        items = scaleModeItems, update = propertyChanged)

    def create(self):
        self.newInput("Matrix List", "Matrices", "inMatrices", dataIsModified = self.modifiesOriginalList)
        self.newInput("Falloff", "Falloff", "falloff")

        if self.useTranslation:
            self.newVectorizedInput("Vector", "useTranslationList",
                ("Translation", "translation"),
                ("Translations", "translations"))

        if self.useRotation:
            self.newVectorizedInput("Euler", "useRotationList",
                ("Rotation", "rotation"),
                ("Rotations", "rotations"))

        if self.useScale:
            self.newVectorizedInput("Vector", "useScaleList",
                ("Scale", "scale", dict(value = (1, 1, 1))),
                ("Scales", "scales"))

        self.newOutput("Matrix List", "Matrices", "outMatrices")

    def draw(self, layout):
        col = layout.column()

        row = col.row(align = True)
        row.prop(self, "useTranslation", text = "Loc", icon = "MAN_TRANS")
        row.prop(self, "useRotation", text = "Rot", icon = "MAN_ROT")
        row.prop(self, "useScale", text = "Scale", icon = "MAN_SCALE")

        col.row().prop(self, "specifiedState", expand = True)

        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawAdvanced(self, layout):
        col = layout.column(align = True)
        col.prop(self, "translationMode", text = "Translation")
        col.prop(self, "rotationMode", text = "Rotation")
        col.prop(self, "scaleMode", text = "Scale")

        if self.scaleMode in ("GLOBAL_AXIS", "INCLUDE_TRANSLATION"):
            layout.label("May result in invalid object matrices", icon = "INFO")


    def execute(self, Matrix4x4List matrices, Falloff falloff, *args):
        self.errorMessage = ""
        if len(args) == 0:
            return matrices

        cdef DoubleList influences = self.evaluateFalloff(matrices, falloff)
        if influences is None:
            return matrices

        if self.useScale:
            scaleMatrixList(matrices, self.scaleMode, self.getScales(args), influences)
        if self.useRotation:
            matrices = getRotatedMatrixList(matrices, self.rotationMode, self.getRotations(args), influences)
        if self.useTranslation:
            translateMatrixList(matrices, self.translationMode, self.getTranslations(args), influences)

        return matrices

    def evaluateFalloff(self, Matrix4x4List matrices, Falloff falloff):
        if self.specifiedState == "END":
            falloff = InvertFalloff(falloff)

        cdef Py_ssize_t i
        cdef FalloffEvaluator evaluator
        cdef DoubleList influences = DoubleList(length = len(matrices))

        try: evaluator = falloff.getEvaluator("Transformation Matrix")
        except:
            self.errorMessage = "Falloff cannot be evaluated for matrices"
            return None

        for i in range(len(influences)):
            influences.data[i] = evaluator.evaluate(matrices.data + i, i)
        return influences

    def getTranslations(self, args):
        if self.useTranslation:
            return CDefaultList(Vector3DList, args[0], (0, 0, 0))
        return None

    def getRotations(self, args):
        if self.useRotation:
            if self.useTranslation:
                return CDefaultList(EulerList, args[1], (0, 0, 0))
            else:
                return CDefaultList(EulerList, args[0], (0, 0, 0))
        return None

    def getScales(self, args):
        if self.useScale:
            return CDefaultList(Vector3DList, args[-1], (1, 1, 1))
        return None

    @property
    def modifiesOriginalList(self):
        return self.useScale or (self.useTranslation and not self.useRotation)
