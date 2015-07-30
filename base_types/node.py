import bpy
from bpy.props import *
from bpy.app.handlers import persistent
from .. mn_execution import allowCompiling, forbidCompiling
from .. utils.mn_node_utils import getNode

class AnimationNode:
    @classmethod
    def poll(cls, nodeTree):
        return nodeTree.bl_idname == "mn_AnimationNodeTree"
        
    def init(self, context):
        forbidCompiling()
        self.create()
        allowCompiling()
        
    def copy(self, sourceNode):
        forbidCompiling()
        self.duplicate(sourceNode)
        allowCompiling()
        
    def free(self):
        forbidCompiling()
        self.delete()
        allowCompiling()
        
    def callFunctionFromUI(self, layout, functionName, text = "", icon = "NONE", description = ""):
        idName = getNodeFunctionCallOperatorName(description)
        props = layout.operator(idName, text = text, icon = icon)
        props.nodeTreeName = self.id_data.name
        props.nodeName = self.name
        props.functionName = functionName
        
nodeFunctionCallOperators = {}
missingNodeOperators = []

def getNodeFunctionCallOperatorName(description):
    if description in nodeFunctionCallOperators:
        return nodeFunctionCallOperators[description]
    missingNodeOperators.append(description)
    return "mn.call_node_function_fallback"

class CallNodeFunctionFallback(bpy.types.Operator):
    bl_idname = "mn.call_node_function_fallback"
    bl_label = "Call Node Function"
    
    nodeTreeName = StringProperty()
    nodeName = StringProperty()
    functionName = StringProperty()
    
    def invoke(self, context, event):
        invokeNodeFunctionCall(self, context, event)
 
def invokeNodeFunctionCall(self, context, event):
    node = getNode(self.nodeTreeName, self.nodeName)
    getattr(node, self.functionName)()
    return {"FINISHED"}

    
@persistent    
def createMissingOperators(scene):
    for description in missingNodeOperators:
        createNodeFunctionCallOperator(description)
    missingNodeOperators.clear()
    
def createNodeFunctionCallOperator(description):
    if description not in nodeFunctionCallOperators:
    
        id = str(len(nodeFunctionCallOperators))
        idName = "mn.call_node_function_" + id
        nodeFunctionCallOperators[description] = idName
        
        operatorType = type("CallNodeFunction_" + id, (bpy.types.Operator,), {
            "bl_idname" : idName,
            "bl_label" : "Call Node Function",
            "bl_description" : description,
            "invoke" : invokeNodeFunctionCall })
        operatorType.nodeTreeName = StringProperty()
        operatorType.nodeName = StringProperty()
        operatorType.functionName = StringProperty()
        
        bpy.utils.register_class(operatorType)
        
        
# Register
################################## 

def register_handlers():    
    bpy.app.handlers.scene_update_post.append(createMissingOperators)
    
def unregister_handlers():
    bpy.app.handlers.scene_update_post.remove(createMissingOperators)           