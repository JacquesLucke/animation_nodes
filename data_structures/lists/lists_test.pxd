ctypedef fused list_or_tuple:
    list
    tuple

cdef class FloatList:
    cdef:
        float* data
        Py_ssize_t length
        Py_ssize_t capacity

    cdef grow(self, Py_ssize_t minCapacity)
    cdef void shrinkToLength(self)
    cdef replaceArray(self, float* newData, Py_ssize_t newLength, Py_ssize_t newCapacity)

    cpdef copy(self)
    cpdef clear(self)
    cpdef fill(self, value)

    cpdef append(self, value)
    cpdef extend(self, values)
    cdef extendList(self, list values)
    cdef extendTuple(self, tuple values)
    cpdef remove(self, value)
    cpdef index(self, value)
    cdef Py_ssize_t searchIndex(self, float value)
    cpdef count(self, value)
    cpdef insert(self, Py_ssize_t index, value)

    cpdef getMemoryView(self)

    cdef FloatList getValuesInSlice(self, slice sliceObject)
    cdef setValuesInSlice(self, slice sliceObject, values)
    cdef removeValuesInSlice(self, slice sliceObject)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values)
    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values)

    cdef getValueAtIndex(self, Py_ssize_t index)
    cdef setValueAtIndex(self, Py_ssize_t index, float value)
    cdef removeValueAtIndex(self, Py_ssize_t index)

    cpdef FloatList reversed(self)
    cdef overwrite(self, FloatList other, Py_ssize_t index = ?)
    cdef overwriteArray(self, float* array, Py_ssize_t arrayLength, Py_ssize_t index)

    # Helpers
    cdef tryConversion(self, value, float* target)
    cdef equals_SameType(self, FloatList other)
    cdef tryCorrectIndex(self, Py_ssize_t index)


cdef class DoubleList:
    cdef:
        double* data
        Py_ssize_t length
        Py_ssize_t capacity

    cdef grow(self, Py_ssize_t minCapacity)
    cdef void shrinkToLength(self)
    cdef replaceArray(self, double* newData, Py_ssize_t newLength, Py_ssize_t newCapacity)

    cpdef copy(self)
    cpdef clear(self)
    cpdef fill(self, value)

    cpdef append(self, value)
    cpdef extend(self, values)
    cdef extendList(self, list values)
    cdef extendTuple(self, tuple values)
    cpdef remove(self, value)
    cpdef index(self, value)
    cdef Py_ssize_t searchIndex(self, double value)
    cpdef count(self, value)
    cpdef insert(self, Py_ssize_t index, value)

    cpdef getMemoryView(self)

    cdef DoubleList getValuesInSlice(self, slice sliceObject)
    cdef setValuesInSlice(self, slice sliceObject, values)
    cdef removeValuesInSlice(self, slice sliceObject)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values)
    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values)

    cdef getValueAtIndex(self, Py_ssize_t index)
    cdef setValueAtIndex(self, Py_ssize_t index, double value)
    cdef removeValueAtIndex(self, Py_ssize_t index)

    cpdef DoubleList reversed(self)
    cdef overwrite(self, DoubleList other, Py_ssize_t index = ?)
    cdef overwriteArray(self, double* array, Py_ssize_t arrayLength, Py_ssize_t index)

    # Helpers
    cdef tryConversion(self, value, double* target)
    cdef equals_SameType(self, DoubleList other)
    cdef tryCorrectIndex(self, Py_ssize_t index)


cdef class CharList:
    cdef:
        char* data
        Py_ssize_t length
        Py_ssize_t capacity

    cdef grow(self, Py_ssize_t minCapacity)
    cdef void shrinkToLength(self)
    cdef replaceArray(self, char* newData, Py_ssize_t newLength, Py_ssize_t newCapacity)

    cpdef copy(self)
    cpdef clear(self)
    cpdef fill(self, value)

    cpdef append(self, value)
    cpdef extend(self, values)
    cdef extendList(self, list values)
    cdef extendTuple(self, tuple values)
    cpdef remove(self, value)
    cpdef index(self, value)
    cdef Py_ssize_t searchIndex(self, char value)
    cpdef count(self, value)
    cpdef insert(self, Py_ssize_t index, value)

    cpdef getMemoryView(self)

    cdef CharList getValuesInSlice(self, slice sliceObject)
    cdef setValuesInSlice(self, slice sliceObject, values)
    cdef removeValuesInSlice(self, slice sliceObject)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values)
    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values)

    cdef getValueAtIndex(self, Py_ssize_t index)
    cdef setValueAtIndex(self, Py_ssize_t index, char value)
    cdef removeValueAtIndex(self, Py_ssize_t index)

    cpdef CharList reversed(self)
    cdef overwrite(self, CharList other, Py_ssize_t index = ?)
    cdef overwriteArray(self, char* array, Py_ssize_t arrayLength, Py_ssize_t index)

    # Helpers
    cdef tryConversion(self, value, char* target)
    cdef equals_SameType(self, CharList other)
    cdef tryCorrectIndex(self, Py_ssize_t index)


cdef class UCharList:
    cdef:
        unsigned char* data
        Py_ssize_t length
        Py_ssize_t capacity

    cdef grow(self, Py_ssize_t minCapacity)
    cdef void shrinkToLength(self)
    cdef replaceArray(self, unsigned char* newData, Py_ssize_t newLength, Py_ssize_t newCapacity)

    cpdef copy(self)
    cpdef clear(self)
    cpdef fill(self, value)

    cpdef append(self, value)
    cpdef extend(self, values)
    cdef extendList(self, list values)
    cdef extendTuple(self, tuple values)
    cpdef remove(self, value)
    cpdef index(self, value)
    cdef Py_ssize_t searchIndex(self, unsigned char value)
    cpdef count(self, value)
    cpdef insert(self, Py_ssize_t index, value)

    cpdef getMemoryView(self)

    cdef UCharList getValuesInSlice(self, slice sliceObject)
    cdef setValuesInSlice(self, slice sliceObject, values)
    cdef removeValuesInSlice(self, slice sliceObject)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values)
    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values)

    cdef getValueAtIndex(self, Py_ssize_t index)
    cdef setValueAtIndex(self, Py_ssize_t index, unsigned char value)
    cdef removeValueAtIndex(self, Py_ssize_t index)

    cpdef UCharList reversed(self)
    cdef overwrite(self, UCharList other, Py_ssize_t index = ?)
    cdef overwriteArray(self, unsigned char* array, Py_ssize_t arrayLength, Py_ssize_t index)

    # Helpers
    cdef tryConversion(self, value, unsigned char* target)
    cdef equals_SameType(self, UCharList other)
    cdef tryCorrectIndex(self, Py_ssize_t index)


cdef class LongList:
    cdef:
        long* data
        Py_ssize_t length
        Py_ssize_t capacity

    cdef grow(self, Py_ssize_t minCapacity)
    cdef void shrinkToLength(self)
    cdef replaceArray(self, long* newData, Py_ssize_t newLength, Py_ssize_t newCapacity)

    cpdef copy(self)
    cpdef clear(self)
    cpdef fill(self, value)

    cpdef append(self, value)
    cpdef extend(self, values)
    cdef extendList(self, list values)
    cdef extendTuple(self, tuple values)
    cpdef remove(self, value)
    cpdef index(self, value)
    cdef Py_ssize_t searchIndex(self, long value)
    cpdef count(self, value)
    cpdef insert(self, Py_ssize_t index, value)

    cpdef getMemoryView(self)

    cdef LongList getValuesInSlice(self, slice sliceObject)
    cdef setValuesInSlice(self, slice sliceObject, values)
    cdef removeValuesInSlice(self, slice sliceObject)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values)
    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values)

    cdef getValueAtIndex(self, Py_ssize_t index)
    cdef setValueAtIndex(self, Py_ssize_t index, long value)
    cdef removeValueAtIndex(self, Py_ssize_t index)

    cpdef LongList reversed(self)
    cdef overwrite(self, LongList other, Py_ssize_t index = ?)
    cdef overwriteArray(self, long* array, Py_ssize_t arrayLength, Py_ssize_t index)

    # Helpers
    cdef tryConversion(self, value, long* target)
    cdef equals_SameType(self, LongList other)
    cdef tryCorrectIndex(self, Py_ssize_t index)


cdef class ULongList:
    cdef:
        unsigned long* data
        Py_ssize_t length
        Py_ssize_t capacity

    cdef grow(self, Py_ssize_t minCapacity)
    cdef void shrinkToLength(self)
    cdef replaceArray(self, unsigned long* newData, Py_ssize_t newLength, Py_ssize_t newCapacity)

    cpdef copy(self)
    cpdef clear(self)
    cpdef fill(self, value)

    cpdef append(self, value)
    cpdef extend(self, values)
    cdef extendList(self, list values)
    cdef extendTuple(self, tuple values)
    cpdef remove(self, value)
    cpdef index(self, value)
    cdef Py_ssize_t searchIndex(self, unsigned long value)
    cpdef count(self, value)
    cpdef insert(self, Py_ssize_t index, value)

    cpdef getMemoryView(self)

    cdef ULongList getValuesInSlice(self, slice sliceObject)
    cdef setValuesInSlice(self, slice sliceObject, values)
    cdef removeValuesInSlice(self, slice sliceObject)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values)
    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values)

    cdef getValueAtIndex(self, Py_ssize_t index)
    cdef setValueAtIndex(self, Py_ssize_t index, unsigned long value)
    cdef removeValueAtIndex(self, Py_ssize_t index)

    cpdef ULongList reversed(self)
    cdef overwrite(self, ULongList other, Py_ssize_t index = ?)
    cdef overwriteArray(self, unsigned long* array, Py_ssize_t arrayLength, Py_ssize_t index)

    # Helpers
    cdef tryConversion(self, value, unsigned long* target)
    cdef equals_SameType(self, ULongList other)
    cdef tryCorrectIndex(self, Py_ssize_t index)


cdef class IntegerList:
    cdef:
        int* data
        Py_ssize_t length
        Py_ssize_t capacity

    cdef grow(self, Py_ssize_t minCapacity)
    cdef void shrinkToLength(self)
    cdef replaceArray(self, int* newData, Py_ssize_t newLength, Py_ssize_t newCapacity)

    cpdef copy(self)
    cpdef clear(self)
    cpdef fill(self, value)

    cpdef append(self, value)
    cpdef extend(self, values)
    cdef extendList(self, list values)
    cdef extendTuple(self, tuple values)
    cpdef remove(self, value)
    cpdef index(self, value)
    cdef Py_ssize_t searchIndex(self, int value)
    cpdef count(self, value)
    cpdef insert(self, Py_ssize_t index, value)

    cpdef getMemoryView(self)

    cdef IntegerList getValuesInSlice(self, slice sliceObject)
    cdef setValuesInSlice(self, slice sliceObject, values)
    cdef removeValuesInSlice(self, slice sliceObject)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values)
    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values)

    cdef getValueAtIndex(self, Py_ssize_t index)
    cdef setValueAtIndex(self, Py_ssize_t index, int value)
    cdef removeValueAtIndex(self, Py_ssize_t index)

    cpdef IntegerList reversed(self)
    cdef overwrite(self, IntegerList other, Py_ssize_t index = ?)
    cdef overwriteArray(self, int* array, Py_ssize_t arrayLength, Py_ssize_t index)

    # Helpers
    cdef tryConversion(self, value, int* target)
    cdef equals_SameType(self, IntegerList other)
    cdef tryCorrectIndex(self, Py_ssize_t index)


cdef class UIntegerList:
    cdef:
        unsigned int* data
        Py_ssize_t length
        Py_ssize_t capacity

    cdef grow(self, Py_ssize_t minCapacity)
    cdef void shrinkToLength(self)
    cdef replaceArray(self, unsigned int* newData, Py_ssize_t newLength, Py_ssize_t newCapacity)

    cpdef copy(self)
    cpdef clear(self)
    cpdef fill(self, value)

    cpdef append(self, value)
    cpdef extend(self, values)
    cdef extendList(self, list values)
    cdef extendTuple(self, tuple values)
    cpdef remove(self, value)
    cpdef index(self, value)
    cdef Py_ssize_t searchIndex(self, unsigned int value)
    cpdef count(self, value)
    cpdef insert(self, Py_ssize_t index, value)

    cpdef getMemoryView(self)

    cdef UIntegerList getValuesInSlice(self, slice sliceObject)
    cdef setValuesInSlice(self, slice sliceObject, values)
    cdef removeValuesInSlice(self, slice sliceObject)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values)
    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values)

    cdef getValueAtIndex(self, Py_ssize_t index)
    cdef setValueAtIndex(self, Py_ssize_t index, unsigned int value)
    cdef removeValueAtIndex(self, Py_ssize_t index)

    cpdef UIntegerList reversed(self)
    cdef overwrite(self, UIntegerList other, Py_ssize_t index = ?)
    cdef overwriteArray(self, unsigned int* array, Py_ssize_t arrayLength, Py_ssize_t index)

    # Helpers
    cdef tryConversion(self, value, unsigned int* target)
    cdef equals_SameType(self, UIntegerList other)
    cdef tryCorrectIndex(self, Py_ssize_t index)


cdef class ShortList:
    cdef:
        short* data
        Py_ssize_t length
        Py_ssize_t capacity

    cdef grow(self, Py_ssize_t minCapacity)
    cdef void shrinkToLength(self)
    cdef replaceArray(self, short* newData, Py_ssize_t newLength, Py_ssize_t newCapacity)

    cpdef copy(self)
    cpdef clear(self)
    cpdef fill(self, value)

    cpdef append(self, value)
    cpdef extend(self, values)
    cdef extendList(self, list values)
    cdef extendTuple(self, tuple values)
    cpdef remove(self, value)
    cpdef index(self, value)
    cdef Py_ssize_t searchIndex(self, short value)
    cpdef count(self, value)
    cpdef insert(self, Py_ssize_t index, value)

    cpdef getMemoryView(self)

    cdef ShortList getValuesInSlice(self, slice sliceObject)
    cdef setValuesInSlice(self, slice sliceObject, values)
    cdef removeValuesInSlice(self, slice sliceObject)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values)
    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values)

    cdef getValueAtIndex(self, Py_ssize_t index)
    cdef setValueAtIndex(self, Py_ssize_t index, short value)
    cdef removeValueAtIndex(self, Py_ssize_t index)

    cpdef ShortList reversed(self)
    cdef overwrite(self, ShortList other, Py_ssize_t index = ?)
    cdef overwriteArray(self, short* array, Py_ssize_t arrayLength, Py_ssize_t index)

    # Helpers
    cdef tryConversion(self, value, short* target)
    cdef equals_SameType(self, ShortList other)
    cdef tryCorrectIndex(self, Py_ssize_t index)


cdef class UShortList:
    cdef:
        unsigned short* data
        Py_ssize_t length
        Py_ssize_t capacity

    cdef grow(self, Py_ssize_t minCapacity)
    cdef void shrinkToLength(self)
    cdef replaceArray(self, unsigned short* newData, Py_ssize_t newLength, Py_ssize_t newCapacity)

    cpdef copy(self)
    cpdef clear(self)
    cpdef fill(self, value)

    cpdef append(self, value)
    cpdef extend(self, values)
    cdef extendList(self, list values)
    cdef extendTuple(self, tuple values)
    cpdef remove(self, value)
    cpdef index(self, value)
    cdef Py_ssize_t searchIndex(self, unsigned short value)
    cpdef count(self, value)
    cpdef insert(self, Py_ssize_t index, value)

    cpdef getMemoryView(self)

    cdef UShortList getValuesInSlice(self, slice sliceObject)
    cdef setValuesInSlice(self, slice sliceObject, values)
    cdef removeValuesInSlice(self, slice sliceObject)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values)
    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values)

    cdef getValueAtIndex(self, Py_ssize_t index)
    cdef setValueAtIndex(self, Py_ssize_t index, unsigned short value)
    cdef removeValueAtIndex(self, Py_ssize_t index)

    cpdef UShortList reversed(self)
    cdef overwrite(self, UShortList other, Py_ssize_t index = ?)
    cdef overwriteArray(self, unsigned short* array, Py_ssize_t arrayLength, Py_ssize_t index)

    # Helpers
    cdef tryConversion(self, value, unsigned short* target)
    cdef equals_SameType(self, UShortList other)
    cdef tryCorrectIndex(self, Py_ssize_t index)


cdef class LongLongList:
    cdef:
        long long* data
        Py_ssize_t length
        Py_ssize_t capacity

    cdef grow(self, Py_ssize_t minCapacity)
    cdef void shrinkToLength(self)
    cdef replaceArray(self, long long* newData, Py_ssize_t newLength, Py_ssize_t newCapacity)

    cpdef copy(self)
    cpdef clear(self)
    cpdef fill(self, value)

    cpdef append(self, value)
    cpdef extend(self, values)
    cdef extendList(self, list values)
    cdef extendTuple(self, tuple values)
    cpdef remove(self, value)
    cpdef index(self, value)
    cdef Py_ssize_t searchIndex(self, long long value)
    cpdef count(self, value)
    cpdef insert(self, Py_ssize_t index, value)

    cpdef getMemoryView(self)

    cdef LongLongList getValuesInSlice(self, slice sliceObject)
    cdef setValuesInSlice(self, slice sliceObject, values)
    cdef removeValuesInSlice(self, slice sliceObject)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values)
    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values)

    cdef getValueAtIndex(self, Py_ssize_t index)
    cdef setValueAtIndex(self, Py_ssize_t index, long long value)
    cdef removeValueAtIndex(self, Py_ssize_t index)

    cpdef LongLongList reversed(self)
    cdef overwrite(self, LongLongList other, Py_ssize_t index = ?)
    cdef overwriteArray(self, long long* array, Py_ssize_t arrayLength, Py_ssize_t index)

    # Helpers
    cdef tryConversion(self, value, long long* target)
    cdef equals_SameType(self, LongLongList other)
    cdef tryCorrectIndex(self, Py_ssize_t index)


cdef class ULongLongList:
    cdef:
        unsigned long long* data
        Py_ssize_t length
        Py_ssize_t capacity

    cdef grow(self, Py_ssize_t minCapacity)
    cdef void shrinkToLength(self)
    cdef replaceArray(self, unsigned long long* newData, Py_ssize_t newLength, Py_ssize_t newCapacity)

    cpdef copy(self)
    cpdef clear(self)
    cpdef fill(self, value)

    cpdef append(self, value)
    cpdef extend(self, values)
    cdef extendList(self, list values)
    cdef extendTuple(self, tuple values)
    cpdef remove(self, value)
    cpdef index(self, value)
    cdef Py_ssize_t searchIndex(self, unsigned long long value)
    cpdef count(self, value)
    cpdef insert(self, Py_ssize_t index, value)

    cpdef getMemoryView(self)

    cdef ULongLongList getValuesInSlice(self, slice sliceObject)
    cdef setValuesInSlice(self, slice sliceObject, values)
    cdef removeValuesInSlice(self, slice sliceObject)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values)
    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values)

    cdef getValueAtIndex(self, Py_ssize_t index)
    cdef setValueAtIndex(self, Py_ssize_t index, unsigned long long value)
    cdef removeValueAtIndex(self, Py_ssize_t index)

    cpdef ULongLongList reversed(self)
    cdef overwrite(self, ULongLongList other, Py_ssize_t index = ?)
    cdef overwriteArray(self, unsigned long long* array, Py_ssize_t arrayLength, Py_ssize_t index)

    # Helpers
    cdef tryConversion(self, value, unsigned long long* target)
    cdef equals_SameType(self, ULongLongList other)
    cdef tryCorrectIndex(self, Py_ssize_t index)
