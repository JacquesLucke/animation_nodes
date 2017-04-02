import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import VectorizedNode
from ... data_structures cimport (
    Falloff,
    FalloffEvaluator,
    Matrix4x4List,
    Vector3DList,
    EulerList,
    DoubleList,
    CDefaultList
)

from ... algorithms.matrices.scale cimport scaleMatrixList

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

    useTranslation = BoolProperty(name = "Use Translation", default = True,
        update = VectorizedNode.refresh)
    useRotation = BoolProperty(name = "Use Rotation", default = False,
        update = VectorizedNode.refresh)
    useScale = BoolProperty(name = "Use Scale", default = False,
        update = VectorizedNode.refresh)

    useScaleList = VectorizedNode.newVectorizeProperty()

    scaleMode = EnumProperty(name = "Scale Mode", default = "LOCAL_AXIS",
        items = scaleModeItems, update = propertyChanged)

    def create(self):
        self.newInput("Matrix List", "Matrices", "inMatrices", dataIsModified = self.modifiesOriginalList)
        self.newInput("Falloff", "Falloff", "falloff")

        if self.useScale:
            self.newVectorizedInput("Vector", "useScaleList",
                ("Scale", "scale", dict(value = (1, 1, 1))),
                ("Scales", "scales"))

        self.newOutput("Matrix List", "Matrices", "outMatrices")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "useTranslation", text = "Loc", icon = "MAN_TRANS")
        row.prop(self, "useRotation", text = "Rot", icon = "MAN_ROT")
        row.prop(self, "useScale", text = "Scale", icon = "MAN_SCALE")

    def drawAdvanced(self, layout):
        layout.prop(self, "scaleMode")

    def execute(self, Matrix4x4List matrices, Falloff falloff, *args):
        if len(args) == 0:
            return matrices

        cdef DoubleList influences = self.evaluateFalloff(matrices, falloff)

        if self.useScale:
            scaleMatrixList(matrices, self.scaleMode, self.getScales(args), influences)

        return matrices

    def evaluateFalloff(self, Matrix4x4List matrices, Falloff falloff):
        cdef FalloffEvaluator evaluator = falloff.getEvaluator("Transformation Matrix")
        cdef Py_ssize_t i
        cdef DoubleList influences = DoubleList(length = len(matrices))
        for i in range(len(influences)):
            influences.data[i] = evaluator.evaluate(matrices.data + i, i)
        return influences

    def getScales(self, args):
        if self.useScale:
            return CDefaultList(Vector3DList, args[-1], (1, 1, 1))
        return None

    @property
    def modifiesOriginalList(self):
        return self.useRotation
