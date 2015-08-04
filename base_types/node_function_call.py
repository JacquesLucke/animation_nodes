import bpy
from bpy.props import *
from bpy.app.handlers import persistent
from .. utils.nodes import getNode

nodeFunctionCallOperators = {}
missingNodeOperators = []

def getNodeFunctionCallOperatorName(description):
    if description in nodeFunctionCallOperators:
        return nodeFunctionCallOperators[description]
    missingNodeOperators.append(description)
    return "an.call_node_function_fallback"

class CallNodeFunctionFallback(bpy.types.Operator):
    bl_idname = "an.call_node_function_fallback"
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
        idName = "an.call_node_function_" + id
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

def registerHandlers():
    bpy.app.handlers.scene_update_post.append(createMissingOperators)

def unregisterHandlers():
    bpy.app.handlers.scene_update_post.remove(createMissingOperators)
