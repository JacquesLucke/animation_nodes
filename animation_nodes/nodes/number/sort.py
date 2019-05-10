import bpy
from ... base_types import AnimationNode

class SortNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SortNode"
    bl_label = "Sort"

    def create(self):
        self.newInput("Float List", "Numbers", "numbers")
        self.newOutput("Float List", "Sorted Numbers", "sortedNumbers")
        self.newOutput("Integer List", "Indices", "indices")

    def getExecutionCode(self, required):
        if "sortedNumbers" in required:
            yield "if len(numbers):"
            yield "    sortedNumbers = DoubleList.fromNumpyArray(numpy.sort(numbers.asMemoryView()))"
            yield "else:"
            yield "    sortedNumbers = DoubleList()"
        if "indices" in required:
            yield "if len(numbers):"
            yield "    indices = LongList.fromNumpyArray(numpy.argsort(numbers.asMemoryView()).astype(int))"
            yield "else:"
            yield "    indices = LongList()"

    def getUsedModules(self):
        return ["numpy"]
