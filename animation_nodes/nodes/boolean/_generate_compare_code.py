numericListNames = (
    "FloatList",
    "DoubleList",
    "CharList",     "UCharList",
    "LongList",     "ULongList",
    "IntegerList",  "UIntegerList",
    "ShortList",    "UShortList",
    "LongLongList", "ULongLongList",
)

compareOperators = {
    "equal" : "==",
    "notEqual" : "!=",
    "greater" : ">",
    "less" : "<",
    "greaterEqual" : ">=",
    "lessEqual" : "<="
}

paths = {}
def setup(utils):
    global paths
    paths = {"compareListFunction" : utils.changeFileName(__file__, "__compare_list.src")}

def getPyPreprocessTasks(PyPreprocessTask, utils):
    return [PyPreprocessTask(
        target = utils.changeFileName(__file__, "compare_c_utils.pyx"),
        dependencies = [__file__, paths["compareListFunction"]],
        function = generateCompareCode
    )]

def generateCompareCode(target, utils):
    compareListFunction = utils.readTextFile(paths["compareListFunction"])

    parts = []
    parts.append("from ... data_structures cimport " + ", ".join(numericListNames + ("BooleanList",)))

    for listName in numericListNames:
        for compareName, operator in compareOperators.items():
            compareCode = utils.multiReplace(compareListFunction,
                COMPARENAME = compareName,
                LISTNAME = listName,
                OPERATOR = operator
            )
            parts.append(compareCode)

    utils.writeTextFile(target, "\n".join(parts))
