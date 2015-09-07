import bpy
from bpy.props import *
from .. utils.nodes import getNode, getSocket
from bpy.app.handlers import persistent

operatorsByDescription = {}
missingDescriptions = set()

def getInvokeFunctionOperator(description):
    if description in operatorsByDescription:
        return operatorsByDescription[description]
    missingDescriptions.add(description)
    return fallbackOperator.bl_idname


@persistent
def createMissingOperators(scene):
    while len(missingDescriptions) > 0:
        description = missingDescriptions.pop()
        operator = createOperatorWithDescription(description)
        operatorsByDescription[description] = operator.bl_idname
        bpy.utils.register_class(operator)

def createOperatorWithDescription(description):
    operatorID = str(len(operatorsByDescription))
    idName = "an.invoke_function_" + operatorID

    operator = type("InvokeFunction_" + operatorID, (bpy.types.Operator, ), {
        "bl_idname" : idName,
        "bl_label" : "Invoke Function",
        "bl_description" : description,
        "execute" : invokeFunction })
    operator.classType = StringProperty() # 'NODE' or 'SOCKET'
    operator.treeName = StringProperty()
    operator.nodeName = StringProperty()
    operator.isOutput = BoolProperty()
    operator.identifier = StringProperty()
    operator.functionName = StringProperty()
    operator.invokeWithData = BoolProperty(default = False)
    operator.data = StringProperty()

    return operator

def invokeFunction(self, context):
    if self.classType == "NODE":
        owner = getNode(self.treeName, self.nodeName)
    elif self.classType == "SOCKET":
        owner = getSocket(self.treeName, self.nodeName, self.isOutput, self.identifier)

    function = getattr(owner, self.functionName)
    if self.invokeWithData: function(self.data)
    else: function()
    bpy.context.area.tag_redraw()
    return {"FINISHED"}

fallbackOperator = createOperatorWithDescription("")


# Register
##################################

def registerHandlers():
    try: bpy.utils.register_class(fallbackOperator)
    except: pass
    bpy.app.handlers.scene_update_post.append(createMissingOperators)

def unregisterHandlers():
    try: bpy.utils.unregister_class(fallbackOperator)
    except: pass
    bpy.app.handlers.scene_update_post.remove(createMissingOperators)
