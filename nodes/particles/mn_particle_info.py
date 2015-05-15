import bpy, random, mathutils
from bpy.types import Node
from bpy.props import *
from mathutils import Vector
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ParticleInfo(Node, AnimationNode):
    bl_idname = "mn_ParticleInfo"
    bl_label = "Particle Info"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ParticleSocket", "Particle")
        self.outputs.new("mn_VectorSocket", "Location")
        self.outputs.new("mn_VectorSocket", "Rotation")
        self.outputs.new("mn_FloatSocket", "Age")
        self.outputs.new("mn_VectorSocket", "Velocity").hide = True
        self.outputs.new("mn_VectorSocket", "Angular Velocity").hide = True
        self.outputs.new("mn_FloatSocket", "Size").hide = True
        self.outputs.new("mn_StringSocket", "Alive State").hide = True
        self.outputs.new("mn_BooleanSocket", "Is Exist").hide = True
        self.outputs.new("mn_BooleanSocket", "Is Visible").hide = True
        self.outputs.new("mn_FloatSocket", "Lifetime").hide = True
        self.outputs.new("mn_FloatSocket", "Birth Time").hide = True
        self.outputs.new("mn_FloatSocket", "Die Time").hide = True
        self.outputs.new("mn_VectorSocket", "Previous Location").hide = True
        self.outputs.new("mn_VectorSocket", "Previous Rotation").hide = True
        self.outputs.new("mn_VectorSocket", "Previous Velocity").hide = True
        self.outputs.new("mn_VectorSocket", "Previous Angular Velocity").hide = True
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Particle" : "particle"}
    def getOutputSocketNames(self):
        return {"Location" : "location",
                "Rotation" : "rotation",
                "Age" : "age",
                "Velocity" : "velocity",
                "Angular Velocity" : "angularVelocity",
                "Size" : "size",
                "Alive State" : "aliveState",
                "Is Exist" : "isExist",
                "Is Visible" : "isVisible",
                "Lifetime" : "lifetime",
                "Birth Time" : "birthTime",
                "Die Time" : "dieTime",
                "Previous Location" : "previousLocation",
                "Previous Rotation" : "previousRotation",
                "Previous Velocity" : "previousVelocity",
                "Previous Angular Velocity" : "previousAngularVelocity"}
        
    def useInLineExecution(self):
        return True
        
    def getInLineExecutionString(self, outputUse):
        codeLines = []
        
        codeLines.append("if %particle%:")
        if outputUse["Location"]: codeLines.append("    $location$ = %particle%.location")
        if outputUse["Rotation"]: codeLines.append("    $rotation$ = mathutils.Vector(%particle%.rotation.to_euler())")
        if outputUse["Velocity"]: codeLines.append("    $velocity$ = %particle%.velocity")
        if outputUse["Angular Velocity"]: codeLines.append("    $angularVelocity$ = %particle%.angular_velocity")
        if outputUse["Size"]: codeLines.append("    $size$ = %particle%.size")
        if outputUse["Alive State"]: codeLines.append("    $aliveState$ = %particle%.alive_state")
        if outputUse["Is Exist"]: codeLines.append("    $isExist$ = %particle%.is_exist")
        if outputUse["Is Visible"]: codeLines.append("    $isVisible$ = %particle%.is_visible")
        if outputUse["Lifetime"]: codeLines.append("    $lifetime$ = %particle%.lifetime")
        if outputUse["Birth Time"]: codeLines.append("    $birthTime$ = %particle%.birth_time")
        if outputUse["Die Time"]: codeLines.append("    $dieTime$ = %particle%.die_time")
        if outputUse["Age"]: codeLines.append("    $age$ = max(0, scene.frame_current - %particle%.birth_time)")
        if outputUse["Previous Location"]: codeLines.append("    $previousLocation$ = %particle%.prev_location")
        if outputUse["Previous Rotation"]: codeLines.append("    $previousRotation$ = mathutils.Vector(%particle%.prev_rotation.to_euler())")
        if outputUse["Previous Velocity"]: codeLines.append("    $previousVelocity$ = %particle%.prev_velocity")
        if outputUse["Previous Angular Velocity"]: codeLines.append("    $previousAngularVelocity$ = %particle%.prev_angular_velocity")
        codeLines.append("    pass")
        
        codeLines.append("else:")
        if outputUse["Location"]: codeLines.append("    $location$ = mathutils.Vector((0, 0, 0))")
        if outputUse["Rotation"]: codeLines.append("    $rotation$ = mathutils.Vector((0, 0, 0))")
        if outputUse["Velocity"]: codeLines.append("    $velocity$ = mathutils.Vector((0, 0, 0))")
        if outputUse["Angular Velocity"]: codeLines.append("    $angularVelocity$ = mathutils.Vector((0, 0, 0))")
        if outputUse["Size"]: codeLines.append("    $size$ = 1")
        if outputUse["Alive State"]: codeLines.append("    $aliveState$ = 'DEAD'")
        if outputUse["Is Exist"]: codeLines.append("    $isExist$ = False")
        if outputUse["Is Visible"]: codeLines.append("    $isVisible$ = False")
        if outputUse["Lifetime"]: codeLines.append("    $lifetime$ = 0")
        if outputUse["Birth Time"]: codeLines.append("    $birthTime$ = 0")
        if outputUse["Die Time"]: codeLines.append("    $dieTime$ = 0")
        if outputUse["Age"]: codeLines.append("    $age$ = 0")
        if outputUse["Previous Location"]: codeLines.append("    $previousLocation$ = mathutils.Vector((0, 0, 0))")
        if outputUse["Previous Rotation"]: codeLines.append("    $previousRotation$ = mathutils.Vector((0, 0, 0))")
        if outputUse["Previous Velocity"]: codeLines.append("    $previousVelocity$ = mathutils.Vector((0, 0, 0))")
        if outputUse["Previous Angular Velocity"]: codeLines.append("    $previousAngularVelocity$ = mathutils.Vector((0, 0, 0))")
        codeLines.append("    pass")        
        
        return "\n".join(codeLines)
        
    def getModuleList(self):
        return ["mathutils"]
