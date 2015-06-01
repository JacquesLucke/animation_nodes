from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import allowCompiling, forbidCompiling

defaultNrSamples = 2
defaultStart = -1.0
defaultEnd = 1.0

class mn_MathUniformSamplerNode(Node, AnimationNode):
    bl_idname = "mn_MathUniformSamplerNode"
    bl_label = "Uniform Sampler"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "NrSamples").number = defaultNrSamples
        self.inputs.new("mn_FloatSocket", "Start").number = defaultStart
        self.inputs.new("mn_FloatSocket", "End").number = defaultEnd
        self.outputs.new("mn_FloatListSocket", "Samples")
        allowCompiling()

    def getInputSocketNames(self):
        return {"NrSamples" : "nrSamples",
                "Start" : "start",
                "End" : "end"}

    def getOutputSocketNames(self):
        return {"Samples" : "samples"}

    def execute(self, nrSamples, start, end):
        def canExecute():
            if nrSamples < 1: return False
            
            return True
            
        samples = []
        if not canExecute(): return samples
        
        if nrSamples == 1: return [0.5 * (start + end)]
        
        delta = (end - start) / float(nrSamples - 1)
        for iSample in range(nrSamples):
            sample = start + iSample * delta
            samples.append(sample)
            
        return samples
