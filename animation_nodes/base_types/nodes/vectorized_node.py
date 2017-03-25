from collections import defaultdict
from . base_node import AnimationNode
from ... sockets.info import toListDataType
from .. effects import AutoSelectVectorization

class VectorizedNode(AnimationNode):

    def create(self):
        self.vectorization = AutoSelectVectorization()
        self.createVectorized()
        self.newSocketEffect(self.vectorization)

    def newVectorizedInput(self, dataType, properties, baseData, listData):
        properties = self._formatInputProperties(properties)

        baseDataType = dataType
        listDataType = toListDataType(dataType)

        socket = self.newInputGroup(getattr(self, properties[0]),
            [baseDataType] + list(baseData),
            [listDataType] + list(listData))

        self.vectorization.input(self, properties[0], socket, properties[1])

    def newVectorizedOutput(self, dataType, properties, baseData, listData):
        properties = self._formatOutputProperties(properties)

        baseDataType = dataType
        listDataType = toListDataType(dataType)

        socket = self.newOutputGroup(self._evaluateOutputProperties(properties),
            [baseDataType] + list(baseData),
            [listDataType] + list(listData))

        self.vectorization.output(self, properties, socket)

    def _formatInputProperties(self, properties):
        if isinstance(properties, str):
            return (properties, [])
        return properties

    def _formatOutputProperties(self, properties):
        if isinstance(properties, str):
            return [(properties, )]
        return properties

    def _evaluateInputProperties(self, properties):
        if not getattr(self, properties[0]):
            return False
        for group in properties[1]:
            if isinstance(group, str):
                if not getattr(self, group):
                    return False
            else:
                if not any(getattr(self, prop) for prop in group):
                    return False
        return True

    def _evaluateOutputProperties(self, properties):
        for group in properties:
            if isinstance(group, str):
                if not getattr(self, group):
                    return False
            else:
                if not any(getattr(self, prop) for prop in group):
                    return False
        return True
