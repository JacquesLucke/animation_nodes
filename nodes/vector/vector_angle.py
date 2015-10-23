import bpy
from ... base_types.node import AnimationNode

class VectorAngleNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorAngleNode"
    bl_label = "Vector Angle"
    
    def create(self):
        self.inputs.new("an_VectorSocket", "A", "a")
        self.inputs.new("an_VectorSocket", "B", "b")
        self.outputs.new("an_FloatSocket", "Angle", "angle")
        self.outputs.new("an_QuaternionSocket", "Rotation Difference", "quat")
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
        
        lines = []
        if isLinked["angle"]: lines.append("angle = a.angle(b, 0)")
        if isLinked["quat"]: lines.append("quat = a.rotation_difference(b)")
        
        return lines
