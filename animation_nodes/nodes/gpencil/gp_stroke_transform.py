import bpy
from ... math import Matrix
from ... data_structures import VirtualMatrix4x4List
from ... base_types import AnimationNode, VectorizedSocket

class GPStrokeTransformNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPStrokeTransformNode"
    bl_label = "GP Stroke Transform"

    useStrokeList: VectorizedSocket.newProperty()
    useMatrixList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Matrix", "useMatrixList",
            ("Matrix", "matrix"), ("Matices", "matrices")))
        self.newOutput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useMatrixList:
            return "executeListList"
        elif self.useStrokeList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, stroke, matrix):
        if matrix is not None:
            self.strokeTransfom(stroke, matrix)
        return stroke

    def executeList(self, strokes, matrix):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            if matrix is not None:
                self.strokeTransfom(stroke, matrix)
        return strokes

    def executeListList(self, strokes, matrices):
        if len(strokes) == 0 or len(matrices) == 0: return strokes
        matrices = VirtualMatrix4x4List.create(matrices, Matrix())
        for i, stroke in enumerate(strokes):
            if matrices[i] is not None:
                self.strokeTransfom(stroke, matrices[i])
        return strokes

    def strokeTransfom(self, stroke, matrix):
        return stroke.vertices.transform(matrix)
