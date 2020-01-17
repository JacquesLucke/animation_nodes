import bpy
from ... base_types import AnimationNode
from ... data_structures import DoubleList, Vector3DList

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
        if stroke is None:
            return 0, Vector3DList(), DoubleList(), DoubleList(), DoubleList(), 0, False, False, False, 0

        vectors = stroke.vectors

        if stroke.start_cap_mode == "ROUND":
            startCapMode = False
        else:
            startCapMode = True

        if stroke.end_cap_mode == "ROUND":
            endCapMode = False
        else:
            endCapMode = True
        return len(vectors), vectors, stroke.strength, stroke.pressure, stroke.uv_rotation,\
            stroke.line_width, stroke.draw_cyclic, startCapMode, endCapMode, stroke.material_index
