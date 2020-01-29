import bpy
from ... data_structures import DoubleList, Vector3DList
from ... base_types import AnimationNode, VectorizedSocket

class GPencilStrokeInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilStrokeInputNode"
    bl_label = "GPencil Stroke Input"

    def create(self):
        self.newInput("Stroke", "Stroke", "stroke")

        self.newOutput("Vector List", "Points", "vertices")
        self.newOutput("Float List", "Strengths", "strengths")
        self.newOutput("Float List", "Pressures", "pressures")
        self.newOutput("Float List", "UV-Rotations", "uvRotations")
        self.newOutput("Float", "Line Width", "lineWidth")
        self.newOutput("Boolean", "Cyclic", "drawCyclic")
        self.newOutput("Boolean", "Start Cap", "startCapMode")
        self.newOutput("Boolean", "End Cap", "endCapMode")
        self.newOutput("Integer", "Material Index", "materialIndex")

        visibleOutputs = ("Points", "Strengths", "Pressures", "Line Width", "Material Index")
        for socket in self.outputs:
            socket.hide = socket.name not in visibleOutputs

    def execute(self, stroke):
        if stroke is None:
            return Vector3DList(), DoubleList(), DoubleList(), DoubleList(), 0, False, False, False, 0

        if stroke.start_cap_mode == "ROUND":
            startCapMode = False
        else:
            startCapMode = True

        if stroke.end_cap_mode == "ROUND":
            endCapMode = False
        else:
            endCapMode = True
        return stroke.vertices, stroke.strength, stroke.pressure, stroke.uv_rotation,\
        stroke.line_width, stroke.draw_cyclic, startCapMode, endCapMode, stroke.material_index
