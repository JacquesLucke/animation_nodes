import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, AutoSelectVectorization

trackAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z", "-X", "-Y", "-Z")]
guideAxisItems  = [(axis, axis, "") for axis in ("X", "Y", "Z")]

class DirectionToRotationNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DirectionToRotationNode"
    bl_label = "Direction to Rotation"
    bl_width_default = 160

    trackAxis = EnumProperty(items = trackAxisItems, update = propertyChanged, default = "Z")
    guideAxis = EnumProperty(items = guideAxisItems, update = propertyChanged, default = "X")

    useDirectionList = BoolProperty(update = AnimationNode.updateSockets)
    useGuideList = BoolProperty(update = AnimationNode.updateSockets)

    def create(self):
        self.newInputGroup(self.useDirectionList,
            ("Vector", "Direction", "direction"),
            ("Vector List", "Directions", "directions"))
        self.newInputGroup(self.useGuideList,
            ("Vector", "Guide", "guide", {"value" : (0, 0, 1)}),
            ("Vector List", "Guides", "guides"))

        generateList = self.useDirectionList or self.useGuideList

        self.newOutputGroup(generateList,
            ("Euler", "Euler Rotation", "eulerRotation"),
            ("Euler List", "Euler Rotations", "eulerRotations"))

        self.newOutputGroup(generateList,
            ("Quaternion", "Quaternion Rotation", "quaternionRotation", {"hide" : True}),
            ("Quaternion List", "Quaternion Rotations", "quaternionRotations", {"hide" : True}))

        self.newOutputGroup(generateList,
            ("Matrix", "Matrix Rotation", "matrixRotation", {"hide" : True}),
            ("Matrix List", "Matrix Rotations", "matrixRotations", {"hide" : True}))

        vectorization = AutoSelectVectorization()
        vectorization.input(self, "useDirectionList", self.inputs[0])
        vectorization.input(self, "useGuideList", self.inputs[1])
        vectorization.output(self, [("useDirectionList", "useGuideList")], list(self.outputs))
        self.newSocketEffect(vectorization)

    def draw(self, layout):
        layout.prop(self, "trackAxis", expand = True)
        layout.prop(self, "guideAxis", expand = True)

        if self.trackAxis[-1:] == self.guideAxis[-1:]:
            layout.label("Must be different", icon = "ERROR")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        generateList = self.useDirectionList or self.useGuideList

        if generateList:
            if self.useDirectionList and self.useGuideList:
                yield "matrixRotations = eulerRotations = quaternionRotations = 0"
            elif self.useDirectionList:
                yield "matrixRotations = AN.algorithms.rotations.directionsToMatrices(directions, guide, self.trackAxis, self.guideAxis)"
            elif self.useGuideList:
                yield "matrixRotations = eulerRotations = quaternionRotations = 0"
            if isLinked["eulerRotations"]: yield "eulerRotations = matrixRotations.toEulers(isNormalized = True)"
            if isLinked["quaternionRotations"]: yield "quaternionRotations = matrixRotations.toQuaternions(isNormalized = True)"
        else:
            yield "matrixRotation = AN.algorithms.rotations.directionToMatrix(direction, guide, self.trackAxis, self.guideAxis)"
            if isLinked["eulerRotation"]: yield "eulerRotation = matrixRotation.to_euler()"
            if isLinked["quaternionRotation"]: yield "quaternionRotation = matrixRotation.to_quaternion()"
