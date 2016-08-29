import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... data_structures cimport FalloffEvaluator, createFalloffEvaluator
from ... math cimport Matrix4, Vector3, Matrix4x4List, toVector3, setTranslationMatrix4, multMatrix4

class OffsetTransformationsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OffsetTransformationsNode"
    bl_label = "Offset Transformations"

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Matrix List", "Transformations", "transformations", dataIsModified = True)
        self.newInput("Vector", "Offset", "offset")
        self.newInput("Falloff", "Falloff", "falloff")
        self.newOutput("Matrix List", "Transformations", "transformations")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, Matrix4x4List transformations, offset, falloff):
        cdef:
            FalloffEvaluator evaluator = createFalloffEvaluator(falloff, "Transformation Matrix")
            Matrix4* _transformations = <Matrix4*>transformations.base.data
            Vector3 _offset, localOffset
            Matrix4 matrix, result
            double influence
            long i

        if evaluator is None:
            self.errorMessage = "Falloff cannot be evaluated for matrices"
            return transformations

        toVector3(&_offset, offset)
        for i in range(len(transformations)):
            influence = evaluator.evaluate(_transformations + i, i)
            localOffset.x = _offset.x * influence
            localOffset.y = _offset.y * influence
            localOffset.z = _offset.z * influence
            setTranslationMatrix4(&matrix, &localOffset)
            multMatrix4(&result, _transformations + i, &matrix)
            _transformations[i] = result

        return transformations
