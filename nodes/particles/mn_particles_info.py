import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ParticlesInfo(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ParticlesInfo"
    bl_label = "Particles Info"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ParticleListSocket", "Particles")
        self.outputs.new("mn_VectorListSocket", "Locations")
        self.outputs.new("mn_VectorListSocket", "Velocities").hide = True
        self.outputs.new("mn_FloatListSocket", "Ages").hide = True
        self.outputs.new("mn_FloatListSocket", "Sizes").hide = True
        self.outputs.new("mn_FloatListSocket", "Birth Times").hide = True
        self.outputs.new("mn_FloatListSocket", "Die Times").hide = True
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Particles" : "particles"}
    def getOutputSocketNames(self):
        return {"Locations" : "locations",
                "Velocities" : "velocity",
                "Ages" : "ages",
                "Sizes" : "sizes",
                "Birth Times" : "birthTimes",
                "Die Times" : "dieTimes"}
        
    def useInLineExecution(self):
        return True
        
    def getInLineExecutionString(self, outputUse):
        codeLines = []
        if outputUse["Locations"]: codeLines.append("$locations$ = [p.location for p in %particles%]")
        if outputUse["Velocities"]: codeLines.append("$velocity$ = [p.velocity for p in %particles%]")
        if outputUse["Ages"]: codeLines.append("$ages$ = [max(0, scene.frame_current - p.birth_time) for p in %particles%]")
        if outputUse["Sizes"]: codeLines.append("$sizes$ = [p.size for p in %particles%]")
        if outputUse["Birth Times"]: codeLines.append("$birthTimes$ = [p.birth_time for p in %particles%]")
        if outputUse["Die Times"]: codeLines.append("$dieTimes$ = [p.die_time for p in %particles%]")
        return "\n".join(codeLines)