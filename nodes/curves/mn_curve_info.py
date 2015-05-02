import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from . import Curves

class mn_CurveInfoNode(Node, AnimationNode):
    bl_idname = "mn_CurveInfoNode"
    bl_label = "Curve Info"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Curve").showName = True
        self.outputs.new("mn_IntegerSocket", "NrSplines")
        self.outputs.new("mn_StringListSocket", "SplineTypes")
        self.outputs.new("mn_FloatSocket", "Length")
        self.outputs.new("mn_FloatSocket", "LengthWorld")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Curve" : "curve"}
    def getOutputSocketNames(self):
        return {"NrSplines" : "nrSplines",
                "SplineTypes" : "splineTypes",
                "Length" : "length",
                "LengthWorld" : "lengthWorld"}
        
    def canExecute(self, curve):
        if curve is None: return False
        if not Curves.IsBezierCurve(curve): return False
        
        return True
        
    def execute(self, curve):
        nrSplines = 0
        splineTypes = []
        length = 0.0
        lengthWorld = 0.0
        if not self.canExecute(curve):
            return nrSplines, splineTypes, length, lengthWorld
        
        try:
            curveCurve = Curves.Curve(curve)
            nrSplines = curveCurve.blenderNrSplines
            splineTypes = curveCurve.blenderSplineTypes
            length = curveCurve.length
            lengthWorld = curveCurve.lengthWorld
        except: pass
            
        return nrSplines, splineTypes, length, lengthWorld
        
