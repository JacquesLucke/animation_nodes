import bpy
from mathutils import Matrix
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualPyList, VirtualMatrix4x4List, Spline

class TransformSplineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformSplineNode"
    bl_label = "Transform Spline"

    useSplineList: VectorizedSocket.newProperty()
    useMatrixList: VectorizedSocket.newProperty()

    def create(self):
        socket = self.newInput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline"), ("Splines", "splines")))
        socket.dataIsModified = not self.useMatrixList
        socket.defaultDrawType = "PROPERTY_ONLY"

        self.newInput(VectorizedSocket("Matrix", "useMatrixList",
            ("Matrix", "matrix"), ("Matrices", "matrices")))

        self.newOutput(VectorizedSocket("Spline", ["useSplineList", "useMatrixList"],
            ("Spline", "spline"), ("Splines", "splines")))

    def getExecutionFunctionName(self):
        if self.useSplineList:
            if self.useMatrixList:
                return "execute_MultipleSpline_MultipleMatrix"
            else:
                return "execute_MultipleSpline_SingleMatrix"
        else:
            if self.useMatrixList:
                return "execute_SingleSpline_MultipleMatrix"
            else:
                return "execute_SingleSpline_SingleMatrix"

    def execute_SingleSpline_SingleMatrix(self, spline, matrix):
        spline.transform(matrix)
        return spline

    def execute_SingleSpline_MultipleMatrix(self, spline, matrices):
        outSplines = []
        for matrix in matrices:
            s = spline.copy()
            s.transform(matrix)
            outSplines.append(s)
        return outSplines

    def execute_MultipleSpline_SingleMatrix(self, splines, matrix):
        for spline in splines:
            spline.transform(matrix)
        return splines

    def execute_MultipleSpline_MultipleMatrix(self, splines, matrices):
        _splines = VirtualPyList.create(splines, Spline())
        _matrices = VirtualMatrix4x4List.create(matrices, Matrix.Identity(4))
        amount = VirtualPyList.getMaxRealLength(_splines, _matrices)
        outSplines = []
        for i in range(amount):
            s = _splines[i].copy()
            s.transform(_matrices[i])
            outSplines.append(s)
        return outSplines
