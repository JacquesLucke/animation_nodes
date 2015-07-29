import bpy
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.splines.from_blender import createSplinesFromBlenderObject

class mn_SplinesFromObject(bpy.types.Node, AnimationNode):
    bl_idname = "mn_SplinesFromObject"
    bl_label = "Splines from Object"
    
    useWorldTransform = bpy.props.BoolProperty(name = "Use World Transform", default = True, description = "Use the position in global space")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.outputs.new("mn_SplineListSocket", "Splines")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "useWorldTransform")
        
    def getInputSocketNames(self):
        return {"Object" : "object"}

    def getOutputSocketNames(self):
        return {"Splines" : "splines"}

    def execute(self, object):
        splines = createSplinesFromBlenderObject(object)
        if self.useWorldTransform:
            for spline in splines:
                spline.transform(object.matrix_world)
        return splines
