import bpy
from bpy.types import Node
import mathutils
import math
from math import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

defaultFunction = "u * v"
defaultNrSamples = 2
defaultStart = -1.0
defaultEnd = 1.0

# list of safe functions for eval()
safe_list = ['math', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh',
             'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot',
             'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians',
             'sin', 'sinh', 'sqrt', 'tan', 'tanh']

# use the list to filter the local namespace
safe_dict = dict((k, globals().get(k, None)) for k in safe_list)

class mn_Math2DFunctionSamplerNode(Node, AnimationNode):
    bl_idname = "mn_Math2DFunctionSamplerNode"
    bl_label = "2D Function Sampler"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_StringSocket", "Function").string = defaultFunction
        self.inputs.new("mn_IntegerSocket", "Samples U").number = defaultNrSamples
        self.inputs.new("mn_IntegerSocket", "Samples V").number = defaultNrSamples
        self.inputs.new("mn_FloatSocket", "Start U").number = defaultStart
        self.inputs.new("mn_FloatSocket", "End U").number = defaultEnd
        self.inputs.new("mn_FloatSocket", "Start V").number = defaultStart
        self.inputs.new("mn_FloatSocket", "End V").number = defaultEnd
        self.outputs.new("mn_FloatListSocket", "Samples")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Function" : "function",
                "Samples U" : "samplesU",
                "Samples V" : "samplesV",
                "Start U" : "startU",
                "End U" : "endU",
                "Start V" : "startV",
                "End V" : "endV"}

    def getOutputSocketNames(self):
        return {"Samples" : "samples"}

    def canExecute(self, function, samplesU, samplesV, startU, endU, startV, endV):
        try: self.expr_args = (compile(function, __file__, 'eval'), {"__builtins__": None}, safe_dict)
        except: return False
        
        if samplesU < 2: return False
        if samplesV < 2: return False
            
        return True

    def execute(self, function, samplesU, samplesV, startU, endU, startV, endV):
        samples = []
        if not self.canExecute(function, samplesU, samplesV, startU, endU, startV, endV):
            return samples
            
        delta_u = (endU - startU) / float(samplesU - 1)
        delta_v = (endV - startV) / float(samplesV - 1)

        for row_u in range(samplesU):
            u = startU + row_u * delta_u

            for row_v in range(samplesV):
                v = startV + row_v * delta_v
                
                sample = 0.0
                safe_dict['u'] = u
                safe_dict['v'] = v

                try: sample = float(eval(*(self.expr_args)))
                except: return []
                
                samples.append(sample)
        
        return samples
