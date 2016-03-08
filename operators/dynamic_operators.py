import bpy
from bpy.props import *
from .. utils.handlers import eventHandler
from .. utils.nodes import getNode, getSocket

operatorsByDescription = {}
missingDescriptions = set()

def getInvokeFunctionOperator(description):
    if description in operatorsByDescription:
        return operatorsByDescription[description]
    missingDescriptions.add(description)
    return fallbackOperator.bl_idname


@eventHandler("SCENE_UPDATE_POST")
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
        "bl_label" : "Are you sure?",
        "bl_description" : description,
        "invoke" : invoke_InvokeFunction,
        "execute" : execute_InvokeFunction })
    operator.classType = StringProperty() # 'NODE' or 'SOCKET'
    operator.treeName = StringProperty()
    operator.nodeName = StringProperty()
    operator.isOutput = BoolProperty()
    operator.identifier = StringProperty()
    operator.functionName = StringProperty()
    operator.invokeWithData = BoolProperty(default = False)
    operator.confirm = BoolProperty()
    operator.data = StringProperty()

    return operator

def invoke_InvokeFunction(self, context, event):
    if self.confirm:
        return context.window_manager.invoke_confirm(self, event)
    return self.execute(context)

def execute_InvokeFunction(self, context):
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

def register():
    try: bpy.utils.register_class(fallbackOperator)
    except: pass

def unregister():
    try: bpy.utils.unregister_class(fallbackOperator)
    except: pass
