import bpy
from ... math import Matrix
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualMatrix4x4List, VirtualPyList, GPStroke

class TransformGPStrokeNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_TransformGPStrokeNode"
    bl_label = "Transform GP Stroke"

    useStrokeList: VectorizedSocket.newProperty()
    useMatrixList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Matrix", "useMatrixList",
            ("Matrix", "matrix"), ("Matices", "matrices")))
        self.newOutput(VectorizedSocket("GPStroke", ["useStrokeList", "useMatrixList"],
            ("Stroke", "stroke"), ("Strokes", "strokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList or self.useMatrixList:
            return "execute_StrokeList_MatrixList"
        else:
            return "execute_Stroke_Matrix"

    def execute_Stroke_Matrix(self, stroke, matrix):
        if matrix is not None:
            self.transformStroke(stroke, matrix)
        return stroke

    def execute_StrokeList_MatrixList(self, strokes, matrices):
        _strokes = VirtualPyList.create(strokes, GPStroke())
        _matrices = VirtualMatrix4x4List.create(matrices, Matrix())
        amount = VirtualPyList.getMaxRealLength(_strokes, _matrices)

        outStrokes = []
        for i in range(amount):
            strokeNew = _strokes[i].copy()
            self.transformStroke(strokeNew, _matrices[i])
            outStrokes.append(strokeNew)
        return outStrokes

    def transformStroke(self, stroke, matrix):
        return stroke.vertices.transform(matrix)
