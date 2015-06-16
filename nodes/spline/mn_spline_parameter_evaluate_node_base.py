from bpy.props import *
from ... mn_execution import nodePropertyChanged

parameterTypeItems = [
    ("RESOLUTION", "Resolution", ""),
    ("UNIFORM", "Uniform", "")]

class SplineParameterEvaluateNodeBase:
    parameterType = EnumProperty(name = "Parameter Type", default = "UNIFORM", items = parameterTypeItems, update = nodePropertyChanged)
    resolution = IntProperty(name = "Resolution", default = 100, min = 2, update = nodePropertyChanged, description = "Increase to have a more accurate evaluation if the type is set to Length")