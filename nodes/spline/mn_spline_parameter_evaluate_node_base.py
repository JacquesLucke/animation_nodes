from bpy.props import *

parameterTypeItems = [
    ("RESOLUTION", "Resolution", ""),
    ("LENGTH", "Length", "")]

class SplineParameterEvaluateNodeBase:
    parameterType = EnumProperty(name = "Parameter Type", default = "LENGTH", items = parameterTypeItems)
    resolution = IntProperty(name = "Resolution", default = 100, min = 2, description = "Increase to have a more accurate evaluation if the type is set to Length")