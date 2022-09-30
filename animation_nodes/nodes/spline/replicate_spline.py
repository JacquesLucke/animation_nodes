import bpy
from bpy.props import *
from mathutils import Matrix
from ... data_structures import Spline
from ... base_types import AnimationNode, VectorizedSocket

transformationTypeItems = [
    ("MATRIX_LIST", "Matrices", "", "NONE", 0),
    ("VECTOR_LIST", "Vectors", "", "NONE", 1)
]

class ReplicateSplineNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_ReplicateSplineNode"
    bl_label = "Replicate Spline"

    useSplineList: VectorizedSocket.newProperty()

    transformationType: EnumProperty(name = "Transformation Type", default = "MATRIX_LIST",
        items = transformationTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Splines", "splines")))

        if self.transformationType == "MATRIX_LIST":
            self.newInput("Matrix List", "Transformations", "transformations")
        else:
            self.newInput("Vector List", "Transformations", "transformations")

        self.newOutput("Spline List", "Splines", "outSplines")

    def draw(self, layout):
        layout.prop(self, "transformationType", text = "")

    def getExecutionFunctionName(self):
        if self.transformationType == "MATRIX_LIST":
            return "execute_MatrixList"
        elif self.transformationType == "VECTOR_LIST":
            return "execute_VectorList"

    def execute_MatrixList(self, splines, matrices):
        if isinstance(splines, Spline):
            splines = [splines]

        outSplines = []
        for matrix in matrices:
            for spline in splines:
                newSpline = spline.copy()
                newSpline.transform(matrix)
                outSplines.append(newSpline)
        return outSplines

    def execute_VectorList(self, splines, vectors):
        if isinstance(splines, Spline):
            splines = [splines]

        outSplines = []
        for vector in vectors:
            for spline in splines:
                newSpline = spline.copy()
                newSpline.transform(Matrix.Translation(vector))
                outSplines.append(newSpline)
        return outSplines
