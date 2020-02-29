import bpy
from bpy.props import *
from ... events import executionCodeChanged
from .. gpencil.c_utils import offsetFloatList
from .. vector.offset_vector import offsetVector3DList
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualVector3DList, VirtualDoubleList

splineTypeItems = [
    ("BEZIER", "Bezier", "Each control point has two handles", "CURVE_BEZCURVE", 0),
    ("POLY", "Poly", "Linear interpolation between the spline points", "NOCURVE", 1)
]

class OffsetSplineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OffsetSplineNode"
    bl_label = "Offset Spline"
    errorHandlingType = "EXCEPTION"

    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        executionCodeChanged()

    splineType: EnumProperty(name = "Spline Type", default = "BEZIER",
        items = splineTypeItems, update = AnimationNode.refresh)

    useLocation: BoolProperty(update = checkedPropertiesChanged)
    useLeftHandle: BoolProperty(update = checkedPropertiesChanged)
    useRightHandle: BoolProperty(update = checkedPropertiesChanged)
    useRadius: BoolProperty(update = checkedPropertiesChanged)
    useTilt: BoolProperty(update = checkedPropertiesChanged)

    useVectorList: VectorizedSocket.newProperty()
    useLeftHandleList: VectorizedSocket.newProperty()
    useRightHandleList: VectorizedSocket.newProperty()
    useRadiusList: VectorizedSocket.newProperty()
    useTiltList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Spline", "Stroke", "spline", dataIsModified = True)
        self.newInput("Falloff", "Falloff", "falloff")
        self.newInput(VectorizedSocket("Vector", "useVectorList",
            ("Offset Location", "offsetLocations", dict(value = (0, 0, 1))),
            ("Offset Locations", "offsetLocations")))
        if self.splineType == "BEZIER":
            self.newInput(VectorizedSocket("Vector", "useLeftHandleList",
                ("Offset LeftHandle", "offsetLeftHandle", dict(value = (0, 0, 1))),
                ("Offset LeftHandles", "offsetLeftHandles")))
            self.newInput(VectorizedSocket("Vector", "useRightHandleList",
                ("Offset RightHandle", "offsetRightHandle", dict(value = (0, 0, 1))),
                ("Offset RightHandles", "offsetRightHandles")))
        self.newInput(VectorizedSocket("Float", "useRadiusList",
            ("Offset Radius", "offsetRadius", dict(value = 1)),
            ("Offset Radii", "offsetRadii")))
        self.newInput(VectorizedSocket("Float", "useTiltList",
            ("Offset Tilt", "offsetTilt", dict(value = 1)),
            ("Offset Tilts", "offsetTilts")))

        self.newOutput("Spline", "Stroke", "spline")

        self.updateSocketVisibility()

    def draw(self, layout):
        layout.prop(self, "splineType", text = "")

        col = layout.column(align = True)

        row = col.row(align = True)
        row.prop(self, "useLocation", text = "Location", toggle = True)

        if self.splineType == "BEZIER":
            row = col.row(align = True)
            row.prop(self, "useLeftHandle", text = "Left Handle", toggle = True)
            row.prop(self, "useRightHandle", text = "Right Handle", toggle = True)

        row = col.row(align = True)
        row.prop(self, "useRadius", text = "Radius", toggle = True)
        row.prop(self, "useTilt", text = "Tilt", toggle = True)

    def updateSocketVisibility(self):
        self.inputs[2].hide = not self.useLocation
        if self.splineType == "BEZIER":
            self.inputs[3].hide = not self.useLeftHandle
            self.inputs[4].hide = not self.useRightHandle
            self.inputs[5].hide = not self.useRadius
            self.inputs[6].hide = not self.useTilt
        elif self.splineType == "POLY":
            self.inputs[3].hide = not self.useRadius
            self.inputs[4].hide = not self.useTilt

    def getExecutionFunctionName(self):
        if self.splineType == "BEZIER":
            return "execute_Bezier"
        elif self.splineType == "POLY":
            return "execute_Poly"

    def execute_Bezier(self, spline, falloff, offsetLocations, offsetLeftHandles, offsetRightHandles,
                       offsetRadii, offsetTilts):
        if spline.type == "POLY":
            self.raiseErrorMessage("Wrong spline type mode.")
        if not any((self.useLocation, self.useLeftHandle, self.useRightHandle, self.useRadius, self.useTilt)):
            return spline

        falloffEvaluator = self.getFalloffEvaluator(falloff)

        if self.useRadius:
            _offsetRadii = VirtualDoubleList.create(offsetRadii, 0)
            offsetFloatList(spline.points, spline.radii, _offsetRadii, falloffEvaluator)

        if self.useTilt:
            _offsetTilts = VirtualDoubleList.create(offsetTilts, 0)
            offsetFloatList(spline.points, spline.tilts, _offsetTilts, falloffEvaluator)

        if self.useLocation:
            _offsetLocations = VirtualVector3DList.create(offsetLocations, (0, 0, 0))
            offsetVector3DList(spline.points, _offsetLocations, falloffEvaluator)
            offsetVector3DList(spline.leftHandles, _offsetLocations, falloffEvaluator)
            offsetVector3DList(spline.rightHandles, _offsetLocations, falloffEvaluator)

        if self.useLeftHandle:
            _offsetLeftHandles = VirtualVector3DList.create(offsetLeftHandles, (0, 0, 0))
            offsetVector3DList(spline.leftHandles, _offsetLeftHandles, falloffEvaluator)

        if self.useRightHandle:
            _offsetRightHandles = VirtualVector3DList.create(offsetRightHandles, (0, 0, 0))
            offsetVector3DList(spline.rightHandles, _offsetRightHandles, falloffEvaluator)

        return spline

    def execute_Poly(self, spline, falloff, offsetLocations, offsetRadii, offsetTilts):
        if spline.type == "BEIZER":
            self.raiseErrorMessage("Wrong spline type mode.")
        if not any((self.useLocation, self.useRadius, self.useTilt)):
            return spline

        falloffEvaluator = self.getFalloffEvaluator(falloff)

        if self.useRadius:
            _offsetRadii = VirtualDoubleList.create(offsetRadii, 0)
            offsetFloatList(spline.points, spline.radii, _offsetRadii, falloffEvaluator)

        if self.useTilt:
            _offsetTilts = VirtualDoubleList.create(offsetTilts, 0)
            offsetFloatList(spline.points, spline.tilts, _offsetTilts, falloffEvaluator)

        if self.useLocation:
            _offsetLocations = VirtualVector3DList.create(offsetLocations, (0, 0, 0))
            offsetVector3DList(spline.points, _offsetLocations, falloffEvaluator)

        return spline

    def getFalloffEvaluator(self, falloff):
        try: return falloff.getEvaluator("LOCATION")
        except: self.raiseErrorMessage("This falloff cannot be evaluated for vectors")
