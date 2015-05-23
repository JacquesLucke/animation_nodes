import bpy
from bpy.props import *

class ContextPie(bpy.types.Menu):
    bl_idname = "mn.context_pie"
    bl_label = "Context Pie"
    
    @classmethod
    def poll(cls, context):
        return context.active_node and animationNodeTreeActive()
    
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("mn.insert_debug_node")
        
        outputDataType = getFirstOutputTypeOfActiveSocket()
        if outputDataType in ["Integer", "Float"]:
            pie.operator("mn.insert_linked_node", text = "Math").nodeType = "mn_FloatMathNode"
        if outputDataType == "Object":
            pie.operator("mn.insert_linked_node", text = "Transforms Output").nodeType = "mn_ObjectTransformsOutput"
        
        
        
class InsertDebugNode(bpy.types.Operator):
    bl_idname = "mn.insert_debug_node"
    bl_label = "Insert Debug Node"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    socketIndex = IntProperty(default = 0)
    
    @classmethod
    def poll(cls, context):
        return activeNodeHasOutputs() and animationNodeTreeActive()
        
    def invoke(self, context, event):
        storeCursorLocation(event)
        amount = len(context.active_node.outputs)
        if amount == 1:
            self.socketIndex = 0
            self.execute(context)
        elif amount >= 2:
            context.window_manager.popup_menu(self.drawSocketChooser, title = "Choose Socket")
        return {"FINISHED"}
        
    def drawSocketChooser(tmp, self, context):
        col = self.layout.column()
        col.operator_context = "EXEC_DEFAULT"
        for i, socket in enumerate(context.active_node.outputs):
            if not socket.hide:
                props = col.operator("mn.insert_debug_node", text = socket.name)
                props.socketIndex = i
            
    def execute(self, context):
        nodeTree = getActiveAnimationNodeTree()
        originNode = getActiveNode()
        node = insertNode("mn_DebugOutputNode")
        nodeTree.links.new(node.inputs[0], originNode.outputs[self.socketIndex])
        onlySelect(node)
        bpy.ops.transform.translate("INVOKE_DEFAULT")
        return{"FINISHED"} 
        
class InsertLinkedNode(bpy.types.Operator):
    bl_idname = "mn.insert_linked_node"
    bl_label = "Insert Linked Node"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    originIndex = IntProperty(default = 0)
    targetIndex = IntProperty(default = 0)
    nodeType = StringProperty(default = "")
    
    @classmethod
    def poll(cls, context):
        return activeNodeHasOutputs() and animationNodeTreeActive()   

    def invoke(self, context, event):
        storeCursorLocation(event)
        
        nodeTree = getActiveAnimationNodeTree()
        originNode = getActiveNode()
        node = insertNode(self.nodeType)
        nodeTree.links.new(node.inputs[self.targetIndex], originNode.outputs[self.originIndex])
        onlySelect(node)
        bpy.ops.transform.translate("INVOKE_DEFAULT")
        return{"FINISHED"} 
      
                
def insertNode(type):
    space = bpy.context.space_data
    nodeTree = space.node_tree
    node = nodeTree.nodes.new(type)
    node.location = space.cursor_location
    return node
    
def storeCursorLocation(event):
    space = bpy.context.space_data
    nodeTree = space.node_tree
    space.cursor_location_from_region(event.mouse_region_x, event.mouse_region_y)    
    
def onlySelect(node):
    bpy.ops.node.select_all(action = "DESELECT")
    node.select = True
    node.id_data.nodes.active = node 
    
    
def getFirstOutputTypeOfActiveSocket():    
    if not activeNodeHasOutputs(): return ""
    socket = getActiveNode().outputs[0]
    return socket.dataType
    
def activeNodeHasOutputs():
    if not activeNodeExists(): return False
    node = getActiveNode()
    return len(node.outputs) > 0
    
def activeNodeExists():
    try: return getActiveNode() is not None
    except: return False
    
def getActiveNode():
    return getattr(bpy.context, "active_node", None)
    
def animationNodeTreeActive():
    try: return getActiveAnimationNodeTree() is not None
    except: return False    
    
def getActiveAnimationNodeTree():
    try:
        nodeTree = bpy.context.space_data.edit_tree
        if nodeTree.bl_idname == "mn_AnimationNodeTree": return nodeTree
    except: pass
    return None