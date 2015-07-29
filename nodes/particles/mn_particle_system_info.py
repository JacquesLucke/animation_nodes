import bpy, random, mathutils
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ParticleSystemInfo(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ParticleSystemInfo"
    bl_label = "Particle System Info"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ParticleSystemSocket", "Particle System")
        self.outputs.new("mn_ParticleListSocket", "Particles")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Particle System" : "particleSystem"}
    def getOutputSocketNames(self):
        return {"Particles" : "particles"}

    def execute(self, particleSystem):
        if not particleSystem: return []
        return list(particleSystem.particles)
        

