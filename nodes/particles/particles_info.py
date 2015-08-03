import bpy
from ... base_types.node import AnimationNode


class ParticlesInfo(bpy.types.Node, AnimationNode):
    bl_idname = "an_ParticlesInfo"
    bl_label = "Particles Info"

    inputNames = { "Particles" : "particles" }

    outputNames = { "Locations" : "locations",
                    "Velocities" : "velocity",
                    "Ages" : "ages",
                    "Sizes" : "sizes",
                    "Birth Times" : "birthTimes",
                    "Die Times" : "dieTimes" }

    def create(self):
        self.inputs.new("an_ParticleListSocket", "Particles")
        self.outputs.new("an_VectorListSocket", "Locations")
        self.outputs.new("an_VectorListSocket", "Velocities").hide = True
        self.outputs.new("an_FloatListSocket", "Ages").hide = True
        self.outputs.new("an_FloatListSocket", "Sizes").hide = True
        self.outputs.new("an_FloatListSocket", "Birth Times").hide = True
        self.outputs.new("an_FloatListSocket", "Die Times").hide = True

    def getExecutionCode(self, usedOutputs):
        codeLines = []
        if usedOutputs["Locations"]: codeLines.append("$locations$ = [p.location for p in %particles%]")
        if usedOutputs["Velocities"]: codeLines.append("$velocity$ = [p.velocity for p in %particles%]")
        if usedOutputs["Ages"]: codeLines.append("$ages$ = [max(0, scene.frame_current - p.birth_time) for p in %particles%]")
        if usedOutputs["Sizes"]: codeLines.append("$sizes$ = [p.size for p in %particles%]")
        if usedOutputs["Birth Times"]: codeLines.append("$birthTimes$ = [p.birth_time for p in %particles%]")
        if usedOutputs["Die Times"]: codeLines.append("$dieTimes$ = [p.die_time for p in %particles%]")
        return "\n".join(codeLines)
