import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... mn_utils import *
from ... utils.mn_node_utils import *


class mn_CombineStringsNode(Node, AnimationNode):
    bl_idname = "mn_CombineStringsNode"
    bl_label = "Combine Texts"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_StringSocket", "1.")
        self.inputs.new("mn_StringSocket", "2.")
        self.inputs.new("mn_EmptySocket", "...").passiveSocketType = "mn_StringSocket"
        self.outputs.new("mn_StringSocket", "Text")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        row = layout.row(align = True)
    
        self.callFunctionFromUI(row, "newInputSocket", text = "New", icon = "PLUS")
        self.callFunctionFromUI(row, "removeInputSocket", text = "Remove", icon = "X")
        
    def update(self):
        forbidCompiling()
        
        socket = self.inputs.get("...")
        updateDependencyNode(socket)
        
        if socket is not None:
            links = socket.links
            if len(links) == 1:
                link = links[0]
                fromSocket = link.from_socket
                originSocket = getOriginSocket(socket)
                self.id_data.links.remove(link)
                if originSocket is not None:
                    if originSocket.dataType == "String":
                        self.inputs.remove(socket)
                        newSocketName = str(len(self.inputs) + 1) + "."
                        newSocket = self.inputs.new("mn_StringSocket", newSocketName)
                        self.inputs.new("mn_EmptySocket", "...").passiveSocketType = "mn_StringSocket"
                        self.id_data.links.new(newSocket, fromSocket)
                
        allowCompiling()
        
    def execute(self, input):
        output = {}
        text = ""
        for i in range(len(self.inputs) - 1):
            identifier = str(i+1) + "."
            text += input[identifier]
        output["Text"] = text
        return output
        
    def newInputSocket(self):
        forbidCompiling()
        newSocketName = str(len(self.inputs)) + "."
        newSocket = self.inputs.new("mn_StringSocket", newSocketName)
        self.inputs.move(len(self.inputs) - 1, len(self.inputs) - 2)
        allowCompiling()
        nodeTreeChanged()
        
    def removeInputSocket(self):
        forbidCompiling()
        if len(self.inputs) > 2:
            self.inputs.remove(self.inputs[len(self.inputs) - 2])
        allowCompiling()
        nodeTreeChanged()