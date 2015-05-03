import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from . import Curves
from . import Surfaces

class mn_CurvePointProjectorNode(Node, AnimationNode):
    bl_idname = "mn_CurvePointProjectorNode"
    bl_label = "Curve Point Projector"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorSocket", "World Point")
        self.inputs.new("mn_IntegerSocket", "Resolution").number = 64
        self.inputs.new("mn_ObjectSocket", "Curve")
        self.outputs.new("mn_FloatSocket", "Parameter")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"World Point" : "point",
                "Resolution" : "resolution",
                "Curve" : "curve"}
        
    def getOutputSocketNames(self):
        return {"Parameter" : "parameter"}
        
    def canExecute(self, point, resolution, curve):
        if resolution < 2: return False
        if not Curves.IsBezierCurve(curve): return False
        
        return True
    
    def execute(self, point, resolution, curve):
        rvParameter = 0.0
        if not self.canExecute(point, resolution, curve):
            return rvParameter
        
        try:
            curveCurve = Curves.Curve(curve)
            samplesWorld = curveCurve.SampleWorld(resolution)
            deltaParameter = float(1.0 / float(resolution - 1))
            
            rvParameter = 0.0
            rvLength2 = (samplesWorld[0] - point).length_squared
            for iSample in range(1, resolution):
                currParameter = deltaParameter * float(iSample)
                currLength2 = (samplesWorld[iSample] - point).length_squared
                if currLength2 < rvLength2:
                    rvLength2 = currLength2
                    rvParameter = currParameter
        except: pass
        
        return rvParameter
   
