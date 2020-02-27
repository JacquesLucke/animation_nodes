import bpy
from bpy.props import *
from ... events import executionCodeChanged
from .. number.offset_number import offsetFloatList
from .. vector.offset_vector import offsetVector3DList
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualVector3DList, VirtualDoubleList

class OffsetGPStrokeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OffsetGPStrokeNode"
    bl_label = "Offset GP Stroke"
    errorHandlingType = "EXCEPTION"

    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        executionCodeChanged()

    useLocation: BoolProperty(update = checkedPropertiesChanged)
    useStrength: BoolProperty(update = checkedPropertiesChanged)
    usePressure: BoolProperty(update = checkedPropertiesChanged)
    useUVRotation: BoolProperty(update = checkedPropertiesChanged)

    useVectorList: VectorizedSocket.newProperty()
    useStrengthList: VectorizedSocket.newProperty()
    usePressureList: VectorizedSocket.newProperty()
    useUVRotationList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("GPStroke", "Stroke", "stroke", dataIsModified = True)
        self.newInput("Falloff", "Falloff", "falloff")
        self.newInput(VectorizedSocket("Vector", "useVectorList",
            ("Offset Location", "offsetLocations", dict(value = (0, 0, 1))),
            ("Offset Locations", "offsetLocations")))
        self.newInput(VectorizedSocket("Float", "useStrengthList",
            ("Offset Strength", "offsetStrength", dict(value = 1)),
            ("Offset Strengths", "offsetStrengths")))
        self.newInput(VectorizedSocket("Float", "usePressureList",
            ("Offset Pressure", "offsetPressure", dict(value = 1)),
            ("Offset Pressures", "offsetPressures")))
        self.newInput(VectorizedSocket("Float", "useUVRotationList",
            ("Offset UV-Rotation", "offsetUVRotation", dict(value = 1)),
            ("Offset UV-Rotations", "offsetUVRotations")))

        self.newOutput("GPStroke", "Stroke", "stroke")

        self.updateSocketVisibility()

    def draw(self, layout):
        col = layout.column()

        row = col.row()
        subrow = row.row(align = True)
        subrow.prop(self, "useLocation", text = "Location", toggle = True)
        subrow.prop(self, "useStrength", text = "Strength", toggle = True)

        row = col.row()
        subrow = row.row(align = True)
        subrow.prop(self, "usePressure", text = "Pressure", toggle = True)
        subrow.prop(self, "useUVRotation", text = "UVRotation", toggle = True)

    def updateSocketVisibility(self):
        self.inputs[2].hide = not self.useLocation
        self.inputs[3].hide = not self.useStrength
        self.inputs[4].hide = not self.usePressure
        self.inputs[5].hide = not self.useUVRotation

    def execute(self, stroke, falloff, offsetLocations, offsetStrengths, offsetPressures, offsetUVRotations):
        if not any((self.useLocation, self.useStrength, self.usePressure, self.useUVRotation)):
            return stroke

        vertices = stroke.vertices.copy()
        falloffEvaluator = self.getFalloffEvaluator(falloff)

        if self.useStrength:
            _offsetStrengths = VirtualDoubleList.create(offsetStrengths, 0)
            offsetFloatList(vertices, stroke.strengths, _offsetStrengths, falloffEvaluator)

        if self.usePressure:
            _offsetPressures = VirtualDoubleList.create(offsetPressures, 0)
            offsetFloatList(vertices, stroke.pressures, _offsetPressures, falloffEvaluator)

        if self.useUVRotation:
            _offsetUVRotations = VirtualDoubleList.create(offsetUVRotations, 0)
            offsetFloatList(vertices, stroke.uvRotations, _offsetUVRotations, falloffEvaluator)

        if self.useLocation:
            _offsetLocations = VirtualVector3DList.create(offsetLocations, (0, 0, 0))
            offsetVector3DList(vertices, _offsetLocations, falloffEvaluator)
            stroke.vertices = vertices

        return stroke

    def getFalloffEvaluator(self, falloff):
        try: return falloff.getEvaluator("LOCATION")
        except: self.raiseErrorMessage("This falloff cannot be evaluated for vectors")
