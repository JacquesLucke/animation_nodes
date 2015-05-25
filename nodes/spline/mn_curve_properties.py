import bpy
from bpy.types import Node
from bpy.props import *
from ... utils.mn_node_utils import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... sockets.mn_socket_info import getIdNameFromDataType

possibleProperties = {
    "bevel_depth" : ("Bevel Depth", "Float"),
    "bevel_resolution" : ("Bevel Resolution", "Integer"),
    "offset" : ("Offset", "Float"),
    "extrude" : ("Extrude", "Float"),
    "taper_object" : ("Taper Object", "Object"),
    "bevel_object" : ("Bevel Object", "Object"),
    "resolution_u" : ("Preview Resolution", "Integer"),
    "bevel_factor_start" : ("Bevel Start", "Float"),
    "bevel_factor_end" : ("Bevel End", "Float") }

class mn_CurveProperties(Node, AnimationNode):
    bl_idname = "mn_CurveProperties"
    bl_label = "Curve Properties"
    
    def getPossiblePropertyItems(self, context):
        items = []
        for path, (name, dataType) in possibleProperties.items():
            if not path in self.inputs:
                items.append((path, name, ""))
        if len(items) == 0: items.append(("NONE", "NONE", ""))
        items = sorted(items, key = lambda x: x[1])
        return items
        
    def settingChanged(self, context):
        for socket in self.inputs[1:]:
            socket.removeable = self.manageSockets
            socket.moveable = self.manageSockets
            
    selectedPath = EnumProperty(name = "Type", items = getPossiblePropertyItems)
    manageSockets = BoolProperty(name = "Manage Sockets", default = True, update = settingChanged, description = "Allows to add, move or remove sockets")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False        
        self.outputs.new("mn_ObjectSocket", "Object")
        self.width += 20
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "manageSockets")
        if self.manageSockets:
            row = layout.row(align = True)
            row.prop(self, "selectedPath", text = "")
            props = row.operator("mn.append_curve_property_socket", text = "", icon = "PLUS")
            props.nodeTreeName = self.id_data.name
            props.nodeName = self.name
        
    def execute(self, inputs):
        object = inputs["Object"]
        if getattr(object, "type", "") == "CURVE":
            for path, value in inputs.items():
                if path == "Object": continue
                setattr(object.data, path, value)
        return {"Object" : object}
        
    def newSocketFromSelection(self):
        path = self.selectedPath
        if path != "NONE":
            self.newSocket(path)
        
    def newSocket(self, path):
        name, dataType = possibleProperties[path]
        socket = self.inputs.new(getIdNameFromDataType(dataType), path)
        socket.customName = name
        socket.displayCustomName = True
        socket.removeable = True
        socket.moveable = True
        
class AppendSocket(bpy.types.Operator):
    bl_idname = "mn.append_curve_property_socket"
    bl_label = "Append Socket"
    bl_description = "Create a new socket for the selected property"
    bl_options = {"REGISTER"}
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
    
    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        node.newSocketFromSelection()
        return {"FINISHED"}          