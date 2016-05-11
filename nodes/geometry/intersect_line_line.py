import bpy
from ... base_types.node import AnimationNode

class IntersectLineLineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectLineLineNode"
    bl_label = "Intersect Line Line"
    bl_width_default = 160
    searchTags = ["Closest Points on 2 Lines"]
        
    def create(self):
        self.newInput("Vector", "Line 1 Start", "line1Start").value = [-2, 0, 0]
        self.newInput("Vector", "Line 1 End", "line1End").value = [2, 0, 0]
        self.newInput("Vector", "Line 2 Start", "line2Start").value = [1, -1, 0]
        self.newInput("Vector", "Line 2 End", "line2End").value = [1, 1, 0]
        
        self.newOutput("Vector", "Intersection (Closest) 1", "int1")
        self.newOutput("Vector", "Intersection (Closest) 2", "int2")
        self.newOutput("Boolean", "Is Valid", "isValid")
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
    
        intersection1  = isLinked["int1"]
        intersection2  = isLinked["int2"]
        isValid = isLinked["isValid"]
        
        yield "int = mathutils.geometry.intersect_line_line(line1Start, line1End, line2Start, line2End)"
        
        yield "if int is None:"
        if intersection1 : yield "    int1 = mathutils.Vector((0, 0, 0))"
        if intersection2 : yield "    int2 = mathutils.Vector((0, 0, 0))"
        if isValid: yield "    isValid = False"
        yield "else:"
        if intersection1 : yield "    int1 = int[0]"
        if intersection2 : yield "    int2 = int[1]"
        if isValid: yield "    isValid = True"
    
    def getUsedModules(self):
        return ["mathutils"]