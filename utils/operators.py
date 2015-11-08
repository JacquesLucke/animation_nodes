import bpy

createdOperators = []

def makeOperator(idName, label):
    def makeOperatorDecorator(function):
        operator = getOperatorForFunction(function, idName, label)
        bpy.utils.register_class(operator)
        createdOperators.append(operator)
        return function
    return makeOperatorDecorator

def getOperatorForFunction(function, idName, label):
    def execute(self, context):
        function()
        return {"FINISHED"}

    operator = type(idName, (bpy.types.Operator, ), {
        "bl_idname" : idName,
        "bl_label" : label,
        "execute" : execute })
    return operator

def register():
    for operator in createdOperators:
        try: bpy.utils.register_class(operator)
        except: pass

def unregister():
    for operator in createdOperators:
        bpy.utils.unregister_class(operator)
