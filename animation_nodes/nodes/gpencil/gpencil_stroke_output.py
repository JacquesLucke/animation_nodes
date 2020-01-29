import bpy
from ... data_structures import Stroke, VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class GPencilStrokeOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilStrokeOutputNode"
    bl_label = "GPencil Stroke Output"

    useStrengthsList: VectorizedSocket.newProperty()
    usePressuresList: VectorizedSocket.newProperty()
    useUVRotationsList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Vector List", "Points", "vertices")
        self.newInput(VectorizedSocket("Float", "useStrengthsList",
            ("Strength", "strength"), ("Strengths", "strengths")), value = 1)
        self.newInput(VectorizedSocket("Float", "usePressuresList",
            ("Pressure", "pressure"), ("Pressures", "pressures")), value = 1)
        self.newInput(VectorizedSocket("Float", "useUVRotationsList",
            ("UV-Rotation", "uvRotation"), ("UV-Rotations", "uvRotations")))
        self.newInput("Float", "Line Width", "lineWidth", value = 250)
        self.newInput("Boolean", "Cyclic", "drawCyclic", value = False)
        self.newInput("Boolean", "Start Cap", "startCapMode", value = False)
        self.newInput("Boolean", "End Cap", "endCapMode", value = False)
        self.newInput("Integer", "Material Index", "materialIndex", value = 0)
        self.newOutput("Stroke", "Stroke", "stroke")

        visibleInputs = ("Points", "Strength", "Strengths", "Pressure", "Pressures", "Line Width", "Material Index")
        for socket in self.inputs:
            socket.hide = socket.name not in visibleInputs

    def execute(self, vertices, strengths, pressures, uvRotations, lineWidth, drawCyclic, startCapMode, endCapMode, materialIndex):
        amount = len(vertices)
        stroke = Stroke()

        strengths = VirtualDoubleList.create(strengths, 1).materialize(amount)
        pressures = VirtualDoubleList.create(pressures, 1).materialize(amount)
        uvRotations = VirtualDoubleList.create(uvRotations, 0).materialize(amount)

        stroke.vertices = vertices
        stroke.strength = strengths
        stroke.pressure = pressures
        stroke.uv_rotation = uvRotations
        stroke.line_width = lineWidth
        stroke.draw_cyclic = drawCyclic

        if startCapMode:
            stroke.start_cap_mode = "FLAT"
        else:
            stroke.start_cap_mode = "ROUND"

        if endCapMode:
            stroke.end_cap_mode = "FLAT"
        else:
            stroke.end_cap_mode = "ROUND"

        stroke.material_index = materialIndex
        return stroke
