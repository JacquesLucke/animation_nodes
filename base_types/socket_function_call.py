import bpy
from bpy.props import *
from bpy.app.handlers import persistent
from .. utils.nodes import getSocket

operatorsByDescription = {}
missingDescriptions = []

def getInvokeSocketFunctionOperator(description):
    if description in operatorsByDescription:
        return operatorsByDescription[description]
    missingDescriptions.append(description)
    return "an.call_socket_function_fallback"

class InvokeSocketFunctionFallback(bpy.types.Operator):
    bl_idname = "an.invoke_socket_function_fallback"
    bl_label = "Invoke Socket Function"

    nodeTreeName = StringProperty()
    nodeName = StringProperty()
    isOutput = BoolProperty()
    identifier = StringProperty()
    functionName = StringProperty()

    def invoke(self, context, event):
        invokeSocketFunction(self, context, event)

def invokeSocketFunction(self, context, event):
    socket = getSocket(self.nodeTreeName, self.nodeName, self.isOutput, self.identifier)
    getattr(socket, self.functionName)()
    bpy.context.area.tag_redraw()
    return {"FINISHED"}


@persistent
def createMissingOperators(scene):
    for description in missingDescriptions:
        createOperatorWithDescription(description)
    missingDescriptions.clear()

def createOperatorWithDescription(description):
    operatorID = str(len(operatorsByDescription))
    idName = "an.invoke_socket_function_" + operatorID
    operatorsByDescription[description] = idName

    operatorType = type("InvokeSocketFunction_" + operatorID, (bpy.types.Operator,), {
        "bl_idname" : idName,
        "bl_label" : "Invoke Socket Function",
        "bl_description" : description,
        "invoke" : invokeSocketFunction })
    operatorType.nodeTreeName = StringProperty()
    operatorType.nodeName = StringProperty()
    operatorType.isOutput = BoolProperty()
    operatorType.identifier = StringProperty()
    operatorType.functionName = StringProperty()

    bpy.utils.register_class(operatorType)


# Register
##################################

def registerHandlers():
    bpy.app.handlers.scene_update_post.append(createMissingOperators)

def unregisterHandlers():
    bpy.app.handlers.scene_update_post.remove(createMissingOperators)
