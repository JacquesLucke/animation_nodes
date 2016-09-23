import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures cimport FalloffEvaluator
from ... algorithms.transform_matrix cimport (
    allocateMatrixTransformer, freeMatrixTransformer, TransformMatrixFunction)
from ... math cimport (Matrix4, Vector3, Euler3, Matrix4x4List, toVector3, toEuler3)

localGlobalItems = [
    ("LOCAL", "Local", "", "NONE", 0),
    ("GLOBAL", "Global", "", "NONE", 1)]

class OffsetMatricesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OffsetMatricesNode"
    bl_label = "Offset Matrices"

    errorMessage = StringProperty()

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

    def create(self):
        self.newInput("Matrix List", "Matrices", "matrices")
        self.newInput("Falloff", "Falloff", "falloff", value = 1)
        self.newInput("Vector", "Translation", "translation")
        self.newInput("Euler", "Rotation", "rotation")
        self.newInput("Vector", "Scale", "scale", value = (1, 1, 1))
        self.newOutput("Matrix List", "Matrices", "matrices")

    def draw(self, layout):
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

    def execute(self, Matrix4x4List transformations, falloff, translation, rotation, scale):
        cdef:
            FalloffEvaluator evaluator = FalloffEvaluator.create(falloff, "Transformation Matrix")
            Vector3 _translation = toVector3(translation)
            Euler3 _rotation = toEuler3(rotation)
            Vector3 _scale = toVector3(scale)
            Vector3 localTranslation, localScale
            Euler3 localRotation
            Matrix4 result
            double influence
            long i

        if evaluator is None:
            self.errorMessage = "Falloff cannot be evaluated for matrices"
            return transformations

        cdef:
            TransformMatrixFunction transformFunction
            void* transformSettings

        allocateMatrixTransformer(&transformFunction, &transformSettings,
            &_translation, self.translationMode == "LOCAL",
            &_rotation, self.rotationMode == "LOCAL", not self.originAsRotationPivot,
            &_scale, self.scaleMode == "LOCAL", not self.originAsScalePivot)

        localRotation.order = _rotation.order

        for i in range(len(transformations)):
            influence = evaluator.evaluate(transformations.data + i, i)

            localTranslation.x = _translation.x * influence
            localTranslation.y = _translation.y * influence
            localTranslation.z = _translation.z * influence

            localRotation.x = _rotation.x * influence
            localRotation.y = _rotation.y * influence
            localRotation.z = _rotation.z * influence

            localScale.x = _scale.x * influence + (1 - influence)
            localScale.y = _scale.y * influence + (1 - influence)
            localScale.z = _scale.z * influence + (1 - influence)

            transformFunction(transformSettings, &result, transformations.data + i,
                &localTranslation, &localRotation, &localScale)

            transformations.data[i] = result

        freeMatrixTransformer(transformFunction, transformSettings)
        return transformations
