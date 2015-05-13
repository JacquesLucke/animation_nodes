import bpy, random, mathutils
from bpy.types import Node
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
        self.outputs.new("mn_VectorSocket", "Velocity")
        self.outputs.new("mn_VectorSocket", "Angular Velocity")
        self.outputs.new("mn_FloatSocket", "Size")
        self.outputs.new("mn_StringSocket", "Alive State")
        self.outputs.new("mn_FloatSocket", "Lifetime")
        self.outputs.new("mn_FloatSocket", "Birth Time")
        self.outputs.new("mn_FloatSocket", "Die Time")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Particle" : "particle"}
    def getOutputSocketNames(self):
        return {"Location" : "location",
                "Rotation" : "rotation",
                "Velocity" : "velocity",
                "Angular Velocity" : "angularVelocity",
                "Size" : "size",
                "Alive State" : "aliveState",
                "Lifetime" : "lifetime",
                "Birth Time" : "birthTime",
                "Die Time" : "dieTime"}

    def execute(self, particle):
        if not particle: return Vector((0, 0, 0)), Vector((0, 0, 0)), Vector((0, 0, 0)), Vector((0, 0, 0)), 1, "DEAD", 0, 0, 0
        location = particle.location
        rotation = Vector(particle.rotation.to_euler())
        velocity = particle.velocity
        angularVelocity = particle.angular_velocity
        size = particle.size
        aliveState = particle.alive_state
        lifetime = particle.lifetime
        birthTime = particle.birth_time
        dieTime = particle.die_time
        return location, rotation, velocity, angularVelocity, size, aliveState, lifetime, birthTime, dieTime
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        codeLines = []
        codeLines.append("if %particle% is not None:")
        if outputUse["Location"]: codeLines.append("    $location$ = %particle%.location")
        if outputUse["Rotation"]: codeLines.append("    $rotation$ = mathutils.Vector(%particle%.rotation.to_euler())")
        if outputUse["Velocity"]: codeLines.append("    $velocity$ = %particle%.velocity")
        if outputUse["Angular Velocity"]: codeLines.append("    $angularVelocity$ = %particle%.angular_velocity")
        if outputUse["Size"]: codeLines.append("    $size$ = %particle%.size")
        if outputUse["Alive State"]: codeLines.append("    $aliveState$ = %particle%.alive_state")
        if outputUse["Lifetime"]: codeLines.append("    $lifetime$ = %particle%.lifetime")
        if outputUse["Birth Time"]: codeLines.append("    $birthTime$ = %particle%.birth_time")
        if outputUse["Die Time"]: codeLines.append("    $dieTime$ = %particle%.die_time")
        codeLines.append("    pass")        
        return "\n".join(codeLines)
    def getModuleList(self):
        return ["mathutils"]
