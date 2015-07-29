import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling
from ... mn_utils import *

class mn_CreatePolygonIndices(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CreatePolygonIndices"
    bl_label = "Create Polygon Indices"
    node_category = "Mesh"
    isDetermined = True
    
    def amountChanged(self, context):
        self.generateInputSockets()
        nodeTreeChanged()
    
    amount = bpy.props.IntProperty(default = 3, name = "Vertex Amount", update = amountChanged, min = 3, soft_max = 10)
    
    def init(self, context):
        forbidCompiling()
        self.generateInputSockets()
        self.outputs.new("mn_PolygonIndicesSocket", "Polygon Indices")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "amount")
        
    def generateInputSockets(self):
        forbidCompiling()
        connections = getConnectionDictionaries(self)
        self.inputs.clear()
        for i in range(self.amount):
            self.inputs.new("mn_IntegerSocket", "Index " + str(i)).number = i
        tryToSetConnectionDictionaries(self, connections)
        allowCompiling()
                
    def getInputSocketNames(self):
        names = {}
        for i, socket in enumerate(self.inputs):
            names[socket.name] = "index" + str(i)
        return names
    def getOutputSocketNames(self):
        return {"Polygon Indices" : "polygonIndices"}
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        list = ", ".join(["%index"+str(i)+"%" for i in range(self.amount)])
        return "$polygonIndices$ = ("+ list +")"
