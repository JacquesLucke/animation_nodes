import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket
from . splines_from_edges_utils import splinesFromBranches, splinesFromEdges

algorithmTypeItems = [
    ("EDGE", "Spline Per Edge", "", "NONE", 0),
    ("BRANCH", "Spline Per Branch", "", "NONE", 1)
]
radiusTypeItems = [
    ("EDGE", "Radius per Edge", "", "NONE", 0),
    ("VERTEX", "Radius per Vertex", "", "NONE", 1)
]

class SplinesFromEdgesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplinesFromEdgesNode"
    bl_label = "Splines from Edges"
    errorHandlingType = "EXCEPTION"
    bl_width_default = 160

    algorithmType: EnumProperty(name = "Algorithm Type", default = "EDGE",
        description = "Choose the algorithm used for generating the splines",
        update = propertyChanged, items = algorithmTypeItems)

    radiusType: EnumProperty(name = "Radius Type", default = "EDGE",
        description = "Only important if there is a list of radii",
        update = propertyChanged, items = radiusTypeItems)

    useRadiusList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Vector List", "Vertices", "vertices", dataIsModified = True)
        self.newInput("Edge Indices List", "Edge Indices", "edgeIndices")

        self.newInput(VectorizedSocket("Float", "useRadiusList",
            ("Radius", "radii", dict(value = 0.1, minValue = 0)),
            ("Radii", "radii"),
            codeProperties = dict(default = 0.1)))

        self.newOutput("Spline List", "Splines", "splines")

    def draw(self, layout):
        layout.prop(self, "algorithmType", text = "")
        if self.algorithmType == "EDGE":
            layout.prop(self, "radiusType", text = "")

    def execute(self, vertices, edgeIndices, radii):
        if len(edgeIndices) == 0: return []
        if edgeIndices.getMaxIndex() >= len(vertices):
            self.raiseErrorMessage("Invalid Edge Indices.")

        radii = VirtualDoubleList.create(radii, 0.1)
        if self.algorithmType == "EDGE":
            return splinesFromEdges(vertices, edgeIndices, radii, self.radiusType)
        else:
            return splinesFromBranches(vertices, edgeIndices, radii)
