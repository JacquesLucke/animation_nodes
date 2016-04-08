import bpy
import inspect
from bpy.props import *
from . blender_ui import redrawAll

createdOperators = []

def makeOperator(idName, label, arguments = [], redraw = False):
    def makeOperatorDecorator(function):
        operator = getOperatorForFunction(function, idName, label, arguments, redraw)
        bpy.utils.register_class(operator)
        createdOperators.append(operator)
        return function
    return makeOperatorDecorator

def getOperatorForFunction(function, idName, label, arguments, redraw):
    def execute(self, context):
        parameters = list(iterParameterNamesAndDefaults(function))
        function(*[getattr(self, name) for name, _ in parameters])
        if redraw:
            redrawAll()
        return {"FINISHED"}

    operator = type(idName, (bpy.types.Operator, ), {
        "bl_idname" : idName,
        "bl_label" : label,
        "execute" : execute })

    parameters = list(iterParameterNamesAndDefaults(function))
    for argument, (name, default) in zip(arguments, parameters):
        if argument == "Int": propertyType = IntProperty
        if argument == "String": propertyType = StringProperty

        if default is None: setattr(operator, name, propertyType())
        else: setattr(operator, name, propertyType(default = default))

    return operator

def iterParameterNamesAndDefaults(function):
    for parameter in inspect.signature(function).parameters.values():
        default = parameter.default if isinstance(parameter.default, (int, float, str)) else None
        yield (parameter.name, default)

def register():
    for operator in createdOperators:
        try: bpy.utils.register_class(operator)
        except: pass

def unregister():
    for operator in createdOperators:
        bpy.utils.unregister_class(operator)
