import bpy
from . an_operator import AnimationNodeOperator
from .. execution.units import getExecutionUnitByNetwork

class PrintCurrentExecutionCode(bpy.types.Operator, AnimationNodeOperator):
    bl_idname = "an.print_current_execution_code"
    bl_label = "Print Execution Code"
    bl_description = "Print the code of the currently active node"

    def execute(self, context):
        code = getCurrentExecutionCode()
        print("\n" * 10)
        print("#### Code for network that contains the active node ####")
        print("\n" * 2)
        print(code)
        return {"FINISHED"}

class WriteCurrentExecutionCode(bpy.types.Operator, AnimationNodeOperator):
    bl_idname = "an.write_current_execution_code"
    bl_label = "Write Execution Code"
    bl_description = "Write the code of the currently active node in a text block"

    def execute(self, context):
        code = getCurrentExecutionCode()

        textBlockName = "Execution Code"
        textBlock = bpy.data.texts.get(textBlockName)
        if textBlock is None: textBlock = bpy.data.texts.new(textBlockName)

        textBlock.clear()
        textBlock.write(code)
        return {"FINISHED"}

def getCurrentExecutionCode():
    network = bpy.context.active_node.network
    unit = getExecutionUnitByNetwork(network)

    codes = [insertLineNumbers(code) for code in unit.getCodes()]
    return ("\n" * 3).join(codes)

def insertLineNumbers(code):
    lines = []
    for i, line in enumerate(code.split("\n")):
        lines.append("{:3}.  {}".format(i + 1, line))
    return "\n".join(lines)
