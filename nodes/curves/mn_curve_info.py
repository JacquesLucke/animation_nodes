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
        self.inputs.new("mn_ObjectSocket", "Curve")
        self.outputs.new("mn_IntegerSocket", "Number of Splines")
        self.outputs.new("mn_StringListSocket", "Types of Splines")
        self.outputs.new("mn_FloatSocket", "Local Length")
        self.outputs.new("mn_FloatSocket", "World Length")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Curve" : "curve"}
    def getOutputSocketNames(self):
        return {"Number of Splines" : "nrSplines",
                "Types of Splines" : "splineTypes",
                "Local Length" : "length",
                "World Length" : "lengthWorld"}
        
    def canExecute(self, curve):
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
            length = curveCurve.CalcLengthWithBlenderResolution()
            lengthWorld = curveCurve.CalcLengthWorldWithBlenderResolution()
        except: pass
            
        return nrSplines, splineTypes, length, lengthWorld
        
