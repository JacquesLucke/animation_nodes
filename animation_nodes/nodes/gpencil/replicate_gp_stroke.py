import bpy
from bpy.props import *
from mathutils import Matrix
from ... data_structures import GPStroke
from ... base_types import AnimationNode, VectorizedSocket

transformationTypeItems = [
    ("MATRIX_LIST", "Matrices", "", "NONE", 0),
    ("VECTOR_LIST", "Vectors", "", "NONE", 1)
]

class ReplicateGPStrokeNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_ReplicateGPStrokeNode"
    bl_label = "Replicate GP Stroke"

    useStrokeList: VectorizedSocket.newProperty()

    transformationType: EnumProperty(name = "Transformation Type", default = "MATRIX_LIST",
        items = transformationTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "strokes"), ("Strokes", "strokes")), dataIsModified = True)

        if self.transformationType == "MATRIX_LIST":
            self.newInput("Matrix List", "Transformations", "transformations")
        else:
            self.newInput("Vector List", "Transformations", "transformations")

        self.newOutput("GPStroke List", "Strokes", "outStrokes")

    def draw(self, layout):
        layout.prop(self, "transformationType", text = "")

    def getExecutionFunctionName(self):
        if self.transformationType == "MATRIX_LIST":
            return "execute_MatrixList"
        elif self.transformationType == "VECTOR_LIST":
            return "execute_VectorList"

    def execute_MatrixList(self, strokes, matrices):
        if isinstance(strokes, GPStroke):
            strokes = [strokes]

        outStrokes = []
        for matrix in matrices:
            for stroke in strokes:
                newStroke = stroke.copy()
                newStroke.vertices.transform(matrix)
                outStrokes.append(newStroke)
        return outStrokes

    def execute_VectorList(self, strokes, vectors):
        if isinstance(strokes, GPStroke):
            strokes = [strokes]

        outStrokes = []
        for vector in vectors:
            for stroke in strokes:
                newStroke = stroke.copy()
                newStroke.vertices.transform(Matrix.Translation(vector))
                outStrokes.append(newStroke)
        return outStrokes
