import bpy
from .. utils.blender_ui import PieMenuHelper

'''
                ###############

    #########                      #########

 Data Input                               #########

    #########                      #########

                  Debug Node

'''

class ContextPie(bpy.types.Menu, PieMenuHelper):
    bl_idname = "an.context_pie"
    bl_label = "Context Pie"

    @classmethod
    def poll(cls, context):
        try: return context.active_node.isAnimationNode
        except: return False

    def drawLeft(self, layout):
        amount = len(self.activeNode.getVisibleInputs())
        if amount == 0: self.empty(layout, text = "Has no visible inputs")
        else: layout.operator("an.insert_data_input_node_template_operator", text = "Data Input")

    def drawBottom(self, layout):
        amount = len(self.activeNode.getVisibleOutputs())
        if amount == 0: self.empty(layout, text = "Has no visible outputs")
        else: layout.operator("an.insert_debug_node_template_operator", text = "Debug")

    @property
    def activeNode(self):
        return bpy.context.active_node
