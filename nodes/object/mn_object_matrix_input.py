import bpy
from bpy.types import Node
from mathutils import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ObjectMatrixInput(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ObjectMatrixInput"
    bl_label = "Object Matrix Input"
    outputUseParameterName = "useOutput"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.outputs.new("mn_MatrixSocket", "Basis")
        self.outputs.new("mn_MatrixSocket", "Local")
        self.outputs.new("mn_MatrixSocket", "Parent Inverse")
        self.outputs.new("mn_MatrixSocket", "World")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Object" : "object"}
    def getOutputSocketNames(self):
        return {"Basis" : "basis",
                "Local" : "local",
                "Parent Inverse" : "parentInverse",
                "World" : "world"}
    
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        codeLines = []
        codeLines.append("try:")
        if outputUse["Basis"]: codeLines.append("    $basis$ = %object%.matrix_basis")
        if outputUse["Local"]: codeLines.append("    $local$ = %object%.matrix_local")
        if outputUse["Parent Inverse"]: codeLines.append("    $parentInverse$ = %object%.matrix_parent_inverse")
        if outputUse["World"]: codeLines.append("    $world$ = %object%.matrix_world")
        codeLines.append("    pass")
        codeLines.append("except:")
        codeLines.append("    $basis$ = mathutils.Matrix.Identity(4)")
        codeLines.append("    $local$ = mathutils.Matrix.Identity(4)")
        codeLines.append("    $parentInverse$ = mathutils.Matrix.Identity(4)")
        codeLines.append("    $world$ = mathutils.Matrix.Identity(4)")
        return "\n".join(codeLines)
        
    def getModuleList(self):
        return ["mathutils"]
