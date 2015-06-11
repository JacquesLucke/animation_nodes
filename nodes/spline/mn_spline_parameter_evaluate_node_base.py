from bpy.props import *
from ... mn_execution import nodePropertyChanged

parameterTypeItems = [
    ("RESOLUTION", "Resolution", ""),
    ("LENGTH", "Length", "")]

class SplineParameterEvaluateNodeBase:
    parameterType = EnumProperty(name = "Parameter Type", default = "LENGTH", items = parameterTypeItems, update = nodePropertyChanged)
    resolution = IntProperty(name = "Resolution", default = 100, min = 2, update = nodePropertyChanged, description = "Increase to have a more accurate evaluation if the type is set to Length")