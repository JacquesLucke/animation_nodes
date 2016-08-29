import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... data_structures cimport FalloffEvaluator, createFalloffEvaluator
from ... math cimport Matrix4, Vector3, Matrix4x4List, toVector3, setTranslationScaleMatrix4, multMatrix4

class OffsetTransformationsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OffsetTransformationsNode"
    bl_label = "Offset Transformations"

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Matrix List", "Transformations", "transformations", dataIsModified = True)
        self.newInput("Falloff", "Falloff", "falloff")
        self.newInput("Vector", "Translation", "translation")
        self.newInput("Vector", "Scale", "scale", value = (1, 1, 1))
        self.newOutput("Matrix List", "Transformations", "transformations")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, Matrix4x4List transformations, falloff, translation, scale):
        cdef:
            FalloffEvaluator evaluator = createFalloffEvaluator(falloff, "Transformation Matrix")
            Matrix4* _transformations = <Matrix4*>transformations.base.data
            Vector3 _translation, localTranslation
            Vector3 _scale, localScale
            Matrix4 matrix, result
            double influence
            long i

        if evaluator is None:
            self.errorMessage = "Falloff cannot be evaluated for matrices"
            return transformations

        toVector3(&_translation, translation)
        toVector3(&_scale, scale)
        for i in range(len(transformations)):
            influence = evaluator.evaluate(_transformations + i, i)

            localTranslation.x = _translation.x * influence
            localTranslation.y = _translation.y * influence
            localTranslation.z = _translation.z * influence

            localScale.x = _scale.x * influence + (1 - influence)
            localScale.y = _scale.y * influence + (1 - influence)
            localScale.z = _scale.z * influence + (1 - influence)

            setTranslationScaleMatrix4(&matrix, &localTranslation, &localScale)
            multMatrix4(&result, _transformations + i, &matrix)
            _transformations[i] = result

        return transformations
