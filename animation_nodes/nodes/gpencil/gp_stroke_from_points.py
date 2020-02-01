import bpy
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import GPStroke, VirtualDoubleList

class GPStrokeFromPointsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPStrokeFromPointsNode"
    bl_label = "GP Stroke From Points"
    errorHandlingType = "EXCEPTION"

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
            ("UV-Rotation", "uvRotation"), ("UV-Rotations", "uvRotations")), hide = True)
        self.newInput("Float", "Line Width", "lineWidth", value = 250)
        self.newInput("Boolean", "Cyclic", "drawCyclic", value = False, hide = True)
        self.newInput("Text", "Start Cap", "startCapMode", value = 'ROUND', hide = True)
        self.newInput("Text", "End Cap", "endCapMode", value = 'ROUND', hide = True)
        self.newInput("Integer", "Material Index", "materialIndex", value = 0)
        self.newInput("Text", "Display Mode", "displayMode", value = 'SCREEN', hide = True)
        self.newOutput("GPStroke", "Stroke", "stroke")

    def execute(self, vertices, strengths, pressures, uvRotations, lineWidth, drawCyclic,
                startCapMode, endCapMode, materialIndex, displayMode):

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

        if startCapMode not in ['ROUND', 'FLAT']:
            self.raiseErrorMessage("The Start Cap mode is invalid. \n\nPossible values for 'Start Cap Mode' are: 'REGULAR', 'FLAT'")
        stroke.startCapMode = startCapMode
        if endCapMode not in ['ROUND', 'FLAT']:
            self.raiseErrorMessage("The End Cap mode is invalid. \n\nPossible values for 'End Cap Mode' are: 'REGULAR', 'FLAT'")
        stroke.endCapMode = endCapMode

        stroke.materialIndex = materialIndex
        stroke.displayMode = displayMode
        return stroke
