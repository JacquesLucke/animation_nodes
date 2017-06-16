import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... events import executionCodeChanged

stateItems = [
    ("REST", "Rest", "Return information in rest position.", "NONE", 0),
    ("POSE", "Pose", "Return information in pose position.", "NONE", 1) ]

class ArmatureInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ArmatureInfoNode"
    bl_label = "Armature Info"

    state = EnumProperty(name = "State", default = "POSE",
        items = stateItems, update = executionCodeChanged)

    def create(self):
        self.newInput("Object", "Armature", "armature", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Matrix List", "Matrices", "matrices")
        self.newOutput("Vector List", "Centers", "centers")
        self.newOutput("Vector List", "Directions", "directions")
        self.newOutput("Float List", "Lengths", "lengths")
        self.newOutput("Vector List", "Heads", "heads", hide = True)
        self.newOutput("Vector List", "Tails", "tails", hide = True)
        self.newOutput("Text List", "Names", "names", hide = True)

    def draw(self, layout):
        layout.prop(self, "state")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return

        yield "if getattr(armature, 'type', '') == 'ARMATURE':"
        if self.state == "REST":
            yield "    bones = armature.data.bones"
            if isLinked["matrices"]:   yield "    matrices = Matrix4x4List.fromValues([bone.matrix_local for bone in bones])"
            if isLinked["centers"]:    yield "    centers = Vector3DList.fromValues([bone.center for bone in bones])"
            if isLinked["directions"]: yield "    directions = Vector3DList.fromValues([bone.vector for bone in bones])"
            if isLinked["lengths"]:    yield "    lengths = DoubleList.fromValues([bone.length for bone in bones])"
            if isLinked["heads"]:      yield "    heads = Vector3DList.fromValues([bone.head for bone in bones])"
            if isLinked["tails"]:      yield "    tails = Vector3DList.fromValues([bone.tail for bone in bones])"
        else:
            yield "    bones = armature.pose.bones"
            if isLinked["matrices"]:   yield "    matrices = Matrix4x4List.fromValues([bone.matrix for bone in bones])"
            if isLinked["centers"]:    yield "    centers = Vector3DList.fromValues([bone.center for bone in bones])"
            if isLinked["directions"]: yield "    directions = Vector3DList.fromValues([bone.vector for bone in bones])"
            if isLinked["lengths"]:    yield "    lengths = DoubleList.fromValues([bone.length for bone in bones])"
            if isLinked["heads"]:      yield "    heads = Vector3DList.fromValues([bone.head for bone in bones])"
            if isLinked["tails"]:      yield "    tails = Vector3DList.fromValues([bone.tail for bone in bones])"
        if isLinked["names"]: yield "    names = [bone.name for bone in armature.data.bones]"
        yield "else:"
        yield "    matrices = Matrix4x4List()"
        yield "    centers = Vector3DList()"
        yield "    directions = Vector3DList()"
        yield "    lengths = DoubleList()"
        yield "    heads = Vector3DList()"
        yield "    tails = Vector3DList()"
        yield "    names = []"
