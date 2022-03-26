import bpy
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import GPStroke, FloatList, VirtualDoubleList, Color, ColorList, VirtualColorList

class GPStrokeFromPointsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPStrokeFromPointsNode"
    bl_label = "GP Stroke From Points"
    errorHandlingType = "EXCEPTION"

    useStrengthList: VectorizedSocket.newProperty()
    usePressureList: VectorizedSocket.newProperty()
    useUVRotationList: VectorizedSocket.newProperty()
    useVertexColorList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Vector List", "Points", "vertices")
        self.newInput(VectorizedSocket("Float", "useStrengthList",
            ("Strength", "strength"), ("Strengths", "strengths")), value = 1)
        self.newInput(VectorizedSocket("Float", "usePressureList",
            ("Pressure", "pressure"), ("Pressures", "pressures")), value = 1)
        self.newInput(VectorizedSocket("Float", "useUVRotationList",
            ("UV-Rotation", "uvRotation"), ("UV-Rotations", "uvRotations")), hide = True)
        self.newInput(VectorizedSocket("Color", "useVertexColorList",
            ("Vertex Color", "vertexColor", dict(value = (0, 0, 0, 0))), ("Vertex Colors", "vertexColors")))
        self.newInput("Integer", "Line Width", "lineWidth", value = 250)
        self.newInput("Float", "Hardness", "hardness", value = 1)
        self.newInput("Boolean", "Cyclic", "useCyclic", value = False, hide = True)
        self.newInput("Text", "Start Cap Mode", "startCapMode", value = 'ROUND', hide = True)
        self.newInput("Text", "End Cap Mode", "endCapMode", value = 'ROUND', hide = True)
        self.newInput("Color", "Vertex Color Fill", "vertexColorFill", value = (0, 0, 0, 0), hide = True)
        self.newInput("Integer", "Material Index", "materialIndex", value = 0)
        self.newInput("Text", "Display Mode", "displayMode", value = '3DSPACE', hide = True)
        self.newOutput("GPStroke", "Stroke", "stroke")

    def execute(self, vertices, strengths, pressures, uvRotations, vertexColors, lineWidth, hardness,
                useCyclic, startCapMode, endCapMode, vertexColorFill, materialIndex, displayMode):

        amount = len(vertices)
        strengths = FloatList.fromValues(VirtualDoubleList.create(strengths, 1).materialize(amount))
        pressures = FloatList.fromValues(VirtualDoubleList.create(pressures, 1).materialize(amount))
        uvRotations = FloatList.fromValues(VirtualDoubleList.create(uvRotations, 0).materialize(amount))
        vertexColors = VirtualColorList.create(vertexColors, Color((0, 0, 0, 0))).materialize(amount)

        if startCapMode not in ['ROUND', 'FLAT']:
            self.raiseErrorMessage("The Start Cap Mode is invalid. \n\nPossible values for 'Start Cap Mode' are: 'ROUND', 'FLAT'")
        if endCapMode not in ['ROUND', 'FLAT']:
            self.raiseErrorMessage("The End Cap Mode is invalid. \n\nPossible values for 'End Cap Mode' are: 'ROUND', 'FLAT'")
        if displayMode not in ['SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE']:
            self.raiseErrorMessage("The Display Mode is invalid. \n\nPossible values for 'Display Mode' are: 'SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE'")

        return GPStroke(vertices, strengths, pressures, uvRotations, vertexColors, lineWidth, hardness,
                        useCyclic, startCapMode, endCapMode, vertexColorFill, materialIndex, displayMode)
