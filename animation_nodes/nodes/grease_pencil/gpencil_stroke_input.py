import bpy
from ... base_types import AnimationNode
from .. vector.c_utils import combineVectorList
from ... data_structures import DoubleList, VirtualDoubleList

class GPencilStrokeInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilStrokeInputNode"
    bl_label = "GPencil Stroke Input"

    def create(self):
        self.newInput("Stroke", "Stroke", "stroke")

        self.newOutput("Integer", "Total Points", "totalPoints")
        self.newOutput("Vector List", "Points", "vectors")
        self.newOutput("Float List", "Strengths", "strengths")
        self.newOutput("Float List", "Pressures", "pressures")
        self.newOutput("Float List", "UV-Rotations", "uvRotations")
        self.newOutput("Float", "Line Width", "lineWidth")
        self.newOutput("Boolean", "Cyclic", "drawCyclic")
        self.newOutput("Boolean", "Start Cap", "startCapMode")
        self.newOutput("Boolean", "End Cap", "endCapMode")
        self.newOutput("Integer", "Material Index", "materialIndex")

        visibleOutputs = ("Total Points", "Points")
        for socket in self.outputs:
            socket.hide = socket.name not in visibleOutputs

    def execute(self, stroke):
        xVectors = []
        yVectors = []
        zVectors = []
        totalPoints = 0
        strengths = []
        pressures = []
        uvRotations = []
        vectors = self.createVectorList(DoubleList.fromValues(xVectors), DoubleList.fromValues(yVectors), DoubleList.fromValues(zVectors))
        if stroke is None: return totalPoints, vectors, DoubleList.fromValues(strengths), DoubleList.fromValues(pressures), DoubleList.fromValues(uvRotations), 0, False, False, False, 0

        totalPoints = len(stroke.vectors)
        if totalPoints == 0: return totalPoints, vectors, DoubleList.fromValues(strengths), DoubleList.fromValues(pressures), DoubleList.fromValues(uvRotations), 0, False, False, False, 0
        if stroke.start_cap_mode == "ROUND":
            startCapMode = False
        else:
            startCapMode = True

        if stroke.end_cap_mode == "ROUND":
            endCapMode = False
        else:
            endCapMode = True
        return totalPoints, stroke.vectors, DoubleList.fromValues(stroke.strength), DoubleList.fromValues(stroke.pressure), DoubleList.fromValues(stroke.uv_rotation), stroke.line_width, stroke.draw_cyclic, startCapMode, endCapMode, stroke.material_index

    def createVectorList(self, x, y, z):
        x, y, z = VirtualDoubleList.createMultiple((x, 0), (y, 0), (z, 0))
        amount = VirtualDoubleList.getMaxRealLength(x, y, z)
        return combineVectorList(amount, x, y, z)
