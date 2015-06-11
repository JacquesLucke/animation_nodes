import bpy
from bpy.props import *

'''
                ###############
                
    #########                      Second active node suggestion
    
#########                               First active node suggestion

    Debug Node                     All other active node suggestions
    
                ###############
                
How to implement suggestions on a per node basis:
1. Create a 'getNextNodeSuggestions(self)' function inside the node
2. Return a list that looks like this:
    [("mn_FloatMathNode", (0, 0)),                      # First suggestion
     ("mn_CombineVector", (0, 0)),                      # Second suggestion
     ("mn_FloatClamp", (0, 0)),                         # ... can be an unlimited amount of suggestions
     ("mn_CombineVector", (0, 0), (0, 1), (0, 2))]      # the tuples indicate which sockets to connect: (output index, input index)
'''

class ContextPie(bpy.types.Menu):
    bl_idname = "mn.context_pie"
    bl_label = "Context Pie"
    
    @classmethod
    def poll(cls, context):
        return animationNodeTreeActive()
    
    def drawLeft(self, context, layout):
        self.empty(layout)
        
    def drawRight(self, context, layout):
        if len(self.activeNodeSuggestions) > 0:
            self.drawInsertNodeOperator(layout, self.activeNodeSuggestions[0])
        else:
            self.empty(layout)
        
    def drawBottom(self, context, layout):
        self.empty(layout)
        
    def drawTop(self, context, layout):
        self.empty(layout)
        
    def drawTopLeft(self, context, layout):
        self.empty(layout)
        
    def drawTopRight(self, context, layout):
        if len(self.activeNodeSuggestions) > 1:
            self.drawInsertNodeOperator(layout, self.activeNodeSuggestions[1])
        else:
            self.empty(layout)
        
    def drawBottomLeft(self, context, layout):
        if activeNodeHasOutputs():
            layout.operator("mn.insert_debug_node")
        else: 
            self.empty(layout)
        
    def drawBottomRight(self, context, layout):
        amount = len(self.activeNodeSuggestions)
        if amount == 3:
            self.drawInsertNodeOperator(layout, self.activeNodeSuggestions[2])
        elif amount > 3:
            col = layout.column()
            for suggestion in self.activeNodeSuggestions[2:]:
                self.drawInsertNodeOperator(col, suggestion)
        else:
            self.empty(layout)
        
        
    def draw(self, context):
        self.prepare(context)
        
        pie = self.layout.menu_pie()
        self.drawLeft(context, pie)
        self.drawRight(context, pie)
        self.drawBottom(context, pie)
        self.drawTop(context, pie)
        self.drawTopLeft(context, pie)
        self.drawTopRight(context, pie)
        self.drawBottomLeft(context, pie)
        self.drawBottomRight(context, pie)
        
    def prepare(self, context):
        node = context.active_node
        try: self.activeNodeSuggestions = node.getNextNodeSuggestions()
        except: self.activeNodeSuggestions = []
        
    def empty(self, layout):
        layout.row().label("")
        
    def drawInsertNodeOperator(self, layout, data):
        nodeIdName = data[0]
        links = data[1:]
        
        props = layout.operator("mn.insert_linked_node", text = getNodeNameFromIdName(nodeIdName))
        props.nodeType = nodeIdName
        for origin, target in links:
            item = props.links.add()
            item.origin = origin
            item.target = target
        
        
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
        

class LinkedIndices(bpy.types.PropertyGroup):
    origin = IntProperty(default = 0)
    target = IntProperty(default = 0)
        
class InsertLinkedNode(bpy.types.Operator):
    bl_idname = "mn.insert_linked_node"
    bl_label = "Insert Linked Node"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    nodeType = StringProperty(default = "")
    links = CollectionProperty(type = LinkedIndices)
    
    @classmethod
    def poll(cls, context):
        return activeNodeHasOutputs() and animationNodeTreeActive()   

    def invoke(self, context, event):
        storeCursorLocation(event)
        
        nodeTree = getActiveAnimationNodeTree()
        originNode = getActiveNode()
        node = insertNode(self.nodeType)
        for item in self.links:
            nodeTree.links.new(node.inputs[item.target], originNode.outputs[item.origin])
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
    
    
def getNodeNameFromIdName(idName):
    try: return getattr(bpy.types, idName).bl_label
    except: return ""
    
    
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