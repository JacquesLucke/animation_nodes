import bpy
from .. sockets.info import isList
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

    def drawRight(self, layout):
        col = layout.column(align = True)
        for socket in self.activeNode.outputs:
            if isList(socket.bl_idname):
                props = col.operator("an.insert_loop_for_iteration_template", text = "Loop through {}".format(repr(socket.getDisplayedName())))
                props.nodeIdentifier = self.activeNode.identifier
                props.socketIndex = socket.index

    @property
    def activeNode(self):
        return bpy.context.active_node
