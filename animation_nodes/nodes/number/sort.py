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
            yield "sortedNumbers = DoubleList.fromNumpyArray(numpy.sort(numbers.asMemoryView()))"
        if "indices" in required:
            yield "indices = LongList.fromNumpyArray(numpy.argsort(numbers.asMemoryView()))"

    def getUsedModules(self):
        return ["numpy"]
