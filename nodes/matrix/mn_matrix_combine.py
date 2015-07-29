import bpy
from bpy.types import Node
from bpy.props import *
from mathutils import *
from ... mn_utils import *
from ... utils.mn_node_utils import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_MatrixCombine(bpy.types.Node, AnimationNode):
    bl_idname = "mn_MatrixCombine"
    bl_label = "Combine Matrices"
    isDetermined = True
    
    def settingChanged(self, context):
        for socket in self.inputs:
            if socket.name != "...":
                socket.moveable = self.manageSockets
                socket.removeable = self.manageSockets
            
    manageSockets = BoolProperty(name = "Manage Sockets", default = False, description = "Allows to (re)move the input sockets", update = settingChanged)
    
    def init(self, context):
        forbidCompiling()
        self.newInputSocket()
        self.newInputSocket()
        self.inputs.new("mn_EmptySocket", "...").passiveSocketType = "mn_MatrixSocket"
        self.outputs.new("mn_MatrixSocket", "Result")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "manageSockets")
        
    def update(self):
        forbidCompiling()
        
        socket = self.inputs.get("...")
        updateDependencyNode(socket)
        
        if socket:
            nodeTree = self.id_data
            nodeTreeInfo = NodeTreeInfo(self.id_data)
            origin = nodeTreeInfo.getDataOriginSocket(socket)
            if getattr(origin, "dataType", "") in ["Matrix", "Vector"]:
                linkOrigin = socket.links[0].from_socket
                newSocket = self.newInputSocket()
                nodeTree.links.new(newSocket, linkOrigin)
                self.removeLinkFromEmptySocket()
            elif getattr(origin, "dataType", "") != "":
                self.removeLinkFromEmptySocket()
            
        allowCompiling()
    
    def removeLinkFromEmptySocket(self):
        try: self.id_data.links.remove(self.inputs.get("...").links[0])
        except: pass
        
    def newInputSocket(self):
        socket = self.inputs.new("mn_MatrixSocket", "Matrix")
        socket.removeable = self.manageSockets
        socket.moveable = self.manageSockets
        amount = len(self.inputs)
        self.inputs.move(amount - 1, amount - 2)
        return socket
        
    def execute(self, input):
        result = Matrix.Identity(4)
        
        sockets = self.inputs
        for socket in reversed(sockets):
            if socket.bl_idname == "mn_MatrixSocket":
                result *= input[socket.identifier]
        
        return { "Result" : result }
