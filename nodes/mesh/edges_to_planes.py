import bpy
from mathutils import Vector
from ... base_types.node import AnimationNode
from ... events import propertyChanged

class an_EdgesToPlanes(bpy.types.Node, AnimationNode):
    bl_idname = "an_EdgesToPlanes"
    bl_label = "Edges to Planes"

    inputNames = { "Vertices" : "vertices",
                   "Edges" : "edges",
                   "Width" : "width",
                   "Up Vector" : "upVector" }

    outputNames = { "Vertices" : "vertices",
                    "Polygons" : "polygons" }

    calculateDirection = bpy.props.BoolProperty(
        name = "Calculate Direction",
        description = "Calculate a rectangle instead of a parallelogram (takes more time)",
        default = True, update = propertyChanged)

    def create(self):
        self.inputs.new("an_VectorListSocket", "Vertices")
        self.inputs.new("an_EdgeIndicesListSocket", "Edges")
        self.inputs.new("an_FloatSocket", "Width").value = 0.01
        socket = self.inputs.new("an_VectorSocket", "Up Vector")
        socket.value = (0.001, 0.001, 0.999)
        socket.hide = True
        self.outputs.new("an_VectorListSocket", "Vertices")
        self.outputs.new("an_PolygonIndicesListSocket", "Polygons")
        self.width += 10

    def draw_buttons(self, context, layout):
        layout.prop(self, "calculateDirection")

    def execute(self, vertices, edges, width, upVector):
        newVertices = []
        polygons = []

        if self.calculateDirection:
            for index1, index2 in edges:
                start = vertices[index1]
                end = vertices[index2]
                offset = (start - end).cross(upVector).normalized() * width / 2
                newVertices.append(start - offset)
                newVertices.append(start + offset)
                newVertices.append(end + offset)
                newVertices.append(end - offset)
        else:
            offset = Vector((width / 2, 0, 0))
            for index1, index2 in edges:
                newVertices.append(vertices[index1] - offset)
                newVertices.append(vertices[index1] + offset)
                newVertices.append(vertices[index2] + offset)
                newVertices.append(vertices[index2] - offset)

        for i in range(0, len(edges) * 4, 4):
            polygons.append((i, i + 1, i + 2, i + 3))
        return newVertices, polygons
