import bpy, random
from bpy.types import Node
from ... mn_cache import getUniformRandom
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... mn_utils import *

class mn_MultiFloatMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_MultiFloatMathNode"
    bl_label = "Multi Float Math"
    node_category = "Math"
    isDetermined = True
    
    operationItems = [("ADD", "Add", ""),
                    ("MULTIPLY", "Multiply", "")]
    
    operation = bpy.props.EnumProperty(default = "ADD", name = "Operation", items = operationItems, update = nodePropertyChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "1.")
        self.inputs.new("mn_FloatSocket", "2.")
        self.inputs.new("mn_EmptySocket", "...")
        self.outputs.new("mn_FloatSocket", "Result")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", text = "Operation")
    
        row = layout.row(align = True)
        self.callFunctionFromUI(row, "newInputSocket", text = "New", icon = "PLUS")
        self.callFunctionFromUI(row, "removeInputSocket", text = "Remove", icon = "X")
        
    def update(self):
        forbidCompiling()
        socket = self.inputs.get("...")
        if socket is not None:
            links = socket.links
            if len(links) == 1:
                link = links[0]
                fromSocket = link.from_socket
                originSocket = getOriginSocket(socket)
                self.id_data.links.remove(link)
                if originSocket is not None:
                    if originSocket.dataType in ["Float", "Integer"]:
                        self.inputs.remove(socket)
                        newSocketName = str(len(self.inputs) + 1) + "."
                        newSocket = self.inputs.new("mn_FloatSocket", newSocketName)
                        self.inputs.new("mn_EmptySocket", "...")
                        self.id_data.links.new(newSocket, fromSocket)
                
        allowCompiling()
        
    def execute(self, inputs):
        output = {}
        result = 0
        
        if self.operation == "ADD":
            for identifier, value in inputs.items():
                if identifier != "...":
                    result += value
        if self.operation == "MULTIPLY":
            result = 1
            for identifier, value in inputs.items():
                if identifier != "...":
                    result *= value
                
        output["Result"] = result
        return output
        
    def newInputSocket(self):
        forbidCompiling()
        newSocketName = str(len(self.inputs)) + "."
        newSocket = self.inputs.new("mn_FloatSocket", newSocketName)
        self.inputs.move(len(self.inputs) - 1, len(self.inputs) - 2)
        allowCompiling()
        
    def removeInputSocket(self):
        forbidCompiling()
        if len(self.inputs) > 2:
            self.inputs.remove(self.inputs[len(self.inputs) - 2])
        allowCompiling()