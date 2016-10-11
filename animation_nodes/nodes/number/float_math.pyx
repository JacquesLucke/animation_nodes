import bpy
from bpy.props import *
from ... data_structures cimport DoubleList
from ... base_types import AnimationNode, AutoSelectVectorization
from ... math cimport (add, subtract, multiply, divide_Save,
                       sin, cos, tan, asin_Save, acos_Save, atan, atan2, hypot,
                       power_Save)

ctypedef double (*SingleInputFunction)(double a)
ctypedef double (*DoubleInputFunction)(double a, double b)

cdef class Operation:
    cdef:
        readonly str name
        readonly str label
        readonly str type
        readonly str expression
        void* function

    cdef setup(self, str name, str label, str type, str expression, void* function):
        self.name = name
        self.label = label
        self.type = type
        self.expression = expression
        self.function = function

    def execute_A(self, DoubleList a):
        cdef DoubleList result = DoubleList(length = a.length)
        cdef SingleInputFunction f = <SingleInputFunction>self.function
        cdef long i
        for i in range(result.length):
            result.data[i] = f(a.data[i])
        return result

    def execute_A_B(self, a, b):
        if isinstance(a, DoubleList) and isinstance(b, DoubleList):
            if len(a) == len(b):
                return self._execute_A_B_Both(a, b)
            else:
                raise ValueError("lists have different length")
        elif isinstance(a, DoubleList):
            return self._execute_A_B_Left(a, b)
        elif isinstance(b, DoubleList):
            return self._execute_A_B_Right(a, b)

    def _execute_A_B_Both(self, DoubleList a, DoubleList b):
        cdef DoubleList result = DoubleList(length = a.length)
        cdef DoubleInputFunction f = <DoubleInputFunction>self.function
        cdef long i
        for i in range(result.length):
            result.data[i] = f(a.data[i], b.data[i])
        return result

    def _execute_A_B_Left(self, DoubleList a, double b):
        cdef DoubleList result = DoubleList(length = a.length)
        cdef DoubleInputFunction f = <DoubleInputFunction>self.function
        cdef long i
        for i in range(result.length):
            result.data[i] = f(a.data[i], b)
        return result

    def _execute_A_B_Right(self, double a, DoubleList b):
        cdef DoubleList result = DoubleList(length = b.length)
        cdef DoubleInputFunction f = <DoubleInputFunction>self.function
        cdef long i
        for i in range(result.length):
            result.data[i] = f(a, b.data[i])
        return result

cdef new(str name, str label, str type, str expression, void* function):
    cdef Operation op = Operation()
    op.setup(name, label, type, expression, function)
    return op

cdef list operations = [None] * 13

# Changing the order can break existing files
operations[0] = new("Add", "A + B", "A_B",
    "result = a + b", <void*>add)
operations[1] = new("Subtract", "A - B", "A_B",
    "result = a + b", <void*>subtract)
operations[2] = new("Multiply", "A * B", "A_B",
    "result = a * b", <void*>multiply)
operations[3] = new("Divide", "A / B", "A_B",
    "result = a / b", <void*>divide_Save)
operations[4] = new("Sin", "sin A", "A",
    "result = math.sin(a)", <void*>sin)
operations[5] = new("Cos", "cos A", "A",
    "result = math.cos(a)", <void*>cos)
operations[6] = new("Tangent", "tan A", "A",
    "result = math.tan(a)", <void*>tan)
operations[7] = new("Arcsin", "asin A", "A",
    "result = math.asin(min(max(a, -1), 1))", <void*>asin_Save)
operations[8] = new("Arccosine", "acos A", "A",
    "result = math.acos(min(max(a, -1), 1))", <void*>acos_Save)
operations[9] = new("Arctangent", "atan A", "A",
    "result = math.atan(a)", <void*>atan)
operations[10] = new("Arctangent B/A", "atan2 (B / A)", "A_B",
    "result = math.atan2(b, a)", <void*>atan2)
operations[11] = new("Hypotenuse", "hypot A, B", "A_B",
    "result = math.hypot(a, b)", <void*>hypot)
operations[12] = new("Power", "A^B", "Base_Exponent",
    "result = math.pow(base, exponent) if base >= 0 or exponent % 1 == 0 else 0", <void*>power_Save)


operationItems = [(op.name, op.name, op.label, i) for i, op in enumerate(operations)]
operationByName = {op.name : op for op in operations}

class FloatMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatMathNode"
    bl_label = "Math"
    dynamicLabelType = "HIDDEN_ONLY"

    operation = EnumProperty(name = "Operation",
        description = "Operation to perform on the inputs",
        items = operationItems, update = AnimationNode.updateSockets)

    errorMessage = StringProperty()

    useListA = BoolProperty(default = False, update = AnimationNode.updateSockets)
    useListB = BoolProperty(default = False, update = AnimationNode.updateSockets)
    useListBase = BoolProperty(default = False, update = AnimationNode.updateSockets)
    useListExponent = BoolProperty(default = False, update = AnimationNode.updateSockets)

    def create(self):
        vectorization = AutoSelectVectorization()
        usedProperties = []

        for name in self._operation.type.split("_"):
            listProperty = "useList" + name
            socket = self.newInputGroup(getattr(self, listProperty),
                ("Float", name, name.lower()),
                ("Float List", name, name.lower()))
            vectorization.input(self, listProperty, socket)
            usedProperties.append(listProperty)

        self.newOutputGroup(self.generatesList,
            ("Float", "Result", "result"),
            ("Float List", "Result", "result"))

        vectorization.output(self, [usedProperties], self.outputs[0])
        self.newSocketEffect(vectorization)

    def draw(self, layout):
        layout.prop(self, "operation", text = "")
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawLabel(self):
        return self._operation.label

    def getExecutionCode(self):
        if self.generatesList:
            currentType = self._operation.type
            if currentType == "A":
                yield "result = self._operation.execute_A(a)"
            elif currentType == "A_B":
                yield "result = self._operation.execute_A_B(a, b)"
            elif currentType == "Base_Exponent":
                yield "result = self._operation.execute_A_B(base, exponent)"
        else:
            yield self._operation.expression

    def getUsedModules(self):
        return ["math"]

    @property
    def _operation(self):
        return operationByName[self.operation]

    @property
    def generatesList(self):
        return any(socket.dataType == "Float List" for socket in self.inputs)
