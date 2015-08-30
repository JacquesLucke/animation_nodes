from bpy.props import *
from ... events import networkChanged

class SubprogramBaseNode:

    subprogramName = StringProperty(name = "Subprogram Name", default = "Subprogram",
        description = "Subprogram name to identify this group elsewhere",
        update = networkChanged)

    subprogramDescription = StringProperty(name = "Subprogram Description", default = "",
        description = "Short description about what this subprogram does",
        update = networkChanged)
