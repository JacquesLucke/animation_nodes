import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, AutoSelectVectorization
from ... data_structures cimport (Vector3DList, EulerList, Matrix4x4List,
                                  FalloffEvaluator, CListMock)
from ... algorithms.transform_matrix cimport (
    allocateMatrixTransformerFromCListMocks, freeMatrixTransformer, TransformMatrixFunction)
from ... math cimport Matrix4, Vector3, Euler3, toVector3, toEuler3
from .. falloff.invert_falloff import InvertFalloff

localGlobalItems = [
    ("LOCAL", "Local", "", "NONE", 0),
    ("GLOBAL", "Global", "", "NONE", 1)]

specifiedStateItems = [
    ("START", "Start", "", "Given matrices set the start state", 0),
    ("END", "End", "", "Given matrices set the end state", 1)
]

class OffsetMatricesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OffsetMatricesNode"
    bl_label = "Offset Matrices"

    errorMessage = StringProperty()

    specifiedState = EnumProperty(name = "Specified State", default = "START",
        description = "Specify if the given matrices are the start or end state",
        items = specifiedStateItems, update = propertyChanged)

    translationMode = EnumProperty(name = "Translation Mode", default = "GLOBAL",
        items = localGlobalItems, update = propertyChanged)
    rotationMode = EnumProperty(name = "Rotation Mode", default = "GLOBAL",
        items = localGlobalItems, update = propertyChanged)
    scaleMode = EnumProperty(name = "Scale Mode", default = "LOCAL",
        items = localGlobalItems, update = propertyChanged)

    originAsRotationPivot = BoolProperty(name = "Origin Rotation", default = False,
        update = propertyChanged, description = "Use world center as rotation pivot")
    originAsScalePivot = BoolProperty(name = "Origin Scale", default = False,
        update = propertyChanged, description = "Use world center as scale pivot")

    useTranslationList = BoolProperty(update = AnimationNode.refresh)
    useRotationList = BoolProperty(update = AnimationNode.refresh)
    useScaleList = BoolProperty(update = AnimationNode.refresh)

    def create(self):
        self.newInput("Matrix List", "Matrices", "inMatrices")
        self.newInput("Falloff", "Falloff", "falloff", value = 1)

        self.newInputGroup(self.useTranslationList,
            ("Vector", "Translation", "translation"),
            ("Vector List", "Translations", "translations"))

        self.newInputGroup(self.useRotationList,
            ("Euler", "Rotation", "rotation"),
            ("Euler List", "Rotations", "rotations"))

        self.newInputGroup(self.useScaleList,
            ("Vector", "Scale", "scale", {"value" : (1, 1, 1)}),
            ("Vector List", "Scales", "scales"))

        self.newOutput("Matrix List", "Matrices", "outMatrices")

        vectorization = AutoSelectVectorization()
        vectorization.input(self, "useTranslationList", self.inputs[2])
        vectorization.input(self, "useRotationList", self.inputs[3])
        vectorization.input(self, "useScaleList", self.inputs[4])
        self.newSocketEffect(vectorization)

    def draw(self, layout):
        layout.prop(self, "specifiedState", expand = True)
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawAdvanced(self, layout):
        col = layout.column(align = False)
        row = col.row(align = True)
        row.label("Translation")
        row.prop(self, "translationMode", expand = True)
        row = col.row(align = True)
        row.label("Rotation")
        row.prop(self, "rotationMode", expand = True)
        row.prop(self, "originAsRotationPivot", icon = "MANIPUL", text = "")
        row = col.row(align = True)
        row.label("Scale")
        row.prop(self, "scaleMode", expand = True)
        row.prop(self, "originAsScalePivot", icon = "MANIPUL", text = "")

    def execute(self, Matrix4x4List inMatrices, falloff, translations, rotations, scales):
        cdef:
            CListMock _translations = CListMock(Vector3DList, translations, (0, 0, 0))
            CListMock _rotations = CListMock(EulerList, rotations, (0, 0, 0))
            CListMock _scales = CListMock(Vector3DList, scales, (1, 1, 1))

            Matrix4x4List outMatrices = Matrix4x4List(length = inMatrices.length)
            FalloffEvaluator evaluator

        if self.specifiedState == "END": falloff = InvertFalloff(falloff)
        try: evaluator = falloff.getEvaluator("Transformation Matrix")
        except:
            self.errorMessage = "Falloff cannot be evaluated for matrices"
            return inMatrices.copy()

        cdef:
            TransformMatrixFunction transformFunction
            void* transformSettings

        allocateMatrixTransformerFromCListMocks(&transformFunction, &transformSettings,
            _translations, self.translationMode == "LOCAL",
            _rotations, self.rotationMode == "LOCAL", not self.originAsRotationPivot,
            _scales, self.scaleMode == "LOCAL", not self.originAsScalePivot)

        cdef:
            long i
            double influence

            Vector3* translation
            Euler3* rotation
            Vector3* scale

            Vector3 localTranslation
            Euler3 localRotation
            Vector3 localScale

        for i in range(outMatrices.length):
            influence = evaluator.evaluate(inMatrices.data + i, i)

            translation = <Vector3*>_translations.get(i)
            localTranslation.x = translation.x * influence
            localTranslation.y = translation.y * influence
            localTranslation.z = translation.z * influence

            rotation = <Euler3*>_rotations.get(i)
            localRotation.order = rotation.order
            localRotation.x = rotation.x * influence
            localRotation.y = rotation.y * influence
            localRotation.z = rotation.z * influence

            scale = <Vector3*>_scales.get(i)
            localScale.x = scale.x * influence + (1 - influence)
            localScale.y = scale.y * influence + (1 - influence)
            localScale.z = scale.z * influence + (1 - influence)

            transformFunction(transformSettings,
                outMatrices.data + i,
                inMatrices.data + i,
                &localTranslation, &localRotation, &localScale)

        freeMatrixTransformer(transformFunction, transformSettings)
        return outMatrices
