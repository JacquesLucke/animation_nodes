import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import getSocketDataTypeItems, getIdNameFromDataType
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

def getListTypeItems(self, context):
    listTypeItems = []
    for idName in getListSocketIdNames():
        baseIdName = getListBaseSocketIdName(idName)
        cls = getSocketClassFromIdName(baseIdName)
        item = (idName, cls.dataType, "")
        listTypeItems.append(item)
    return listTypeItems

class mn_DataInput(bpy.types.Node, AnimationNode):
    bl_idname = "mn_DataInput"
    bl_label = "Data Input"
    
    selectedType = EnumProperty(name = "Type", items = getSocketDataTypeItems)
    assignedType = StringProperty(default = "Float")
    
    def init(self, context):
        forbidCompiling()
        self.recreateSockets()
        allowCompiling()
        
    def draw_buttons_ext(self, context, layout):
        col = layout.column(align = True)
        col.prop(self, "selectedType", text = "")
        props = col.operator("mn.assign_selected_socket_type_to_data_input_node", text = "Assign")
        props.nodeTreeName = self.id_data.name
        props.nodeName = self.name
        
    def getInputSocketNames(self):
        return {"Input" : "input"}
    def getOutputSocketNames(self):
        return {"Output" : "output"}
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        return "$output$ = %input%"
        
    def assignSocketType(self, dataType):
        self.assignedType = dataType
        self.recreateSockets()
        
    def recreateSockets(self):
        forbidCompiling()
        self.inputs.clear()
        self.outputs.clear()
        
        idName = getIdNameFromDataType(self.assignedType)
        socket = self.inputs.new(idName, "Input")
        self.setupSocket(socket)
        socket = self.outputs.new(idName, "Output")
        self.setupSocket(socket)
        
        allowCompiling()
        nodeTreeChanged()
        
    def setupSocket(self, socket):
        socket.displayCustomName = True
        socket.uniqueCustomName = False
        socket.customName = self.assignedType
        
        
class AssignListType(bpy.types.Operator):
    bl_idname = "mn.assign_selected_socket_type_to_data_input_node"
    bl_label = "Assign Socket Type"
    bl_description = "Remove all sockets and set the selected socket type"
    bl_options = {"REGISTER"}
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
    
    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        node.assignSocketType(node.selectedType)
        return {"FINISHED"}             