import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... data_structures cimport FalloffEvaluator
from ... math cimport (Matrix4, Vector3, Euler3, Matrix4x4List, toVector3, toEuler3,
                       multMatrix4, toPyMatrix4, setTranslationRotationScaleMatrix,
                       convertMatrix4ToMatrix3, multMatrix3, setRotationScaleMatrix,
                       convertMatrix3ToMatrix4, Matrix3)

ctypedef void (*OffsetMatrixFunction)(Matrix4* target, Matrix4* source,
                        Vector3* translation, Euler3* rotation, Vector3* scale)

localGlobalItems = [
    ("LOCAL", "Local", "", "NONE", 0),
    ("GLOBAL", "Global", "", "NONE", 1)]

class OffsetTransformationsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OffsetTransformationsNode"
    bl_label = "Offset Transformations"

    errorMessage = StringProperty()

    translationMode = EnumProperty(name = "Translation Mode", default = "GLOBAL",
        items = localGlobalItems, update = propertyChanged)
    rotationMode = EnumProperty(name = "Rotation Mode", default = "GLOBAL",
        items = localGlobalItems, update = propertyChanged)
    scaleMode = EnumProperty(name = "Scale Mode", default = "GLOBAL",
        items = localGlobalItems, update = propertyChanged)

    axisRotation = BoolProperty(name = "Axis Rotation", default = False,
        update = propertyChanged, description = "Use world center as rotation pivot")
    axisScale = BoolProperty(name = "Axis Scale", default = False,
        update = propertyChanged, description = "Use world center as scale pivot")

    def create(self):
        self.newInput("Matrix List", "Transformations", "transformations", dataIsModified = True)
        self.newInput("Falloff", "Falloff", "falloff")
        self.newInput("Vector", "Translation", "translation")
        self.newInput("Euler", "Rotation", "rotation")
        self.newInput("Vector", "Scale", "scale", value = (1, 1, 1))
        self.newOutput("Matrix List", "Transformations", "transformations")

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
        row.prop(self, "axisRotation", icon = "MANIPUL", text = "")
        row = col.row(align = True)
        row.label("Scale")
        row.prop(self, "scaleMode", expand = True)
        row.prop(self, "axisScale", icon = "MANIPUL", text = "")

    def execute(self, Matrix4x4List transformations, falloff, translation, rotation, scale):
        cdef:
            FalloffEvaluator evaluator = FalloffEvaluator.create(falloff, "Transformation Matrix")
            OffsetMatrixFunction offsetFunction = getOffsetFunction(self)
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

            offsetFunction(&result, transformations.data + i,
                &localTranslation, &localRotation, &localScale)

            transformations.data[i] = result

        return transformations

cdef OffsetMatrixFunction getOffsetFunction(node):
    raise NotImplementedError()
    if name == "APPLY_BEFORE":
        return applyBefore
    if name == "APPLY_AFTER":
        return applyAfter
    if name == "ADVANCED":
        return applyAdvanced

cdef void applyBefore(Matrix4* target, Matrix4* source,
                      Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef Matrix4 matrix
    setTranslationRotationScaleMatrix(&matrix, translation, rotation, scale)
    multMatrix4(target, source, &matrix)

cdef void applyAfter(Matrix4* target, Matrix4* source,
                     Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef Matrix4 matrix
    setTranslationRotationScaleMatrix(&matrix, translation, rotation, scale)
    multMatrix4(target, &matrix, source)

cdef void applyAdvanced(Matrix4* target, Matrix4* source,
                     Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef Matrix3 _source
    convertMatrix4ToMatrix3(&_source, source)
    cdef Matrix3 rotationScale
    setRotationScaleMatrix(&rotationScale, rotation, scale)
    cdef Matrix3 newRotationScale
    multMatrix3(&newRotationScale, &rotationScale, &_source)
    convertMatrix3ToMatrix4(target, &newRotationScale)
    target.a14 = source.a14 + translation.x
    target.a24 = source.a24 + translation.y
    target.a34 = source.a34 + translation.z
