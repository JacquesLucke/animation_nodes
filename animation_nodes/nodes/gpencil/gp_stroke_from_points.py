import bpy
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import GPStroke, VirtualDoubleList

class GPStrokeFromPointsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPStrokeFromPointsNode"
    bl_label = "GP Stroke From Points"

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
        self.newOutput("GPStroke", "Stroke", "stroke")

        visibleInputs = ("Points", "Strength", "Strengths", "Pressure", "Pressures", "Line Width", "Material Index")
        for socket in self.inputs:
            socket.hide = socket.name not in visibleInputs

    def execute(self, vertices, strengths, pressures, uvRotations, lineWidth, drawCyclic, startCapMode, endCapMode, materialIndex):
        amount = len(vertices)
        stroke = GPStroke()

        strengths = VirtualDoubleList.create(strengths, 1).materialize(amount)
        pressures = VirtualDoubleList.create(pressures, 1).materialize(amount)
        uvRotations = VirtualDoubleList.create(uvRotations, 0).materialize(amount)

        stroke.vertices = vertices
        stroke.strengths = strengths
        stroke.pressures = pressures
        stroke.uvRotations = uvRotations
        stroke.lineWidth = lineWidth
        stroke.drawCyclic = drawCyclic

        if startCapMode:
            stroke.startCapMode = "FLAT"
        else:
            stroke.startCapMode = "ROUND"

        if endCapMode:
            stroke.endCapMode = "FLAT"
        else:
            stroke.endCapMode = "ROUND"

        stroke.materialIndex = materialIndex
        return stroke
