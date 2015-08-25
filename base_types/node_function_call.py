import bpy
import inspect
from bpy.props import *
from bpy.app.handlers import persistent
from .. utils.nodes import getNode

operatorsByDescription = {}
missingDescriptions = []

def getInvokeNodeFunctionOperator(description):
    if description in operatorsByDescription:
        return operatorsByDescription[description]
    missingDescriptions.append(description)
    return "an.invoke_node_function_fallback"

class InvokeNodeFunctionFallback(bpy.types.Operator):
    bl_idname = "an.invoke_node_function_fallback"
    bl_label = "Invoke Node Function"

    nodeTreeName = StringProperty()
    nodeName = StringProperty()
    functionName = StringProperty()
    invokeWithData = BoolProperty(default = False)
    data = StringProperty()

    def invoke(self, context, event):
        invokeNodeFunction(self, context, event)

def invokeNodeFunction(self, context, event):
    node = getNode(self.nodeTreeName, self.nodeName)
    function = getattr(node, self.functionName)
    if self.invokeWithData: function(self.data)
    else: function()
    bpy.context.area.tag_redraw()
    return {"FINISHED"}


@persistent
def createMissingOperators(scene):
    for description in missingDescriptions:
        createOperatorWithDescription(description)
    missingDescriptions.clear()

def createOperatorWithDescription(description):
    operatorID = str(len(operatorsByDescription))
    idName = "an.invoke_node_function_" + operatorID
    operatorsByDescription[description] = idName

    operatorType = type("InvokeNodeFunction_" + operatorID, (bpy.types.Operator,), {
        "bl_idname" : idName,
        "bl_label" : "Invoke Node Function",
        "bl_description" : description,
        "invoke" : invokeNodeFunction })
    operatorType.nodeTreeName = StringProperty()
    operatorType.nodeName = StringProperty()
    operatorType.functionName = StringProperty()
    operatorType.invokeWithData = BoolProperty(default = False)
    operatorType.data = StringProperty()

    bpy.utils.register_class(operatorType)


# Register
##################################

def registerHandlers():
    bpy.app.handlers.scene_update_post.append(createMissingOperators)

def unregisterHandlers():
    bpy.app.handlers.scene_update_post.remove(createMissingOperators)
