import bpy
from bpy.props import *
from mathutils import Vector
from ... events import propertyChanged
from ... data_structures import Vector3DList
from ... base_types import AnimationNode

class an_EdgesToPlanesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EdgesToPlanesNode"
    bl_label = "Edges to Planes"
    bl_width_default = 150

    calculateDirection = BoolProperty(
        name = "Calculate Direction",
        description = "Calculate a rectangle instead of a parallelogram (takes more time)",
        default = True, update = propertyChanged)

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Vector List", "Vertices", "vertices")
        self.newInput("Edge Indices List", "Edges", "edges")
        self.newInput("Float", "Width", "width", value = 0.01)
        self.newInput("Vector", "Up Vector", "upVector", value = (0.001, 0.001, 0.999), hide = True)

        self.newOutput("Vector List", "Vertices", "outVertices")
        self.newOutput("Polygon Indices List", "Polygons", "polygons")

    def draw(self, layout):
        layout.prop(self, "calculateDirection")
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, vertices, edges, width, upVector):
        try:
            self.errorMessage = ""
            return self.calculatePlanes(vertices, edges, width, upVector)
        except IndexError:
            self.errorMessage = "Missing vertices"
            return [], []


    def calculatePlanes(self, vertices, edges, width, upVector):
        newVertices = Vector3DList()
        polygons = []
        appendVertex = newVertices.append
        appendPolygon = polygons.append

        if self.calculateDirection:
            for index1, index2 in edges:
                start = vertices[index1]
                end = vertices[index2]
                offset = (start - end).cross(upVector).normalized() * width / 2
                appendVertex(start - offset)
                appendVertex(start + offset)
                appendVertex(end + offset)
                appendVertex(end - offset)
        else:
            offset = Vector((width / 2, 0, 0))
            for index1, index2 in edges:
                appendVertex(vertices[index1] - offset)
                appendVertex(vertices[index1] + offset)
                appendVertex(vertices[index2] + offset)
                appendVertex(vertices[index2] - offset)

        for i in range(0, len(edges) * 4, 4):
            appendPolygon((i, i + 1, i + 2, i + 3))
        return newVertices, polygons
