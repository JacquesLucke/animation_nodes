import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... data_structures cimport FalloffEvaluator
from ... math cimport (Matrix4, Vector3, Euler3, Matrix4x4List, toVector3, toEuler3,
                       multMatrix4, toPyMatrix4, setTranslationRotationScaleMatrix,
                       convertMatrix4ToMatrix3, multMatrix3, setRotationScaleMatrix,
                       convertMatrix3ToMatrix4, Matrix3, setScaleMatrix, setRotationMatrix,
                       setTranslationMatrix, transformVec3AsDirection, multMatrix3Parts)

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
    scaleMode = EnumProperty(name = "Scale Mode", default = "LOCAL",
        items = localGlobalItems, update = propertyChanged)

    axisRotation = BoolProperty(name = "Axis Rotation", default = False,
        update = propertyChanged, description = "Use world center as rotation pivot")
    axisScale = BoolProperty(name = "Axis Scale", default = False,
        update = propertyChanged, description = "Use world center as scale pivot")

    def create(self):
        self.newInput("Matrix List", "Transformations", "transformations", dataIsModified = True)
        self.newInput("Falloff", "Falloff", "falloff", value = 1)
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
            #OffsetMatrixFunction offsetFunction = getOffsetFunction(self)
            Vector3 _translation = toVector3(translation)
            Euler3 _rotation = toEuler3(rotation)
            Vector3 _scale = toVector3(scale)
            Vector3 localTranslation, localScale
            Euler3 localRotation
            Matrix4 result
            double influence
            long i

        cdef:
            bint axisRotation = self.axisRotation
            bint axisScale = self.axisScale
            bint useLocalTranslation = self.translationMode == "LOCAL"
            bint useLocalRotation = self.rotationMode == "LOCAL"
            bint useLocalScale = self.scaleMode == "LOCAL"

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

            applyTransformation(&result, transformations.data + i,
                &localTranslation, &localRotation, &localScale,
                useLocalTranslation, useLocalRotation, useLocalScale,
                axisRotation, axisScale)

            transformations.data[i] = result

        return transformations

cdef void applyTransformation(Matrix4* target, Matrix4* source,
                     Vector3* translation, Euler3* rotation, Vector3* scale,
                     bint localTranslation, bint localRotation, bint localScale,
                     bint axisRotation, bint axisScale):

    cdef Matrix4 afterScale, afterRotation
    applyScale(&afterScale, source, scale, localScale, axisScale)
    applyRotation(&afterRotation, &afterScale, rotation, localRotation, axisRotation)
    applyTranslation(target, &afterRotation, source, translation, localTranslation)

cdef void applyScale(Matrix4* target, Matrix4* source,
                     Vector3* scale, bint localScale, bint axisScale):
    cdef Matrix4 scaleMatrix
    setScaleMatrix(&scaleMatrix, scale)
    if localScale:
        if axisScale:
            multMatrix4(target, source, &scaleMatrix)
        else:
            multMatrix3Parts(target, source, &scaleMatrix, keepFirst = True)
    else:
        if axisScale:
            multMatrix4(target, &scaleMatrix, source)
        else:
            multMatrix3Parts(target, &scaleMatrix, source, keepFirst = False)

cdef void applyRotation(Matrix4* target, Matrix4* source,
                        Euler3* rotation, bint localRotation, bint axisRotation):
    cdef Matrix4 rotationMatrix
    setRotationMatrix(&rotationMatrix, rotation)
    if localRotation:
        if axisRotation:
            multMatrix4(target, source, &rotationMatrix)
        else:
            multMatrix3Parts(target, source, &rotationMatrix, keepFirst = True)
    else:
        if axisRotation:
            multMatrix4(target, &rotationMatrix, source)
        else:
            multMatrix3Parts(target, &rotationMatrix, source, keepFirst = False)

cdef void applyTranslation(Matrix4* target, Matrix4* source, Matrix4* original,
                           Vector3* translation, bint localTranslation):
    cdef Matrix4 translationMatrix
    cdef Vector3 offsetTranslation
    if localTranslation:
        transformVec3AsDirection(&offsetTranslation, translation, original)
    else:
        offsetTranslation = translation[0]
    target[0] = source[0]
    target.a14 += offsetTranslation.x
    target.a24 += offsetTranslation.y
    target.a34 += offsetTranslation.z
