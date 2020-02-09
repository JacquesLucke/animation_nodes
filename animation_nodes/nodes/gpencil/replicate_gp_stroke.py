import bpy
from bpy.props import *
from mathutils import Matrix
from ... data_structures import GPStroke
from ... base_types import AnimationNode, VectorizedSocket

transformationTypeItems = [
    ("Matrix List", "Matrices", "", "NONE", 0),
    ("Vector List", "Vectors", "", "NONE", 1)
]

class ReplicateGPStrokeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReplicateGPStrokeNode"
    bl_label = "Replicate GP Stroke"

    useStrokeList: VectorizedSocket.newProperty()

    transformationType: EnumProperty(name = "Transformation Type", default = "Matrix List",
        items = transformationTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Strokes", "strokes")))

        self.newInput(self.transformationType, "Transformations", "transformations")

        self.newOutput("GPStroke List", "Strokes", "outStrokes")

    def draw(self, layout):
        layout.prop(self, "transformationType", text = "")

    def getExecutionFunctionName(self):
        if self.transformationType == "Matrix List":
            return "execute_MatrixList"
        elif self.transformationType == "Vector List":
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
