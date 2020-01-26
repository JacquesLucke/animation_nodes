import bpy
from ... base_types import AnimationNode, VectorizedSocket

class ObjectTransformsInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectTransformsInputNode"
    bl_label = "Object Transforms Input"
    bl_width_default = 160
    codeEffects = [VectorizedSocket.CodeEffect]

    useObjectList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects")))

        self.newOutput(VectorizedSocket("Vector", "useObjectList",
            ("Location", "location"), ("Locations", "locations")))

        self.newOutput(VectorizedSocket("Euler", "useObjectList",
            ("Rotation", "rotation"), ("Rotations", "rotations")))

        self.newOutput(VectorizedSocket("Vector", "useObjectList",
            ("Scale", "scale"), ("Scales", "scales")))

        self.newOutput(VectorizedSocket("Quaternion", "useObjectList",
            ("Quaternion", "quaternion", dict(hide = True)),
            ("Quaternions", "quaternions", dict(hide = True))))

    def drawAdvanced(self, layout):
        self.invokeFunction(layout, "createAutoExecutionTrigger", text = "Create Execution Trigger")

    def getExecutionCode(self, required):
        if len(required) == 0:
            return

        yield "if object is not None:"
        yield "    evaluatedObject = AN.utils.depsgraph.getEvaluatedID(object)"
        if "location" in required:   yield "    location = evaluatedObject.location"
        if "rotation" in required:   yield "    rotation = evaluatedObject.rotation_euler"
        if "scale" in required:      yield "    scale = evaluatedObject.scale"
        if "quaternion" in required: yield "    quaternion = evaluatedObject.rotation_quaternion"
        yield "else:"
        yield "    location = Vector((0, 0, 0))"
        yield "    rotation = Euler((0, 0, 0))"
        yield "    scale = Vector((1, 1, 1))"
        yield "    quaternion = Quaternion((1, 0, 0, 0))"

    def createAutoExecutionTrigger(self):
        isLinked = self.getLinkedOutputsDict()
        customTriggers = self.nodeTree.autoExecution.customTriggers

        attrs = []
        if isLinked["scale"]: attrs.append("scale")
        if isLinked["location"]: attrs.append("location")
        if isLinked["rotation"]: attrs.append("rotation_euler")
        if isLinked["quaternion"]: attrs.append("rotation_quaternion")
        
        if attrs:
            item = self.nodeTree.autoExecution.customTriggers.new("MONITOR_PROPERTY")
            item.idType = "OBJECT"
            item.dataPaths = ",".join(attrs)
            item.object = self.inputs["Object"].object
