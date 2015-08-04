import bpy
from bpy.props import *
from bpy.app.handlers import persistent
from .. old_utils import getSocket

socketFunctionCallOperators = {}
missingSocketOperators = []

def getSocketFunctionCallOperatorName(description):
    if description in socketFunctionCallOperators:
        return socketFunctionCallOperators[description]
    missingSocketOperators.append(description)
    return "an.call_socket_function_fallback"

class CallSocketFunctionFallback(bpy.types.Operator):
    bl_idname = "an.call_socket_function_fallback"
    bl_label = "Call Socket Function"

    nodeTreeName = StringProperty()
    nodeName = StringProperty()
    isOutput = BoolProperty()
    identifier = StringProperty()
    functionName = StringProperty()

    def invoke(self, context, event):
        invokeSocketFunctionCall(self, context, event)

def invokeSocketFunctionCall(self, context, event):
    socket = getSocket(self.nodeTreeName, self.nodeName, self.isOutput, self.identifier)
    getattr(socket, self.functionName)()
    return {"FINISHED"}


@persistent
def createMissingOperators(scene):
    for description in missingSocketOperators:
        createSocketFunctionCallOperator(description)
    missingSocketOperators.clear()

def createSocketFunctionCallOperator(description):
    if description not in socketFunctionCallOperators:

        id = str(len(socketFunctionCallOperators))
        idName = "an.call_socket_function_" + id
        socketFunctionCallOperators[description] = idName

        operatorType = type("CallSocketFunction_" + id, (bpy.types.Operator,), {
            "bl_idname" : idName,
            "bl_label" : "Call Socket Function",
            "bl_description" : description,
            "invoke" : invokeSocketFunctionCall })
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
