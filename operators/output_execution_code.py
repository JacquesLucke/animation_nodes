import bpy
from . an_operator import AnimationNodeOperator
from .. execution.units import getExecutionUnitByNetwork

class PrintExecutionCode(bpy.types.Operator, AnimationNodeOperator):
    bl_idname = "an.print_execution_code"
    bl_label = "Print Execution Code"
    bl_description = "Print the code of the currently active node"

    def execute(self, context):
        network = context.active_node.network
        unit = getExecutionUnitByNetwork(network)
        print("\n"*5)
        print(unit.getCode())
        return {"FINISHED"}
