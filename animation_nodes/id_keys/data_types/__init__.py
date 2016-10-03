from . text_type import TextDataType
from . float_type import FloatDataType
from . integer_type import IntegerDataType
from . transforms_type import TransformDataType


dataTypeByIdentifier = {
    "Text" : TextDataType,
    "Float" : FloatDataType,
    "Integer" : IntegerDataType,
    "Transforms" : TransformDataType
}

dataTypeIdentifiers = set(dataTypeByIdentifier.keys())
