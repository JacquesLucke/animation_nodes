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
        self.inputs.new("mn_ObjectSocket", "Object").showName = True
        self.outputs.new("mn_ObjectSocket", "Curve Data")
        self.outputs.new("mn_StringSocket", "Type")
        self.outputs.new("mn_FloatSocket", "Length")
        self.outputs.new("mn_FloatSocket", "LengthWorld")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Object" : "object"}
    def getOutputSocketNames(self):
        return {"Curve Data" : "curveData",
                "Type" : "type",
                "Length" : "length",
                "LengthWorld" : "lengthW"}
        
    def execute(self, object):
        curveData = None
        type = "?type?"
        resolution = -1

        if object is None: print("!! " + "mn_CurveInfoNode.execute(): " + "object is None")
        
        try: curveData = object.data
        except: pass
        
        try: type = object.data.splines[0].type
        except: pass
        
        # TODO
        length = -1.0
        try: curve = Curves.Curve(object)
        except Exception as excCrv: print("!! EXC: " + "curve = Curves.Curve(object)" + ": " + repr(excCrv))
        try: length = curve.CalcLength()
        except Exception as excLen: print("!! EXC: " + "length = curve.CalcLength()" + ": " + repr(excLen))
            
        lengthW = -1.0
        try: curveW = Curves.Curve(object)
        except Exception as excCrvW: print("!! EXC: " + "curve = Curves.Curve(object)" + ": " + repr(excCrvW))
        try: lengthW = curveW.CalcLengthWorld()
        except Exception as excLenW: print("!! EXC: " + "length = curveW.CalcLengthWorld()" + ": " + repr(excLenW))
        
        return curveData, type, length, lengthW
        
