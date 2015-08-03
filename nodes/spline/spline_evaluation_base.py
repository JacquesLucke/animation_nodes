from bpy.props import *
from ... mn_execution import nodePropertyChanged
from ... events import propertyChanged

parameterTypeItems = [
    ("RESOLUTION", "Resolution", ""),
    ("UNIFORM", "Uniform", "")]

class SplineEvaluationBase:

    parameterType = EnumProperty(
        name = "Parameter Type",
        default = "UNIFORM",
        items = parameterTypeItems,
        update = propertyChanged)

    resolution = IntProperty(
        name = "Resolution",
        min = 2, 
        default = 100,
        update = propertyChanged,
        description = "Increase to have a more accurate evaluation if the type is set to Length")
