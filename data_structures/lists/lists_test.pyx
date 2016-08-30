cimport cython
from types import GeneratorType
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy, memmove, memcmp
from . utils cimport predictSliceLength, makeStepPositive, removeValuesInSlice, getValuesInSlice

@cython.freelist(10)
cdef class FloatList:

    # Initialization and Memory Management
    ###############################################

    def __cinit__(self, Py_ssize_t length = 0, Py_ssize_t capacity = -1):
        '''
        Initialize a new object with the given length.
        You can also directly allocate more memory from the beginning
        to allow faster appending/extending without memory reallocation.
        '''
        if length < 0:
            raise ValueError("Length has to be >= 0")
        if capacity < length:
            capacity = length
        self.data = <float*>malloc(sizeof(float) * capacity)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.capacity = capacity

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef grow(self, Py_ssize_t minCapacity):
        if minCapacity < self.capacity:
            return

        cdef Py_ssize_t newCapacity = minCapacity * 2 + 1
        self.data = <float*>realloc(self.data, sizeof(float) * newCapacity)
        if self.data == NULL:
            self.length = 0
            self.capacity = 0
            raise MemoryError()
        self.capacity = newCapacity

    cdef void shrinkToLength(self):
        cdef Py_ssize_t newCapacity = max(1, self.length)
        self.data = <float*>realloc(self.data, sizeof(float) * newCapacity)
        self.capacity = newCapacity

    cdef replaceArray(self, float* newData, Py_ssize_t newLength, Py_ssize_t newCapacity):
        free(self.data)
        self.data = newData
        self.length = newLength
        self.capacity = newCapacity


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getValueAtIndex(key)
        elif isinstance(key, slice):
            return self.getValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.setValueAtIndex(key, value)
        elif isinstance(key, slice):
            self.setValuesInSlice(key, value)
        else:
            raise TypeError("Expected int or slice object")

    def __delitem__(self, key):
        if isinstance(key, int):
            self.removeValueAtIndex(key)
        elif isinstance(key, slice):
            self.removeValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __add__(a, b):
        cdef FloatList newList
        try:
            newList = FloatList(capacity = len(a) + len(b))
            newList.extend(a)
            newList.extend(b)
        except:
            raise NotImplementedError()
        return newList

    def __mul__(FloatList self, Py_ssize_t amount):
        return self.repeated(amount = amount)

    def __iadd__(FloatList self, other):
        try:
            self.extend(other)
        except:
            raise NotImplementedError()
        return self

    def __iter__(self):
        return FloatListIterator(self)

    def __contains__(self, float value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    def __richcmp__(x, y, int operation):
        if operation == 2: # '=='
            if type(x) == type(y):
                return (<FloatList>x).equals_SameType(y)
            if len(x) == len(y):
                return all(a == b for a, b in zip(x, y))
            return False
        raise NotImplemented()

    cdef equals_SameType(self, FloatList other):
        if self.length != other.length:
            return False
        cdef Py_ssize_t i
        for i in range(self.length):
            if not self.data[i] == other.data[i]: return False
        return True


    # Base operations for lists - mimic python list
    ###############################################

    cpdef copy(self):
        newList = FloatList(self.length)
        newList.overwrite(self)
        return newList

    cpdef clear(self):
        self.length = 0
        self.shrinkToLength()

    cpdef fill(self, value):
        cdef Py_ssize_t i
        cdef float _value
        self.tryConversion(value, &_value)
        for i in range(self.length):
            self.data[i] = _value

    cpdef append(self, value):
        if self.length >= self.capacity:
            self.grow(self.length + 1)
        self.tryConversion(value, self.data + self.length)
        self.length += 1

    cpdef extend(self, values):
        cdef Py_ssize_t oldLength, newLength, i
        if isinstance(values, FloatList):
            self.overwrite(values, self.length)
        elif isinstance(values, list):
            self.extendList(values)
        elif isinstance(values, tuple):
            self.extendTuple(values)
        elif hasattr(values, "__len__"):
            newLength = self.length + len(values)
            self.grow(newLength)
            for i, value in enumerate(values, start = self.length):
                self.tryConversion(value, self.data + i)
            self.length = newLength
        else:
            try:
                oldLength = self.length
                for value in values:
                    self.append(value)
            except:
                self.length = oldLength
                raise TypeError("invalid input")

    cdef extendList(self, list values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cdef extendTuple(self, tuple values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cpdef index(self, value):
        cdef float _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t index = self.searchIndex(_value)
        if index >= 0: return index
        raise ValueError("value not in list")

    cdef Py_ssize_t searchIndex(self, float value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef count(self, value):
        cdef float _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t i
        cdef Py_ssize_t amount = 0
        for i in range(self.length):
            if self.data[i] == _value:
                amount += 1
        return amount

    cpdef remove(self, value):
        cdef Py_ssize_t index = self.searchIndex(value)
        if index == -1:
            raise ValueError("value not in list")
        else:
            self.removeValueAtIndex(index)

    cpdef insert(self, Py_ssize_t index, value):
        cdef float _value
        if index >= self.length:
            self.append(value)
        else:
            self.tryConversion(value, &_value)
            self.grow(self.length + 1)
            if index < 0: index += self.length
            if index < 0: index = 0
            memmove(self.data + index + 1,
                    self.data + index,
                    sizeof(float) * (self.length - index))
            self.data[index] = _value
            self.length += 1



    # Get/Set/Remove single element
    ################################################

    cdef getValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        return self.data[index]

    cdef setValueAtIndex(self, Py_ssize_t index, float value):
        index = self.tryCorrectIndex(index)
        self.data[index] = value

    cdef removeValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        memmove(self.data + index,
                self.data + index + 1,
                (self.length - index) * sizeof(float))
        self.length -= 1


    # Get/Set/Remove elements in slice
    ################################################

    cdef FloatList getValuesInSlice(self, slice sliceObject):
        cdef:
            void* newArray
            Py_ssize_t newLength
            FloatList newList

        getValuesInSlice(self.data, self.length, sizeof(float),
                         &newArray, &newLength, sliceObject)

        newList = FloatList()
        newList.replaceArray(<float*>newArray, newLength, newLength)
        return newList

    cdef setValuesInSlice(self, slice sliceObject, values):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))

        if step == 1:
            self.setValuesInSimpleSlice(start, stop, values)
        else:
            self.setValuesInExtendedSlice(start, stop, step, values)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values):
        cdef:
            Py_ssize_t replacementLength = len(values)
            Py_ssize_t sliceLength = predictSliceLength(start, stop, 1)

        if replacementLength > sliceLength:
            self.grow(self.length + (replacementLength - sliceLength))
        if replacementLength != sliceLength:
            memmove(self.data + start + replacementLength,
                    self.data + stop,
                    sizeof(float) * (self.length - stop))
            self.length += replacementLength - sliceLength

        cdef Py_ssize_t i
        cdef float _value
        if isinstance(values, FloatList):
            self.overwrite(values, start)
        else:
            for i in range(replacementLength):
                self.tryConversion(values[i], self.data + start + i)

    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values):
        cdef Py_ssize_t sliceLength = predictSliceLength(start, stop, step)
        if sliceLength != len(values):
            raise ValueError("attempt to assign sequence of size {} to extended slice of size {}"
                             .format(len(values), sliceLength))

        # TODO: Speedup for specific list types + use while loop
        # range does not efficiently work with a variable step
        cdef Py_ssize_t i
        for i, value in zip(range(start, stop, step), values):
            self.tryConversion(value, self.data + i)

    cdef removeValuesInSlice(self, slice sliceObject):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))
        cdef Py_ssize_t removeAmount = removeValuesInSlice(
                      arrayStart = <char*>self.data,
                      arrayLength = self.length * sizeof(float),
                      elementSize = sizeof(float),
                      start = start, stop = stop, step = step)
        self.length -= removeAmount


    # Create new lists based on an existing list
    ###############################################

    cpdef FloatList reversed(self):
        cdef:
            FloatList newList = FloatList(self.length)
            Py_ssize_t i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def repeated(self, *, Py_ssize_t length = -1, Py_ssize_t amount = -1):
        if length < 0 and amount < 0:
            raise ValueError("Specify the 'length' or 'amount' parameter as keyword")
        elif length > 0 and amount > 0:
            raise ValueError("Can only evaluate one parameter of 'length' and 'amount'")

        if amount >= 0:
            length = self.length * amount

        if self.length == 0 and length > 0:
            raise ValueError("Cannot repeat a list with zero elements to something longer")

        cdef:
            FloatList newList = FloatList(length)
            Py_ssize_t copyAmount = length // self.length
            Py_ssize_t i

        # Full copy as often as possible
        for i in range(copyAmount):
            memcpy(newList.data + i * self.length,
                   self.data,
                   sizeof(float) * self.length)
        # Partial copy at the end
        memcpy(newList.data + self.length * copyAmount,
               self.data,
               sizeof(float) * (length % self.length))
        return newList


    # Low level utilities
    ###############################################

    cdef tryConversion(self, value, float* target):
        target[0] = value

    cdef tryCorrectIndex(self, Py_ssize_t index):
        if index < 0:
            index += self.length
        if index < 0 or index >= self.length:
            raise IndexError("list index out of range")
        return index

    cdef overwrite(self, FloatList other, Py_ssize_t index = 0):
        if self.capacity <= index + other.length:
            self.grow(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(float))
        self.length = max(self.length, index + other.length)

    cdef overwriteArray(self, float* array, Py_ssize_t arrayLength, Py_ssize_t index):
        if self.capacity <= index + arrayLength:
            self.grow(index + arrayLength)
        memcpy(self.data + index, array, arrayLength * sizeof(float))
        self.length = max(self.length, index + arrayLength)


    # Memory Views
    ###############################################

    cpdef getMemoryView(self):
        if "float" == "None":
            raise NotImplementedError("Cannot create memoryview for this type")

        cdef float[:] memview
        if self.length > 0:
            memview = <float[:self.length]>self.data
        else:
            # hack to make zero-length memview possible
            memview = (<float[:1]>self.data)[1:]
        return memview


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def join(cls, *sourceLists):
        cdef Py_ssize_t newLength = 0
        cdef Py_ssize_t offset = 0
        cdef FloatList source

        for source in sourceLists:
            newLength += len(source)
        newList = FloatList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, values):
        if isinstance(values, (list, tuple)):
            return cls.fromListOrTuple(values)

        try:
            from . convert import toFloatList
            return toFloatList(values)
        except TypeError: pass

        cdef FloatList newList = FloatList()
        newList.extend(values)
        return newList

    @classmethod
    def fromListOrTuple(cls, list_or_tuple values):
        cdef FloatList newList = FloatList(len(values))
        cdef Py_ssize_t i
        for i, value in enumerate(values):
            newList.tryConversion(value, newList.data + i)
        return newList


    # String Representations
    ###############################################

    def __repr__(self):
        if self.length < 20:
            return "<FloatList [{}]>".format(", ".join(str(self[i]) for i in range(self.length)))
        else:
            return "<FloatList [{}, ...]>".format(", ".join(str(self[i]) for i in range(20)))

    def status(self):
        return "Length: {}, Capacity: {}, Size: {} bytes".format(
            self.length, self.capacity, self.capacity * sizeof(float))


cdef class FloatListIterator:
    '''
    Implements the 'Iterator Protocol' that is used to allow iteration
    over a custom list object (eg with a for loop).
    An instance of this class is only created in the __iter__ method
    of the corresponding list type.
    https://docs.python.org/3.5/library/stdtypes.html#iterator-types
    '''
    cdef:
        FloatList source
        Py_ssize_t current

    def __cinit__(self, FloatList source):
        self.source = source
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef float currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue


cimport cython
from types import GeneratorType
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy, memmove, memcmp
from . utils cimport predictSliceLength, makeStepPositive, removeValuesInSlice, getValuesInSlice

@cython.freelist(10)
cdef class DoubleList:

    # Initialization and Memory Management
    ###############################################

    def __cinit__(self, Py_ssize_t length = 0, Py_ssize_t capacity = -1):
        '''
        Initialize a new object with the given length.
        You can also directly allocate more memory from the beginning
        to allow faster appending/extending without memory reallocation.
        '''
        if length < 0:
            raise ValueError("Length has to be >= 0")
        if capacity < length:
            capacity = length
        self.data = <double*>malloc(sizeof(double) * capacity)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.capacity = capacity

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef grow(self, Py_ssize_t minCapacity):
        if minCapacity < self.capacity:
            return

        cdef Py_ssize_t newCapacity = minCapacity * 2 + 1
        self.data = <double*>realloc(self.data, sizeof(double) * newCapacity)
        if self.data == NULL:
            self.length = 0
            self.capacity = 0
            raise MemoryError()
        self.capacity = newCapacity

    cdef void shrinkToLength(self):
        cdef Py_ssize_t newCapacity = max(1, self.length)
        self.data = <double*>realloc(self.data, sizeof(double) * newCapacity)
        self.capacity = newCapacity

    cdef replaceArray(self, double* newData, Py_ssize_t newLength, Py_ssize_t newCapacity):
        free(self.data)
        self.data = newData
        self.length = newLength
        self.capacity = newCapacity


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getValueAtIndex(key)
        elif isinstance(key, slice):
            return self.getValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.setValueAtIndex(key, value)
        elif isinstance(key, slice):
            self.setValuesInSlice(key, value)
        else:
            raise TypeError("Expected int or slice object")

    def __delitem__(self, key):
        if isinstance(key, int):
            self.removeValueAtIndex(key)
        elif isinstance(key, slice):
            self.removeValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __add__(a, b):
        cdef DoubleList newList
        try:
            newList = DoubleList(capacity = len(a) + len(b))
            newList.extend(a)
            newList.extend(b)
        except:
            raise NotImplementedError()
        return newList

    def __mul__(DoubleList self, Py_ssize_t amount):
        return self.repeated(amount = amount)

    def __iadd__(DoubleList self, other):
        try:
            self.extend(other)
        except:
            raise NotImplementedError()
        return self

    def __iter__(self):
        return DoubleListIterator(self)

    def __contains__(self, double value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    def __richcmp__(x, y, int operation):
        if operation == 2: # '=='
            if type(x) == type(y):
                return (<DoubleList>x).equals_SameType(y)
            if len(x) == len(y):
                return all(a == b for a, b in zip(x, y))
            return False
        raise NotImplemented()

    cdef equals_SameType(self, DoubleList other):
        if self.length != other.length:
            return False
        cdef Py_ssize_t i
        for i in range(self.length):
            if not self.data[i] == other.data[i]: return False
        return True


    # Base operations for lists - mimic python list
    ###############################################

    cpdef copy(self):
        newList = DoubleList(self.length)
        newList.overwrite(self)
        return newList

    cpdef clear(self):
        self.length = 0
        self.shrinkToLength()

    cpdef fill(self, value):
        cdef Py_ssize_t i
        cdef double _value
        self.tryConversion(value, &_value)
        for i in range(self.length):
            self.data[i] = _value

    cpdef append(self, value):
        if self.length >= self.capacity:
            self.grow(self.length + 1)
        self.tryConversion(value, self.data + self.length)
        self.length += 1

    cpdef extend(self, values):
        cdef Py_ssize_t oldLength, newLength, i
        if isinstance(values, DoubleList):
            self.overwrite(values, self.length)
        elif isinstance(values, list):
            self.extendList(values)
        elif isinstance(values, tuple):
            self.extendTuple(values)
        elif hasattr(values, "__len__"):
            newLength = self.length + len(values)
            self.grow(newLength)
            for i, value in enumerate(values, start = self.length):
                self.tryConversion(value, self.data + i)
            self.length = newLength
        else:
            try:
                oldLength = self.length
                for value in values:
                    self.append(value)
            except:
                self.length = oldLength
                raise TypeError("invalid input")

    cdef extendList(self, list values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cdef extendTuple(self, tuple values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cpdef index(self, value):
        cdef double _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t index = self.searchIndex(_value)
        if index >= 0: return index
        raise ValueError("value not in list")

    cdef Py_ssize_t searchIndex(self, double value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef count(self, value):
        cdef double _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t i
        cdef Py_ssize_t amount = 0
        for i in range(self.length):
            if self.data[i] == _value:
                amount += 1
        return amount

    cpdef remove(self, value):
        cdef Py_ssize_t index = self.searchIndex(value)
        if index == -1:
            raise ValueError("value not in list")
        else:
            self.removeValueAtIndex(index)

    cpdef insert(self, Py_ssize_t index, value):
        cdef double _value
        if index >= self.length:
            self.append(value)
        else:
            self.tryConversion(value, &_value)
            self.grow(self.length + 1)
            if index < 0: index += self.length
            if index < 0: index = 0
            memmove(self.data + index + 1,
                    self.data + index,
                    sizeof(double) * (self.length - index))
            self.data[index] = _value
            self.length += 1



    # Get/Set/Remove single element
    ################################################

    cdef getValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        return self.data[index]

    cdef setValueAtIndex(self, Py_ssize_t index, double value):
        index = self.tryCorrectIndex(index)
        self.data[index] = value

    cdef removeValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        memmove(self.data + index,
                self.data + index + 1,
                (self.length - index) * sizeof(double))
        self.length -= 1


    # Get/Set/Remove elements in slice
    ################################################

    cdef DoubleList getValuesInSlice(self, slice sliceObject):
        cdef:
            void* newArray
            Py_ssize_t newLength
            DoubleList newList

        getValuesInSlice(self.data, self.length, sizeof(double),
                         &newArray, &newLength, sliceObject)

        newList = DoubleList()
        newList.replaceArray(<double*>newArray, newLength, newLength)
        return newList

    cdef setValuesInSlice(self, slice sliceObject, values):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))

        if step == 1:
            self.setValuesInSimpleSlice(start, stop, values)
        else:
            self.setValuesInExtendedSlice(start, stop, step, values)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values):
        cdef:
            Py_ssize_t replacementLength = len(values)
            Py_ssize_t sliceLength = predictSliceLength(start, stop, 1)

        if replacementLength > sliceLength:
            self.grow(self.length + (replacementLength - sliceLength))
        if replacementLength != sliceLength:
            memmove(self.data + start + replacementLength,
                    self.data + stop,
                    sizeof(double) * (self.length - stop))
            self.length += replacementLength - sliceLength

        cdef Py_ssize_t i
        cdef double _value
        if isinstance(values, DoubleList):
            self.overwrite(values, start)
        else:
            for i in range(replacementLength):
                self.tryConversion(values[i], self.data + start + i)

    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values):
        cdef Py_ssize_t sliceLength = predictSliceLength(start, stop, step)
        if sliceLength != len(values):
            raise ValueError("attempt to assign sequence of size {} to extended slice of size {}"
                             .format(len(values), sliceLength))

        # TODO: Speedup for specific list types + use while loop
        # range does not efficiently work with a variable step
        cdef Py_ssize_t i
        for i, value in zip(range(start, stop, step), values):
            self.tryConversion(value, self.data + i)

    cdef removeValuesInSlice(self, slice sliceObject):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))
        cdef Py_ssize_t removeAmount = removeValuesInSlice(
                      arrayStart = <char*>self.data,
                      arrayLength = self.length * sizeof(double),
                      elementSize = sizeof(double),
                      start = start, stop = stop, step = step)
        self.length -= removeAmount


    # Create new lists based on an existing list
    ###############################################

    cpdef DoubleList reversed(self):
        cdef:
            DoubleList newList = DoubleList(self.length)
            Py_ssize_t i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def repeated(self, *, Py_ssize_t length = -1, Py_ssize_t amount = -1):
        if length < 0 and amount < 0:
            raise ValueError("Specify the 'length' or 'amount' parameter as keyword")
        elif length > 0 and amount > 0:
            raise ValueError("Can only evaluate one parameter of 'length' and 'amount'")

        if amount >= 0:
            length = self.length * amount

        if self.length == 0 and length > 0:
            raise ValueError("Cannot repeat a list with zero elements to something longer")

        cdef:
            DoubleList newList = DoubleList(length)
            Py_ssize_t copyAmount = length // self.length
            Py_ssize_t i

        # Full copy as often as possible
        for i in range(copyAmount):
            memcpy(newList.data + i * self.length,
                   self.data,
                   sizeof(double) * self.length)
        # Partial copy at the end
        memcpy(newList.data + self.length * copyAmount,
               self.data,
               sizeof(double) * (length % self.length))
        return newList


    # Low level utilities
    ###############################################

    cdef tryConversion(self, value, double* target):
        target[0] = value

    cdef tryCorrectIndex(self, Py_ssize_t index):
        if index < 0:
            index += self.length
        if index < 0 or index >= self.length:
            raise IndexError("list index out of range")
        return index

    cdef overwrite(self, DoubleList other, Py_ssize_t index = 0):
        if self.capacity <= index + other.length:
            self.grow(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(double))
        self.length = max(self.length, index + other.length)

    cdef overwriteArray(self, double* array, Py_ssize_t arrayLength, Py_ssize_t index):
        if self.capacity <= index + arrayLength:
            self.grow(index + arrayLength)
        memcpy(self.data + index, array, arrayLength * sizeof(double))
        self.length = max(self.length, index + arrayLength)


    # Memory Views
    ###############################################

    cpdef getMemoryView(self):
        if "double" == "None":
            raise NotImplementedError("Cannot create memoryview for this type")

        cdef double[:] memview
        if self.length > 0:
            memview = <double[:self.length]>self.data
        else:
            # hack to make zero-length memview possible
            memview = (<double[:1]>self.data)[1:]
        return memview


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def join(cls, *sourceLists):
        cdef Py_ssize_t newLength = 0
        cdef Py_ssize_t offset = 0
        cdef DoubleList source

        for source in sourceLists:
            newLength += len(source)
        newList = DoubleList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, values):
        if isinstance(values, (list, tuple)):
            return cls.fromListOrTuple(values)

        try:
            from . convert import toDoubleList
            return toDoubleList(values)
        except TypeError: pass

        cdef DoubleList newList = DoubleList()
        newList.extend(values)
        return newList

    @classmethod
    def fromListOrTuple(cls, list_or_tuple values):
        cdef DoubleList newList = DoubleList(len(values))
        cdef Py_ssize_t i
        for i, value in enumerate(values):
            newList.tryConversion(value, newList.data + i)
        return newList


    # String Representations
    ###############################################

    def __repr__(self):
        if self.length < 20:
            return "<DoubleList [{}]>".format(", ".join(str(self[i]) for i in range(self.length)))
        else:
            return "<DoubleList [{}, ...]>".format(", ".join(str(self[i]) for i in range(20)))

    def status(self):
        return "Length: {}, Capacity: {}, Size: {} bytes".format(
            self.length, self.capacity, self.capacity * sizeof(double))


cdef class DoubleListIterator:
    '''
    Implements the 'Iterator Protocol' that is used to allow iteration
    over a custom list object (eg with a for loop).
    An instance of this class is only created in the __iter__ method
    of the corresponding list type.
    https://docs.python.org/3.5/library/stdtypes.html#iterator-types
    '''
    cdef:
        DoubleList source
        Py_ssize_t current

    def __cinit__(self, DoubleList source):
        self.source = source
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef double currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue


cimport cython
from types import GeneratorType
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy, memmove, memcmp
from . utils cimport predictSliceLength, makeStepPositive, removeValuesInSlice, getValuesInSlice

@cython.freelist(10)
cdef class CharList:

    # Initialization and Memory Management
    ###############################################

    def __cinit__(self, Py_ssize_t length = 0, Py_ssize_t capacity = -1):
        '''
        Initialize a new object with the given length.
        You can also directly allocate more memory from the beginning
        to allow faster appending/extending without memory reallocation.
        '''
        if length < 0:
            raise ValueError("Length has to be >= 0")
        if capacity < length:
            capacity = length
        self.data = <char*>malloc(sizeof(char) * capacity)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.capacity = capacity

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef grow(self, Py_ssize_t minCapacity):
        if minCapacity < self.capacity:
            return

        cdef Py_ssize_t newCapacity = minCapacity * 2 + 1
        self.data = <char*>realloc(self.data, sizeof(char) * newCapacity)
        if self.data == NULL:
            self.length = 0
            self.capacity = 0
            raise MemoryError()
        self.capacity = newCapacity

    cdef void shrinkToLength(self):
        cdef Py_ssize_t newCapacity = max(1, self.length)
        self.data = <char*>realloc(self.data, sizeof(char) * newCapacity)
        self.capacity = newCapacity

    cdef replaceArray(self, char* newData, Py_ssize_t newLength, Py_ssize_t newCapacity):
        free(self.data)
        self.data = newData
        self.length = newLength
        self.capacity = newCapacity


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getValueAtIndex(key)
        elif isinstance(key, slice):
            return self.getValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.setValueAtIndex(key, value)
        elif isinstance(key, slice):
            self.setValuesInSlice(key, value)
        else:
            raise TypeError("Expected int or slice object")

    def __delitem__(self, key):
        if isinstance(key, int):
            self.removeValueAtIndex(key)
        elif isinstance(key, slice):
            self.removeValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __add__(a, b):
        cdef CharList newList
        try:
            newList = CharList(capacity = len(a) + len(b))
            newList.extend(a)
            newList.extend(b)
        except:
            raise NotImplementedError()
        return newList

    def __mul__(CharList self, Py_ssize_t amount):
        return self.repeated(amount = amount)

    def __iadd__(CharList self, other):
        try:
            self.extend(other)
        except:
            raise NotImplementedError()
        return self

    def __iter__(self):
        return CharListIterator(self)

    def __contains__(self, char value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    def __richcmp__(x, y, int operation):
        if operation == 2: # '=='
            if type(x) == type(y):
                return (<CharList>x).equals_SameType(y)
            if len(x) == len(y):
                return all(a == b for a, b in zip(x, y))
            return False
        raise NotImplemented()

    cdef equals_SameType(self, CharList other):
        if self.length != other.length:
            return False
        cdef Py_ssize_t i
        for i in range(self.length):
            if not self.data[i] == other.data[i]: return False
        return True


    # Base operations for lists - mimic python list
    ###############################################

    cpdef copy(self):
        newList = CharList(self.length)
        newList.overwrite(self)
        return newList

    cpdef clear(self):
        self.length = 0
        self.shrinkToLength()

    cpdef fill(self, value):
        cdef Py_ssize_t i
        cdef char _value
        self.tryConversion(value, &_value)
        for i in range(self.length):
            self.data[i] = _value

    cpdef append(self, value):
        if self.length >= self.capacity:
            self.grow(self.length + 1)
        self.tryConversion(value, self.data + self.length)
        self.length += 1

    cpdef extend(self, values):
        cdef Py_ssize_t oldLength, newLength, i
        if isinstance(values, CharList):
            self.overwrite(values, self.length)
        elif isinstance(values, list):
            self.extendList(values)
        elif isinstance(values, tuple):
            self.extendTuple(values)
        elif hasattr(values, "__len__"):
            newLength = self.length + len(values)
            self.grow(newLength)
            for i, value in enumerate(values, start = self.length):
                self.tryConversion(value, self.data + i)
            self.length = newLength
        else:
            try:
                oldLength = self.length
                for value in values:
                    self.append(value)
            except:
                self.length = oldLength
                raise TypeError("invalid input")

    cdef extendList(self, list values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cdef extendTuple(self, tuple values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cpdef index(self, value):
        cdef char _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t index = self.searchIndex(_value)
        if index >= 0: return index
        raise ValueError("value not in list")

    cdef Py_ssize_t searchIndex(self, char value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef count(self, value):
        cdef char _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t i
        cdef Py_ssize_t amount = 0
        for i in range(self.length):
            if self.data[i] == _value:
                amount += 1
        return amount

    cpdef remove(self, value):
        cdef Py_ssize_t index = self.searchIndex(value)
        if index == -1:
            raise ValueError("value not in list")
        else:
            self.removeValueAtIndex(index)

    cpdef insert(self, Py_ssize_t index, value):
        cdef char _value
        if index >= self.length:
            self.append(value)
        else:
            self.tryConversion(value, &_value)
            self.grow(self.length + 1)
            if index < 0: index += self.length
            if index < 0: index = 0
            memmove(self.data + index + 1,
                    self.data + index,
                    sizeof(char) * (self.length - index))
            self.data[index] = _value
            self.length += 1



    # Get/Set/Remove single element
    ################################################

    cdef getValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        return self.data[index]

    cdef setValueAtIndex(self, Py_ssize_t index, char value):
        index = self.tryCorrectIndex(index)
        self.data[index] = value

    cdef removeValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        memmove(self.data + index,
                self.data + index + 1,
                (self.length - index) * sizeof(char))
        self.length -= 1


    # Get/Set/Remove elements in slice
    ################################################

    cdef CharList getValuesInSlice(self, slice sliceObject):
        cdef:
            void* newArray
            Py_ssize_t newLength
            CharList newList

        getValuesInSlice(self.data, self.length, sizeof(char),
                         &newArray, &newLength, sliceObject)

        newList = CharList()
        newList.replaceArray(<char*>newArray, newLength, newLength)
        return newList

    cdef setValuesInSlice(self, slice sliceObject, values):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))

        if step == 1:
            self.setValuesInSimpleSlice(start, stop, values)
        else:
            self.setValuesInExtendedSlice(start, stop, step, values)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values):
        cdef:
            Py_ssize_t replacementLength = len(values)
            Py_ssize_t sliceLength = predictSliceLength(start, stop, 1)

        if replacementLength > sliceLength:
            self.grow(self.length + (replacementLength - sliceLength))
        if replacementLength != sliceLength:
            memmove(self.data + start + replacementLength,
                    self.data + stop,
                    sizeof(char) * (self.length - stop))
            self.length += replacementLength - sliceLength

        cdef Py_ssize_t i
        cdef char _value
        if isinstance(values, CharList):
            self.overwrite(values, start)
        else:
            for i in range(replacementLength):
                self.tryConversion(values[i], self.data + start + i)

    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values):
        cdef Py_ssize_t sliceLength = predictSliceLength(start, stop, step)
        if sliceLength != len(values):
            raise ValueError("attempt to assign sequence of size {} to extended slice of size {}"
                             .format(len(values), sliceLength))

        # TODO: Speedup for specific list types + use while loop
        # range does not efficiently work with a variable step
        cdef Py_ssize_t i
        for i, value in zip(range(start, stop, step), values):
            self.tryConversion(value, self.data + i)

    cdef removeValuesInSlice(self, slice sliceObject):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))
        cdef Py_ssize_t removeAmount = removeValuesInSlice(
                      arrayStart = <char*>self.data,
                      arrayLength = self.length * sizeof(char),
                      elementSize = sizeof(char),
                      start = start, stop = stop, step = step)
        self.length -= removeAmount


    # Create new lists based on an existing list
    ###############################################

    cpdef CharList reversed(self):
        cdef:
            CharList newList = CharList(self.length)
            Py_ssize_t i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def repeated(self, *, Py_ssize_t length = -1, Py_ssize_t amount = -1):
        if length < 0 and amount < 0:
            raise ValueError("Specify the 'length' or 'amount' parameter as keyword")
        elif length > 0 and amount > 0:
            raise ValueError("Can only evaluate one parameter of 'length' and 'amount'")

        if amount >= 0:
            length = self.length * amount

        if self.length == 0 and length > 0:
            raise ValueError("Cannot repeat a list with zero elements to something longer")

        cdef:
            CharList newList = CharList(length)
            Py_ssize_t copyAmount = length // self.length
            Py_ssize_t i

        # Full copy as often as possible
        for i in range(copyAmount):
            memcpy(newList.data + i * self.length,
                   self.data,
                   sizeof(char) * self.length)
        # Partial copy at the end
        memcpy(newList.data + self.length * copyAmount,
               self.data,
               sizeof(char) * (length % self.length))
        return newList


    # Low level utilities
    ###############################################

    cdef tryConversion(self, value, char* target):
        target[0] = value

    cdef tryCorrectIndex(self, Py_ssize_t index):
        if index < 0:
            index += self.length
        if index < 0 or index >= self.length:
            raise IndexError("list index out of range")
        return index

    cdef overwrite(self, CharList other, Py_ssize_t index = 0):
        if self.capacity <= index + other.length:
            self.grow(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(char))
        self.length = max(self.length, index + other.length)

    cdef overwriteArray(self, char* array, Py_ssize_t arrayLength, Py_ssize_t index):
        if self.capacity <= index + arrayLength:
            self.grow(index + arrayLength)
        memcpy(self.data + index, array, arrayLength * sizeof(char))
        self.length = max(self.length, index + arrayLength)


    # Memory Views
    ###############################################

    cpdef getMemoryView(self):
        if "char" == "None":
            raise NotImplementedError("Cannot create memoryview for this type")

        cdef char[:] memview
        if self.length > 0:
            memview = <char[:self.length]>self.data
        else:
            # hack to make zero-length memview possible
            memview = (<char[:1]>self.data)[1:]
        return memview


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def join(cls, *sourceLists):
        cdef Py_ssize_t newLength = 0
        cdef Py_ssize_t offset = 0
        cdef CharList source

        for source in sourceLists:
            newLength += len(source)
        newList = CharList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, values):
        if isinstance(values, (list, tuple)):
            return cls.fromListOrTuple(values)

        try:
            from . convert import toCharList
            return toCharList(values)
        except TypeError: pass

        cdef CharList newList = CharList()
        newList.extend(values)
        return newList

    @classmethod
    def fromListOrTuple(cls, list_or_tuple values):
        cdef CharList newList = CharList(len(values))
        cdef Py_ssize_t i
        for i, value in enumerate(values):
            newList.tryConversion(value, newList.data + i)
        return newList


    # String Representations
    ###############################################

    def __repr__(self):
        if self.length < 20:
            return "<CharList [{}]>".format(", ".join(str(self[i]) for i in range(self.length)))
        else:
            return "<CharList [{}, ...]>".format(", ".join(str(self[i]) for i in range(20)))

    def status(self):
        return "Length: {}, Capacity: {}, Size: {} bytes".format(
            self.length, self.capacity, self.capacity * sizeof(char))


cdef class CharListIterator:
    '''
    Implements the 'Iterator Protocol' that is used to allow iteration
    over a custom list object (eg with a for loop).
    An instance of this class is only created in the __iter__ method
    of the corresponding list type.
    https://docs.python.org/3.5/library/stdtypes.html#iterator-types
    '''
    cdef:
        CharList source
        Py_ssize_t current

    def __cinit__(self, CharList source):
        self.source = source
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef char currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue


cimport cython
from types import GeneratorType
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy, memmove, memcmp
from . utils cimport predictSliceLength, makeStepPositive, removeValuesInSlice, getValuesInSlice

@cython.freelist(10)
cdef class UCharList:

    # Initialization and Memory Management
    ###############################################

    def __cinit__(self, Py_ssize_t length = 0, Py_ssize_t capacity = -1):
        '''
        Initialize a new object with the given length.
        You can also directly allocate more memory from the beginning
        to allow faster appending/extending without memory reallocation.
        '''
        if length < 0:
            raise ValueError("Length has to be >= 0")
        if capacity < length:
            capacity = length
        self.data = <unsigned char*>malloc(sizeof(unsigned char) * capacity)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.capacity = capacity

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef grow(self, Py_ssize_t minCapacity):
        if minCapacity < self.capacity:
            return

        cdef Py_ssize_t newCapacity = minCapacity * 2 + 1
        self.data = <unsigned char*>realloc(self.data, sizeof(unsigned char) * newCapacity)
        if self.data == NULL:
            self.length = 0
            self.capacity = 0
            raise MemoryError()
        self.capacity = newCapacity

    cdef void shrinkToLength(self):
        cdef Py_ssize_t newCapacity = max(1, self.length)
        self.data = <unsigned char*>realloc(self.data, sizeof(unsigned char) * newCapacity)
        self.capacity = newCapacity

    cdef replaceArray(self, unsigned char* newData, Py_ssize_t newLength, Py_ssize_t newCapacity):
        free(self.data)
        self.data = newData
        self.length = newLength
        self.capacity = newCapacity


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getValueAtIndex(key)
        elif isinstance(key, slice):
            return self.getValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.setValueAtIndex(key, value)
        elif isinstance(key, slice):
            self.setValuesInSlice(key, value)
        else:
            raise TypeError("Expected int or slice object")

    def __delitem__(self, key):
        if isinstance(key, int):
            self.removeValueAtIndex(key)
        elif isinstance(key, slice):
            self.removeValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __add__(a, b):
        cdef UCharList newList
        try:
            newList = UCharList(capacity = len(a) + len(b))
            newList.extend(a)
            newList.extend(b)
        except:
            raise NotImplementedError()
        return newList

    def __mul__(UCharList self, Py_ssize_t amount):
        return self.repeated(amount = amount)

    def __iadd__(UCharList self, other):
        try:
            self.extend(other)
        except:
            raise NotImplementedError()
        return self

    def __iter__(self):
        return UCharListIterator(self)

    def __contains__(self, unsigned char value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    def __richcmp__(x, y, int operation):
        if operation == 2: # '=='
            if type(x) == type(y):
                return (<UCharList>x).equals_SameType(y)
            if len(x) == len(y):
                return all(a == b for a, b in zip(x, y))
            return False
        raise NotImplemented()

    cdef equals_SameType(self, UCharList other):
        if self.length != other.length:
            return False
        cdef Py_ssize_t i
        for i in range(self.length):
            if not self.data[i] == other.data[i]: return False
        return True


    # Base operations for lists - mimic python list
    ###############################################

    cpdef copy(self):
        newList = UCharList(self.length)
        newList.overwrite(self)
        return newList

    cpdef clear(self):
        self.length = 0
        self.shrinkToLength()

    cpdef fill(self, value):
        cdef Py_ssize_t i
        cdef unsigned char _value
        self.tryConversion(value, &_value)
        for i in range(self.length):
            self.data[i] = _value

    cpdef append(self, value):
        if self.length >= self.capacity:
            self.grow(self.length + 1)
        self.tryConversion(value, self.data + self.length)
        self.length += 1

    cpdef extend(self, values):
        cdef Py_ssize_t oldLength, newLength, i
        if isinstance(values, UCharList):
            self.overwrite(values, self.length)
        elif isinstance(values, list):
            self.extendList(values)
        elif isinstance(values, tuple):
            self.extendTuple(values)
        elif hasattr(values, "__len__"):
            newLength = self.length + len(values)
            self.grow(newLength)
            for i, value in enumerate(values, start = self.length):
                self.tryConversion(value, self.data + i)
            self.length = newLength
        else:
            try:
                oldLength = self.length
                for value in values:
                    self.append(value)
            except:
                self.length = oldLength
                raise TypeError("invalid input")

    cdef extendList(self, list values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cdef extendTuple(self, tuple values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cpdef index(self, value):
        cdef unsigned char _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t index = self.searchIndex(_value)
        if index >= 0: return index
        raise ValueError("value not in list")

    cdef Py_ssize_t searchIndex(self, unsigned char value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef count(self, value):
        cdef unsigned char _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t i
        cdef Py_ssize_t amount = 0
        for i in range(self.length):
            if self.data[i] == _value:
                amount += 1
        return amount

    cpdef remove(self, value):
        cdef Py_ssize_t index = self.searchIndex(value)
        if index == -1:
            raise ValueError("value not in list")
        else:
            self.removeValueAtIndex(index)

    cpdef insert(self, Py_ssize_t index, value):
        cdef unsigned char _value
        if index >= self.length:
            self.append(value)
        else:
            self.tryConversion(value, &_value)
            self.grow(self.length + 1)
            if index < 0: index += self.length
            if index < 0: index = 0
            memmove(self.data + index + 1,
                    self.data + index,
                    sizeof(unsigned char) * (self.length - index))
            self.data[index] = _value
            self.length += 1



    # Get/Set/Remove single element
    ################################################

    cdef getValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        return self.data[index]

    cdef setValueAtIndex(self, Py_ssize_t index, unsigned char value):
        index = self.tryCorrectIndex(index)
        self.data[index] = value

    cdef removeValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        memmove(self.data + index,
                self.data + index + 1,
                (self.length - index) * sizeof(unsigned char))
        self.length -= 1


    # Get/Set/Remove elements in slice
    ################################################

    cdef UCharList getValuesInSlice(self, slice sliceObject):
        cdef:
            void* newArray
            Py_ssize_t newLength
            UCharList newList

        getValuesInSlice(self.data, self.length, sizeof(unsigned char),
                         &newArray, &newLength, sliceObject)

        newList = UCharList()
        newList.replaceArray(<unsigned char*>newArray, newLength, newLength)
        return newList

    cdef setValuesInSlice(self, slice sliceObject, values):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))

        if step == 1:
            self.setValuesInSimpleSlice(start, stop, values)
        else:
            self.setValuesInExtendedSlice(start, stop, step, values)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values):
        cdef:
            Py_ssize_t replacementLength = len(values)
            Py_ssize_t sliceLength = predictSliceLength(start, stop, 1)

        if replacementLength > sliceLength:
            self.grow(self.length + (replacementLength - sliceLength))
        if replacementLength != sliceLength:
            memmove(self.data + start + replacementLength,
                    self.data + stop,
                    sizeof(unsigned char) * (self.length - stop))
            self.length += replacementLength - sliceLength

        cdef Py_ssize_t i
        cdef unsigned char _value
        if isinstance(values, UCharList):
            self.overwrite(values, start)
        else:
            for i in range(replacementLength):
                self.tryConversion(values[i], self.data + start + i)

    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values):
        cdef Py_ssize_t sliceLength = predictSliceLength(start, stop, step)
        if sliceLength != len(values):
            raise ValueError("attempt to assign sequence of size {} to extended slice of size {}"
                             .format(len(values), sliceLength))

        # TODO: Speedup for specific list types + use while loop
        # range does not efficiently work with a variable step
        cdef Py_ssize_t i
        for i, value in zip(range(start, stop, step), values):
            self.tryConversion(value, self.data + i)

    cdef removeValuesInSlice(self, slice sliceObject):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))
        cdef Py_ssize_t removeAmount = removeValuesInSlice(
                      arrayStart = <char*>self.data,
                      arrayLength = self.length * sizeof(unsigned char),
                      elementSize = sizeof(unsigned char),
                      start = start, stop = stop, step = step)
        self.length -= removeAmount


    # Create new lists based on an existing list
    ###############################################

    cpdef UCharList reversed(self):
        cdef:
            UCharList newList = UCharList(self.length)
            Py_ssize_t i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def repeated(self, *, Py_ssize_t length = -1, Py_ssize_t amount = -1):
        if length < 0 and amount < 0:
            raise ValueError("Specify the 'length' or 'amount' parameter as keyword")
        elif length > 0 and amount > 0:
            raise ValueError("Can only evaluate one parameter of 'length' and 'amount'")

        if amount >= 0:
            length = self.length * amount

        if self.length == 0 and length > 0:
            raise ValueError("Cannot repeat a list with zero elements to something longer")

        cdef:
            UCharList newList = UCharList(length)
            Py_ssize_t copyAmount = length // self.length
            Py_ssize_t i

        # Full copy as often as possible
        for i in range(copyAmount):
            memcpy(newList.data + i * self.length,
                   self.data,
                   sizeof(unsigned char) * self.length)
        # Partial copy at the end
        memcpy(newList.data + self.length * copyAmount,
               self.data,
               sizeof(unsigned char) * (length % self.length))
        return newList


    # Low level utilities
    ###############################################

    cdef tryConversion(self, value, unsigned char* target):
        target[0] = value

    cdef tryCorrectIndex(self, Py_ssize_t index):
        if index < 0:
            index += self.length
        if index < 0 or index >= self.length:
            raise IndexError("list index out of range")
        return index

    cdef overwrite(self, UCharList other, Py_ssize_t index = 0):
        if self.capacity <= index + other.length:
            self.grow(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(unsigned char))
        self.length = max(self.length, index + other.length)

    cdef overwriteArray(self, unsigned char* array, Py_ssize_t arrayLength, Py_ssize_t index):
        if self.capacity <= index + arrayLength:
            self.grow(index + arrayLength)
        memcpy(self.data + index, array, arrayLength * sizeof(unsigned char))
        self.length = max(self.length, index + arrayLength)


    # Memory Views
    ###############################################

    cpdef getMemoryView(self):
        if "unsigned char" == "None":
            raise NotImplementedError("Cannot create memoryview for this type")

        cdef unsigned char[:] memview
        if self.length > 0:
            memview = <unsigned char[:self.length]>self.data
        else:
            # hack to make zero-length memview possible
            memview = (<unsigned char[:1]>self.data)[1:]
        return memview


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def join(cls, *sourceLists):
        cdef Py_ssize_t newLength = 0
        cdef Py_ssize_t offset = 0
        cdef UCharList source

        for source in sourceLists:
            newLength += len(source)
        newList = UCharList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, values):
        if isinstance(values, (list, tuple)):
            return cls.fromListOrTuple(values)

        try:
            from . convert import toUCharList
            return toUCharList(values)
        except TypeError: pass

        cdef UCharList newList = UCharList()
        newList.extend(values)
        return newList

    @classmethod
    def fromListOrTuple(cls, list_or_tuple values):
        cdef UCharList newList = UCharList(len(values))
        cdef Py_ssize_t i
        for i, value in enumerate(values):
            newList.tryConversion(value, newList.data + i)
        return newList


    # String Representations
    ###############################################

    def __repr__(self):
        if self.length < 20:
            return "<UCharList [{}]>".format(", ".join(str(self[i]) for i in range(self.length)))
        else:
            return "<UCharList [{}, ...]>".format(", ".join(str(self[i]) for i in range(20)))

    def status(self):
        return "Length: {}, Capacity: {}, Size: {} bytes".format(
            self.length, self.capacity, self.capacity * sizeof(unsigned char))


cdef class UCharListIterator:
    '''
    Implements the 'Iterator Protocol' that is used to allow iteration
    over a custom list object (eg with a for loop).
    An instance of this class is only created in the __iter__ method
    of the corresponding list type.
    https://docs.python.org/3.5/library/stdtypes.html#iterator-types
    '''
    cdef:
        UCharList source
        Py_ssize_t current

    def __cinit__(self, UCharList source):
        self.source = source
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef unsigned char currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue


cimport cython
from types import GeneratorType
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy, memmove, memcmp
from . utils cimport predictSliceLength, makeStepPositive, removeValuesInSlice, getValuesInSlice

@cython.freelist(10)
cdef class LongList:

    # Initialization and Memory Management
    ###############################################

    def __cinit__(self, Py_ssize_t length = 0, Py_ssize_t capacity = -1):
        '''
        Initialize a new object with the given length.
        You can also directly allocate more memory from the beginning
        to allow faster appending/extending without memory reallocation.
        '''
        if length < 0:
            raise ValueError("Length has to be >= 0")
        if capacity < length:
            capacity = length
        self.data = <long*>malloc(sizeof(long) * capacity)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.capacity = capacity

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef grow(self, Py_ssize_t minCapacity):
        if minCapacity < self.capacity:
            return

        cdef Py_ssize_t newCapacity = minCapacity * 2 + 1
        self.data = <long*>realloc(self.data, sizeof(long) * newCapacity)
        if self.data == NULL:
            self.length = 0
            self.capacity = 0
            raise MemoryError()
        self.capacity = newCapacity

    cdef void shrinkToLength(self):
        cdef Py_ssize_t newCapacity = max(1, self.length)
        self.data = <long*>realloc(self.data, sizeof(long) * newCapacity)
        self.capacity = newCapacity

    cdef replaceArray(self, long* newData, Py_ssize_t newLength, Py_ssize_t newCapacity):
        free(self.data)
        self.data = newData
        self.length = newLength
        self.capacity = newCapacity


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getValueAtIndex(key)
        elif isinstance(key, slice):
            return self.getValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.setValueAtIndex(key, value)
        elif isinstance(key, slice):
            self.setValuesInSlice(key, value)
        else:
            raise TypeError("Expected int or slice object")

    def __delitem__(self, key):
        if isinstance(key, int):
            self.removeValueAtIndex(key)
        elif isinstance(key, slice):
            self.removeValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __add__(a, b):
        cdef LongList newList
        try:
            newList = LongList(capacity = len(a) + len(b))
            newList.extend(a)
            newList.extend(b)
        except:
            raise NotImplementedError()
        return newList

    def __mul__(LongList self, Py_ssize_t amount):
        return self.repeated(amount = amount)

    def __iadd__(LongList self, other):
        try:
            self.extend(other)
        except:
            raise NotImplementedError()
        return self

    def __iter__(self):
        return LongListIterator(self)

    def __contains__(self, long value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    def __richcmp__(x, y, int operation):
        if operation == 2: # '=='
            if type(x) == type(y):
                return (<LongList>x).equals_SameType(y)
            if len(x) == len(y):
                return all(a == b for a, b in zip(x, y))
            return False
        raise NotImplemented()

    cdef equals_SameType(self, LongList other):
        if self.length != other.length:
            return False
        cdef Py_ssize_t i
        for i in range(self.length):
            if not self.data[i] == other.data[i]: return False
        return True


    # Base operations for lists - mimic python list
    ###############################################

    cpdef copy(self):
        newList = LongList(self.length)
        newList.overwrite(self)
        return newList

    cpdef clear(self):
        self.length = 0
        self.shrinkToLength()

    cpdef fill(self, value):
        cdef Py_ssize_t i
        cdef long _value
        self.tryConversion(value, &_value)
        for i in range(self.length):
            self.data[i] = _value

    cpdef append(self, value):
        if self.length >= self.capacity:
            self.grow(self.length + 1)
        self.tryConversion(value, self.data + self.length)
        self.length += 1

    cpdef extend(self, values):
        cdef Py_ssize_t oldLength, newLength, i
        if isinstance(values, LongList):
            self.overwrite(values, self.length)
        elif isinstance(values, list):
            self.extendList(values)
        elif isinstance(values, tuple):
            self.extendTuple(values)
        elif hasattr(values, "__len__"):
            newLength = self.length + len(values)
            self.grow(newLength)
            for i, value in enumerate(values, start = self.length):
                self.tryConversion(value, self.data + i)
            self.length = newLength
        else:
            try:
                oldLength = self.length
                for value in values:
                    self.append(value)
            except:
                self.length = oldLength
                raise TypeError("invalid input")

    cdef extendList(self, list values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cdef extendTuple(self, tuple values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cpdef index(self, value):
        cdef long _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t index = self.searchIndex(_value)
        if index >= 0: return index
        raise ValueError("value not in list")

    cdef Py_ssize_t searchIndex(self, long value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef count(self, value):
        cdef long _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t i
        cdef Py_ssize_t amount = 0
        for i in range(self.length):
            if self.data[i] == _value:
                amount += 1
        return amount

    cpdef remove(self, value):
        cdef Py_ssize_t index = self.searchIndex(value)
        if index == -1:
            raise ValueError("value not in list")
        else:
            self.removeValueAtIndex(index)

    cpdef insert(self, Py_ssize_t index, value):
        cdef long _value
        if index >= self.length:
            self.append(value)
        else:
            self.tryConversion(value, &_value)
            self.grow(self.length + 1)
            if index < 0: index += self.length
            if index < 0: index = 0
            memmove(self.data + index + 1,
                    self.data + index,
                    sizeof(long) * (self.length - index))
            self.data[index] = _value
            self.length += 1



    # Get/Set/Remove single element
    ################################################

    cdef getValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        return self.data[index]

    cdef setValueAtIndex(self, Py_ssize_t index, long value):
        index = self.tryCorrectIndex(index)
        self.data[index] = value

    cdef removeValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        memmove(self.data + index,
                self.data + index + 1,
                (self.length - index) * sizeof(long))
        self.length -= 1


    # Get/Set/Remove elements in slice
    ################################################

    cdef LongList getValuesInSlice(self, slice sliceObject):
        cdef:
            void* newArray
            Py_ssize_t newLength
            LongList newList

        getValuesInSlice(self.data, self.length, sizeof(long),
                         &newArray, &newLength, sliceObject)

        newList = LongList()
        newList.replaceArray(<long*>newArray, newLength, newLength)
        return newList

    cdef setValuesInSlice(self, slice sliceObject, values):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))

        if step == 1:
            self.setValuesInSimpleSlice(start, stop, values)
        else:
            self.setValuesInExtendedSlice(start, stop, step, values)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values):
        cdef:
            Py_ssize_t replacementLength = len(values)
            Py_ssize_t sliceLength = predictSliceLength(start, stop, 1)

        if replacementLength > sliceLength:
            self.grow(self.length + (replacementLength - sliceLength))
        if replacementLength != sliceLength:
            memmove(self.data + start + replacementLength,
                    self.data + stop,
                    sizeof(long) * (self.length - stop))
            self.length += replacementLength - sliceLength

        cdef Py_ssize_t i
        cdef long _value
        if isinstance(values, LongList):
            self.overwrite(values, start)
        else:
            for i in range(replacementLength):
                self.tryConversion(values[i], self.data + start + i)

    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values):
        cdef Py_ssize_t sliceLength = predictSliceLength(start, stop, step)
        if sliceLength != len(values):
            raise ValueError("attempt to assign sequence of size {} to extended slice of size {}"
                             .format(len(values), sliceLength))

        # TODO: Speedup for specific list types + use while loop
        # range does not efficiently work with a variable step
        cdef Py_ssize_t i
        for i, value in zip(range(start, stop, step), values):
            self.tryConversion(value, self.data + i)

    cdef removeValuesInSlice(self, slice sliceObject):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))
        cdef Py_ssize_t removeAmount = removeValuesInSlice(
                      arrayStart = <char*>self.data,
                      arrayLength = self.length * sizeof(long),
                      elementSize = sizeof(long),
                      start = start, stop = stop, step = step)
        self.length -= removeAmount


    # Create new lists based on an existing list
    ###############################################

    cpdef LongList reversed(self):
        cdef:
            LongList newList = LongList(self.length)
            Py_ssize_t i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def repeated(self, *, Py_ssize_t length = -1, Py_ssize_t amount = -1):
        if length < 0 and amount < 0:
            raise ValueError("Specify the 'length' or 'amount' parameter as keyword")
        elif length > 0 and amount > 0:
            raise ValueError("Can only evaluate one parameter of 'length' and 'amount'")

        if amount >= 0:
            length = self.length * amount

        if self.length == 0 and length > 0:
            raise ValueError("Cannot repeat a list with zero elements to something longer")

        cdef:
            LongList newList = LongList(length)
            Py_ssize_t copyAmount = length // self.length
            Py_ssize_t i

        # Full copy as often as possible
        for i in range(copyAmount):
            memcpy(newList.data + i * self.length,
                   self.data,
                   sizeof(long) * self.length)
        # Partial copy at the end
        memcpy(newList.data + self.length * copyAmount,
               self.data,
               sizeof(long) * (length % self.length))
        return newList


    # Low level utilities
    ###############################################

    cdef tryConversion(self, value, long* target):
        target[0] = value

    cdef tryCorrectIndex(self, Py_ssize_t index):
        if index < 0:
            index += self.length
        if index < 0 or index >= self.length:
            raise IndexError("list index out of range")
        return index

    cdef overwrite(self, LongList other, Py_ssize_t index = 0):
        if self.capacity <= index + other.length:
            self.grow(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(long))
        self.length = max(self.length, index + other.length)

    cdef overwriteArray(self, long* array, Py_ssize_t arrayLength, Py_ssize_t index):
        if self.capacity <= index + arrayLength:
            self.grow(index + arrayLength)
        memcpy(self.data + index, array, arrayLength * sizeof(long))
        self.length = max(self.length, index + arrayLength)


    # Memory Views
    ###############################################

    cpdef getMemoryView(self):
        if "long" == "None":
            raise NotImplementedError("Cannot create memoryview for this type")

        cdef long[:] memview
        if self.length > 0:
            memview = <long[:self.length]>self.data
        else:
            # hack to make zero-length memview possible
            memview = (<long[:1]>self.data)[1:]
        return memview


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def join(cls, *sourceLists):
        cdef Py_ssize_t newLength = 0
        cdef Py_ssize_t offset = 0
        cdef LongList source

        for source in sourceLists:
            newLength += len(source)
        newList = LongList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, values):
        if isinstance(values, (list, tuple)):
            return cls.fromListOrTuple(values)

        try:
            from . convert import toLongList
            return toLongList(values)
        except TypeError: pass

        cdef LongList newList = LongList()
        newList.extend(values)
        return newList

    @classmethod
    def fromListOrTuple(cls, list_or_tuple values):
        cdef LongList newList = LongList(len(values))
        cdef Py_ssize_t i
        for i, value in enumerate(values):
            newList.tryConversion(value, newList.data + i)
        return newList


    # String Representations
    ###############################################

    def __repr__(self):
        if self.length < 20:
            return "<LongList [{}]>".format(", ".join(str(self[i]) for i in range(self.length)))
        else:
            return "<LongList [{}, ...]>".format(", ".join(str(self[i]) for i in range(20)))

    def status(self):
        return "Length: {}, Capacity: {}, Size: {} bytes".format(
            self.length, self.capacity, self.capacity * sizeof(long))


cdef class LongListIterator:
    '''
    Implements the 'Iterator Protocol' that is used to allow iteration
    over a custom list object (eg with a for loop).
    An instance of this class is only created in the __iter__ method
    of the corresponding list type.
    https://docs.python.org/3.5/library/stdtypes.html#iterator-types
    '''
    cdef:
        LongList source
        Py_ssize_t current

    def __cinit__(self, LongList source):
        self.source = source
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef long currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue


cimport cython
from types import GeneratorType
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy, memmove, memcmp
from . utils cimport predictSliceLength, makeStepPositive, removeValuesInSlice, getValuesInSlice

@cython.freelist(10)
cdef class ULongList:

    # Initialization and Memory Management
    ###############################################

    def __cinit__(self, Py_ssize_t length = 0, Py_ssize_t capacity = -1):
        '''
        Initialize a new object with the given length.
        You can also directly allocate more memory from the beginning
        to allow faster appending/extending without memory reallocation.
        '''
        if length < 0:
            raise ValueError("Length has to be >= 0")
        if capacity < length:
            capacity = length
        self.data = <unsigned long*>malloc(sizeof(unsigned long) * capacity)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.capacity = capacity

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef grow(self, Py_ssize_t minCapacity):
        if minCapacity < self.capacity:
            return

        cdef Py_ssize_t newCapacity = minCapacity * 2 + 1
        self.data = <unsigned long*>realloc(self.data, sizeof(unsigned long) * newCapacity)
        if self.data == NULL:
            self.length = 0
            self.capacity = 0
            raise MemoryError()
        self.capacity = newCapacity

    cdef void shrinkToLength(self):
        cdef Py_ssize_t newCapacity = max(1, self.length)
        self.data = <unsigned long*>realloc(self.data, sizeof(unsigned long) * newCapacity)
        self.capacity = newCapacity

    cdef replaceArray(self, unsigned long* newData, Py_ssize_t newLength, Py_ssize_t newCapacity):
        free(self.data)
        self.data = newData
        self.length = newLength
        self.capacity = newCapacity


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getValueAtIndex(key)
        elif isinstance(key, slice):
            return self.getValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.setValueAtIndex(key, value)
        elif isinstance(key, slice):
            self.setValuesInSlice(key, value)
        else:
            raise TypeError("Expected int or slice object")

    def __delitem__(self, key):
        if isinstance(key, int):
            self.removeValueAtIndex(key)
        elif isinstance(key, slice):
            self.removeValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __add__(a, b):
        cdef ULongList newList
        try:
            newList = ULongList(capacity = len(a) + len(b))
            newList.extend(a)
            newList.extend(b)
        except:
            raise NotImplementedError()
        return newList

    def __mul__(ULongList self, Py_ssize_t amount):
        return self.repeated(amount = amount)

    def __iadd__(ULongList self, other):
        try:
            self.extend(other)
        except:
            raise NotImplementedError()
        return self

    def __iter__(self):
        return ULongListIterator(self)

    def __contains__(self, unsigned long value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    def __richcmp__(x, y, int operation):
        if operation == 2: # '=='
            if type(x) == type(y):
                return (<ULongList>x).equals_SameType(y)
            if len(x) == len(y):
                return all(a == b for a, b in zip(x, y))
            return False
        raise NotImplemented()

    cdef equals_SameType(self, ULongList other):
        if self.length != other.length:
            return False
        cdef Py_ssize_t i
        for i in range(self.length):
            if not self.data[i] == other.data[i]: return False
        return True


    # Base operations for lists - mimic python list
    ###############################################

    cpdef copy(self):
        newList = ULongList(self.length)
        newList.overwrite(self)
        return newList

    cpdef clear(self):
        self.length = 0
        self.shrinkToLength()

    cpdef fill(self, value):
        cdef Py_ssize_t i
        cdef unsigned long _value
        self.tryConversion(value, &_value)
        for i in range(self.length):
            self.data[i] = _value

    cpdef append(self, value):
        if self.length >= self.capacity:
            self.grow(self.length + 1)
        self.tryConversion(value, self.data + self.length)
        self.length += 1

    cpdef extend(self, values):
        cdef Py_ssize_t oldLength, newLength, i
        if isinstance(values, ULongList):
            self.overwrite(values, self.length)
        elif isinstance(values, list):
            self.extendList(values)
        elif isinstance(values, tuple):
            self.extendTuple(values)
        elif hasattr(values, "__len__"):
            newLength = self.length + len(values)
            self.grow(newLength)
            for i, value in enumerate(values, start = self.length):
                self.tryConversion(value, self.data + i)
            self.length = newLength
        else:
            try:
                oldLength = self.length
                for value in values:
                    self.append(value)
            except:
                self.length = oldLength
                raise TypeError("invalid input")

    cdef extendList(self, list values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cdef extendTuple(self, tuple values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cpdef index(self, value):
        cdef unsigned long _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t index = self.searchIndex(_value)
        if index >= 0: return index
        raise ValueError("value not in list")

    cdef Py_ssize_t searchIndex(self, unsigned long value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef count(self, value):
        cdef unsigned long _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t i
        cdef Py_ssize_t amount = 0
        for i in range(self.length):
            if self.data[i] == _value:
                amount += 1
        return amount

    cpdef remove(self, value):
        cdef Py_ssize_t index = self.searchIndex(value)
        if index == -1:
            raise ValueError("value not in list")
        else:
            self.removeValueAtIndex(index)

    cpdef insert(self, Py_ssize_t index, value):
        cdef unsigned long _value
        if index >= self.length:
            self.append(value)
        else:
            self.tryConversion(value, &_value)
            self.grow(self.length + 1)
            if index < 0: index += self.length
            if index < 0: index = 0
            memmove(self.data + index + 1,
                    self.data + index,
                    sizeof(unsigned long) * (self.length - index))
            self.data[index] = _value
            self.length += 1



    # Get/Set/Remove single element
    ################################################

    cdef getValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        return self.data[index]

    cdef setValueAtIndex(self, Py_ssize_t index, unsigned long value):
        index = self.tryCorrectIndex(index)
        self.data[index] = value

    cdef removeValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        memmove(self.data + index,
                self.data + index + 1,
                (self.length - index) * sizeof(unsigned long))
        self.length -= 1


    # Get/Set/Remove elements in slice
    ################################################

    cdef ULongList getValuesInSlice(self, slice sliceObject):
        cdef:
            void* newArray
            Py_ssize_t newLength
            ULongList newList

        getValuesInSlice(self.data, self.length, sizeof(unsigned long),
                         &newArray, &newLength, sliceObject)

        newList = ULongList()
        newList.replaceArray(<unsigned long*>newArray, newLength, newLength)
        return newList

    cdef setValuesInSlice(self, slice sliceObject, values):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))

        if step == 1:
            self.setValuesInSimpleSlice(start, stop, values)
        else:
            self.setValuesInExtendedSlice(start, stop, step, values)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values):
        cdef:
            Py_ssize_t replacementLength = len(values)
            Py_ssize_t sliceLength = predictSliceLength(start, stop, 1)

        if replacementLength > sliceLength:
            self.grow(self.length + (replacementLength - sliceLength))
        if replacementLength != sliceLength:
            memmove(self.data + start + replacementLength,
                    self.data + stop,
                    sizeof(unsigned long) * (self.length - stop))
            self.length += replacementLength - sliceLength

        cdef Py_ssize_t i
        cdef unsigned long _value
        if isinstance(values, ULongList):
            self.overwrite(values, start)
        else:
            for i in range(replacementLength):
                self.tryConversion(values[i], self.data + start + i)

    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values):
        cdef Py_ssize_t sliceLength = predictSliceLength(start, stop, step)
        if sliceLength != len(values):
            raise ValueError("attempt to assign sequence of size {} to extended slice of size {}"
                             .format(len(values), sliceLength))

        # TODO: Speedup for specific list types + use while loop
        # range does not efficiently work with a variable step
        cdef Py_ssize_t i
        for i, value in zip(range(start, stop, step), values):
            self.tryConversion(value, self.data + i)

    cdef removeValuesInSlice(self, slice sliceObject):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))
        cdef Py_ssize_t removeAmount = removeValuesInSlice(
                      arrayStart = <char*>self.data,
                      arrayLength = self.length * sizeof(unsigned long),
                      elementSize = sizeof(unsigned long),
                      start = start, stop = stop, step = step)
        self.length -= removeAmount


    # Create new lists based on an existing list
    ###############################################

    cpdef ULongList reversed(self):
        cdef:
            ULongList newList = ULongList(self.length)
            Py_ssize_t i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def repeated(self, *, Py_ssize_t length = -1, Py_ssize_t amount = -1):
        if length < 0 and amount < 0:
            raise ValueError("Specify the 'length' or 'amount' parameter as keyword")
        elif length > 0 and amount > 0:
            raise ValueError("Can only evaluate one parameter of 'length' and 'amount'")

        if amount >= 0:
            length = self.length * amount

        if self.length == 0 and length > 0:
            raise ValueError("Cannot repeat a list with zero elements to something longer")

        cdef:
            ULongList newList = ULongList(length)
            Py_ssize_t copyAmount = length // self.length
            Py_ssize_t i

        # Full copy as often as possible
        for i in range(copyAmount):
            memcpy(newList.data + i * self.length,
                   self.data,
                   sizeof(unsigned long) * self.length)
        # Partial copy at the end
        memcpy(newList.data + self.length * copyAmount,
               self.data,
               sizeof(unsigned long) * (length % self.length))
        return newList


    # Low level utilities
    ###############################################

    cdef tryConversion(self, value, unsigned long* target):
        target[0] = value

    cdef tryCorrectIndex(self, Py_ssize_t index):
        if index < 0:
            index += self.length
        if index < 0 or index >= self.length:
            raise IndexError("list index out of range")
        return index

    cdef overwrite(self, ULongList other, Py_ssize_t index = 0):
        if self.capacity <= index + other.length:
            self.grow(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(unsigned long))
        self.length = max(self.length, index + other.length)

    cdef overwriteArray(self, unsigned long* array, Py_ssize_t arrayLength, Py_ssize_t index):
        if self.capacity <= index + arrayLength:
            self.grow(index + arrayLength)
        memcpy(self.data + index, array, arrayLength * sizeof(unsigned long))
        self.length = max(self.length, index + arrayLength)


    # Memory Views
    ###############################################

    cpdef getMemoryView(self):
        if "unsigned long" == "None":
            raise NotImplementedError("Cannot create memoryview for this type")

        cdef unsigned long[:] memview
        if self.length > 0:
            memview = <unsigned long[:self.length]>self.data
        else:
            # hack to make zero-length memview possible
            memview = (<unsigned long[:1]>self.data)[1:]
        return memview


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def join(cls, *sourceLists):
        cdef Py_ssize_t newLength = 0
        cdef Py_ssize_t offset = 0
        cdef ULongList source

        for source in sourceLists:
            newLength += len(source)
        newList = ULongList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, values):
        if isinstance(values, (list, tuple)):
            return cls.fromListOrTuple(values)

        try:
            from . convert import toULongList
            return toULongList(values)
        except TypeError: pass

        cdef ULongList newList = ULongList()
        newList.extend(values)
        return newList

    @classmethod
    def fromListOrTuple(cls, list_or_tuple values):
        cdef ULongList newList = ULongList(len(values))
        cdef Py_ssize_t i
        for i, value in enumerate(values):
            newList.tryConversion(value, newList.data + i)
        return newList


    # String Representations
    ###############################################

    def __repr__(self):
        if self.length < 20:
            return "<ULongList [{}]>".format(", ".join(str(self[i]) for i in range(self.length)))
        else:
            return "<ULongList [{}, ...]>".format(", ".join(str(self[i]) for i in range(20)))

    def status(self):
        return "Length: {}, Capacity: {}, Size: {} bytes".format(
            self.length, self.capacity, self.capacity * sizeof(unsigned long))


cdef class ULongListIterator:
    '''
    Implements the 'Iterator Protocol' that is used to allow iteration
    over a custom list object (eg with a for loop).
    An instance of this class is only created in the __iter__ method
    of the corresponding list type.
    https://docs.python.org/3.5/library/stdtypes.html#iterator-types
    '''
    cdef:
        ULongList source
        Py_ssize_t current

    def __cinit__(self, ULongList source):
        self.source = source
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef unsigned long currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue


cimport cython
from types import GeneratorType
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy, memmove, memcmp
from . utils cimport predictSliceLength, makeStepPositive, removeValuesInSlice, getValuesInSlice

@cython.freelist(10)
cdef class IntegerList:

    # Initialization and Memory Management
    ###############################################

    def __cinit__(self, Py_ssize_t length = 0, Py_ssize_t capacity = -1):
        '''
        Initialize a new object with the given length.
        You can also directly allocate more memory from the beginning
        to allow faster appending/extending without memory reallocation.
        '''
        if length < 0:
            raise ValueError("Length has to be >= 0")
        if capacity < length:
            capacity = length
        self.data = <int*>malloc(sizeof(int) * capacity)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.capacity = capacity

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef grow(self, Py_ssize_t minCapacity):
        if minCapacity < self.capacity:
            return

        cdef Py_ssize_t newCapacity = minCapacity * 2 + 1
        self.data = <int*>realloc(self.data, sizeof(int) * newCapacity)
        if self.data == NULL:
            self.length = 0
            self.capacity = 0
            raise MemoryError()
        self.capacity = newCapacity

    cdef void shrinkToLength(self):
        cdef Py_ssize_t newCapacity = max(1, self.length)
        self.data = <int*>realloc(self.data, sizeof(int) * newCapacity)
        self.capacity = newCapacity

    cdef replaceArray(self, int* newData, Py_ssize_t newLength, Py_ssize_t newCapacity):
        free(self.data)
        self.data = newData
        self.length = newLength
        self.capacity = newCapacity


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getValueAtIndex(key)
        elif isinstance(key, slice):
            return self.getValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.setValueAtIndex(key, value)
        elif isinstance(key, slice):
            self.setValuesInSlice(key, value)
        else:
            raise TypeError("Expected int or slice object")

    def __delitem__(self, key):
        if isinstance(key, int):
            self.removeValueAtIndex(key)
        elif isinstance(key, slice):
            self.removeValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __add__(a, b):
        cdef IntegerList newList
        try:
            newList = IntegerList(capacity = len(a) + len(b))
            newList.extend(a)
            newList.extend(b)
        except:
            raise NotImplementedError()
        return newList

    def __mul__(IntegerList self, Py_ssize_t amount):
        return self.repeated(amount = amount)

    def __iadd__(IntegerList self, other):
        try:
            self.extend(other)
        except:
            raise NotImplementedError()
        return self

    def __iter__(self):
        return IntegerListIterator(self)

    def __contains__(self, int value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    def __richcmp__(x, y, int operation):
        if operation == 2: # '=='
            if type(x) == type(y):
                return (<IntegerList>x).equals_SameType(y)
            if len(x) == len(y):
                return all(a == b for a, b in zip(x, y))
            return False
        raise NotImplemented()

    cdef equals_SameType(self, IntegerList other):
        if self.length != other.length:
            return False
        cdef Py_ssize_t i
        for i in range(self.length):
            if not self.data[i] == other.data[i]: return False
        return True


    # Base operations for lists - mimic python list
    ###############################################

    cpdef copy(self):
        newList = IntegerList(self.length)
        newList.overwrite(self)
        return newList

    cpdef clear(self):
        self.length = 0
        self.shrinkToLength()

    cpdef fill(self, value):
        cdef Py_ssize_t i
        cdef int _value
        self.tryConversion(value, &_value)
        for i in range(self.length):
            self.data[i] = _value

    cpdef append(self, value):
        if self.length >= self.capacity:
            self.grow(self.length + 1)
        self.tryConversion(value, self.data + self.length)
        self.length += 1

    cpdef extend(self, values):
        cdef Py_ssize_t oldLength, newLength, i
        if isinstance(values, IntegerList):
            self.overwrite(values, self.length)
        elif isinstance(values, list):
            self.extendList(values)
        elif isinstance(values, tuple):
            self.extendTuple(values)
        elif hasattr(values, "__len__"):
            newLength = self.length + len(values)
            self.grow(newLength)
            for i, value in enumerate(values, start = self.length):
                self.tryConversion(value, self.data + i)
            self.length = newLength
        else:
            try:
                oldLength = self.length
                for value in values:
                    self.append(value)
            except:
                self.length = oldLength
                raise TypeError("invalid input")

    cdef extendList(self, list values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cdef extendTuple(self, tuple values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cpdef index(self, value):
        cdef int _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t index = self.searchIndex(_value)
        if index >= 0: return index
        raise ValueError("value not in list")

    cdef Py_ssize_t searchIndex(self, int value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef count(self, value):
        cdef int _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t i
        cdef Py_ssize_t amount = 0
        for i in range(self.length):
            if self.data[i] == _value:
                amount += 1
        return amount

    cpdef remove(self, value):
        cdef Py_ssize_t index = self.searchIndex(value)
        if index == -1:
            raise ValueError("value not in list")
        else:
            self.removeValueAtIndex(index)

    cpdef insert(self, Py_ssize_t index, value):
        cdef int _value
        if index >= self.length:
            self.append(value)
        else:
            self.tryConversion(value, &_value)
            self.grow(self.length + 1)
            if index < 0: index += self.length
            if index < 0: index = 0
            memmove(self.data + index + 1,
                    self.data + index,
                    sizeof(int) * (self.length - index))
            self.data[index] = _value
            self.length += 1



    # Get/Set/Remove single element
    ################################################

    cdef getValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        return self.data[index]

    cdef setValueAtIndex(self, Py_ssize_t index, int value):
        index = self.tryCorrectIndex(index)
        self.data[index] = value

    cdef removeValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        memmove(self.data + index,
                self.data + index + 1,
                (self.length - index) * sizeof(int))
        self.length -= 1


    # Get/Set/Remove elements in slice
    ################################################

    cdef IntegerList getValuesInSlice(self, slice sliceObject):
        cdef:
            void* newArray
            Py_ssize_t newLength
            IntegerList newList

        getValuesInSlice(self.data, self.length, sizeof(int),
                         &newArray, &newLength, sliceObject)

        newList = IntegerList()
        newList.replaceArray(<int*>newArray, newLength, newLength)
        return newList

    cdef setValuesInSlice(self, slice sliceObject, values):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))

        if step == 1:
            self.setValuesInSimpleSlice(start, stop, values)
        else:
            self.setValuesInExtendedSlice(start, stop, step, values)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values):
        cdef:
            Py_ssize_t replacementLength = len(values)
            Py_ssize_t sliceLength = predictSliceLength(start, stop, 1)

        if replacementLength > sliceLength:
            self.grow(self.length + (replacementLength - sliceLength))
        if replacementLength != sliceLength:
            memmove(self.data + start + replacementLength,
                    self.data + stop,
                    sizeof(int) * (self.length - stop))
            self.length += replacementLength - sliceLength

        cdef Py_ssize_t i
        cdef int _value
        if isinstance(values, IntegerList):
            self.overwrite(values, start)
        else:
            for i in range(replacementLength):
                self.tryConversion(values[i], self.data + start + i)

    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values):
        cdef Py_ssize_t sliceLength = predictSliceLength(start, stop, step)
        if sliceLength != len(values):
            raise ValueError("attempt to assign sequence of size {} to extended slice of size {}"
                             .format(len(values), sliceLength))

        # TODO: Speedup for specific list types + use while loop
        # range does not efficiently work with a variable step
        cdef Py_ssize_t i
        for i, value in zip(range(start, stop, step), values):
            self.tryConversion(value, self.data + i)

    cdef removeValuesInSlice(self, slice sliceObject):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))
        cdef Py_ssize_t removeAmount = removeValuesInSlice(
                      arrayStart = <char*>self.data,
                      arrayLength = self.length * sizeof(int),
                      elementSize = sizeof(int),
                      start = start, stop = stop, step = step)
        self.length -= removeAmount


    # Create new lists based on an existing list
    ###############################################

    cpdef IntegerList reversed(self):
        cdef:
            IntegerList newList = IntegerList(self.length)
            Py_ssize_t i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def repeated(self, *, Py_ssize_t length = -1, Py_ssize_t amount = -1):
        if length < 0 and amount < 0:
            raise ValueError("Specify the 'length' or 'amount' parameter as keyword")
        elif length > 0 and amount > 0:
            raise ValueError("Can only evaluate one parameter of 'length' and 'amount'")

        if amount >= 0:
            length = self.length * amount

        if self.length == 0 and length > 0:
            raise ValueError("Cannot repeat a list with zero elements to something longer")

        cdef:
            IntegerList newList = IntegerList(length)
            Py_ssize_t copyAmount = length // self.length
            Py_ssize_t i

        # Full copy as often as possible
        for i in range(copyAmount):
            memcpy(newList.data + i * self.length,
                   self.data,
                   sizeof(int) * self.length)
        # Partial copy at the end
        memcpy(newList.data + self.length * copyAmount,
               self.data,
               sizeof(int) * (length % self.length))
        return newList


    # Low level utilities
    ###############################################

    cdef tryConversion(self, value, int* target):
        target[0] = value

    cdef tryCorrectIndex(self, Py_ssize_t index):
        if index < 0:
            index += self.length
        if index < 0 or index >= self.length:
            raise IndexError("list index out of range")
        return index

    cdef overwrite(self, IntegerList other, Py_ssize_t index = 0):
        if self.capacity <= index + other.length:
            self.grow(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(int))
        self.length = max(self.length, index + other.length)

    cdef overwriteArray(self, int* array, Py_ssize_t arrayLength, Py_ssize_t index):
        if self.capacity <= index + arrayLength:
            self.grow(index + arrayLength)
        memcpy(self.data + index, array, arrayLength * sizeof(int))
        self.length = max(self.length, index + arrayLength)


    # Memory Views
    ###############################################

    cpdef getMemoryView(self):
        if "int" == "None":
            raise NotImplementedError("Cannot create memoryview for this type")

        cdef int[:] memview
        if self.length > 0:
            memview = <int[:self.length]>self.data
        else:
            # hack to make zero-length memview possible
            memview = (<int[:1]>self.data)[1:]
        return memview


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def join(cls, *sourceLists):
        cdef Py_ssize_t newLength = 0
        cdef Py_ssize_t offset = 0
        cdef IntegerList source

        for source in sourceLists:
            newLength += len(source)
        newList = IntegerList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, values):
        if isinstance(values, (list, tuple)):
            return cls.fromListOrTuple(values)

        try:
            from . convert import toIntegerList
            return toIntegerList(values)
        except TypeError: pass

        cdef IntegerList newList = IntegerList()
        newList.extend(values)
        return newList

    @classmethod
    def fromListOrTuple(cls, list_or_tuple values):
        cdef IntegerList newList = IntegerList(len(values))
        cdef Py_ssize_t i
        for i, value in enumerate(values):
            newList.tryConversion(value, newList.data + i)
        return newList


    # String Representations
    ###############################################

    def __repr__(self):
        if self.length < 20:
            return "<IntegerList [{}]>".format(", ".join(str(self[i]) for i in range(self.length)))
        else:
            return "<IntegerList [{}, ...]>".format(", ".join(str(self[i]) for i in range(20)))

    def status(self):
        return "Length: {}, Capacity: {}, Size: {} bytes".format(
            self.length, self.capacity, self.capacity * sizeof(int))


cdef class IntegerListIterator:
    '''
    Implements the 'Iterator Protocol' that is used to allow iteration
    over a custom list object (eg with a for loop).
    An instance of this class is only created in the __iter__ method
    of the corresponding list type.
    https://docs.python.org/3.5/library/stdtypes.html#iterator-types
    '''
    cdef:
        IntegerList source
        Py_ssize_t current

    def __cinit__(self, IntegerList source):
        self.source = source
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef int currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue


cimport cython
from types import GeneratorType
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy, memmove, memcmp
from . utils cimport predictSliceLength, makeStepPositive, removeValuesInSlice, getValuesInSlice

@cython.freelist(10)
cdef class UIntegerList:

    # Initialization and Memory Management
    ###############################################

    def __cinit__(self, Py_ssize_t length = 0, Py_ssize_t capacity = -1):
        '''
        Initialize a new object with the given length.
        You can also directly allocate more memory from the beginning
        to allow faster appending/extending without memory reallocation.
        '''
        if length < 0:
            raise ValueError("Length has to be >= 0")
        if capacity < length:
            capacity = length
        self.data = <unsigned int*>malloc(sizeof(unsigned int) * capacity)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.capacity = capacity

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef grow(self, Py_ssize_t minCapacity):
        if minCapacity < self.capacity:
            return

        cdef Py_ssize_t newCapacity = minCapacity * 2 + 1
        self.data = <unsigned int*>realloc(self.data, sizeof(unsigned int) * newCapacity)
        if self.data == NULL:
            self.length = 0
            self.capacity = 0
            raise MemoryError()
        self.capacity = newCapacity

    cdef void shrinkToLength(self):
        cdef Py_ssize_t newCapacity = max(1, self.length)
        self.data = <unsigned int*>realloc(self.data, sizeof(unsigned int) * newCapacity)
        self.capacity = newCapacity

    cdef replaceArray(self, unsigned int* newData, Py_ssize_t newLength, Py_ssize_t newCapacity):
        free(self.data)
        self.data = newData
        self.length = newLength
        self.capacity = newCapacity


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getValueAtIndex(key)
        elif isinstance(key, slice):
            return self.getValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.setValueAtIndex(key, value)
        elif isinstance(key, slice):
            self.setValuesInSlice(key, value)
        else:
            raise TypeError("Expected int or slice object")

    def __delitem__(self, key):
        if isinstance(key, int):
            self.removeValueAtIndex(key)
        elif isinstance(key, slice):
            self.removeValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __add__(a, b):
        cdef UIntegerList newList
        try:
            newList = UIntegerList(capacity = len(a) + len(b))
            newList.extend(a)
            newList.extend(b)
        except:
            raise NotImplementedError()
        return newList

    def __mul__(UIntegerList self, Py_ssize_t amount):
        return self.repeated(amount = amount)

    def __iadd__(UIntegerList self, other):
        try:
            self.extend(other)
        except:
            raise NotImplementedError()
        return self

    def __iter__(self):
        return UIntegerListIterator(self)

    def __contains__(self, unsigned int value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    def __richcmp__(x, y, int operation):
        if operation == 2: # '=='
            if type(x) == type(y):
                return (<UIntegerList>x).equals_SameType(y)
            if len(x) == len(y):
                return all(a == b for a, b in zip(x, y))
            return False
        raise NotImplemented()

    cdef equals_SameType(self, UIntegerList other):
        if self.length != other.length:
            return False
        cdef Py_ssize_t i
        for i in range(self.length):
            if not self.data[i] == other.data[i]: return False
        return True


    # Base operations for lists - mimic python list
    ###############################################

    cpdef copy(self):
        newList = UIntegerList(self.length)
        newList.overwrite(self)
        return newList

    cpdef clear(self):
        self.length = 0
        self.shrinkToLength()

    cpdef fill(self, value):
        cdef Py_ssize_t i
        cdef unsigned int _value
        self.tryConversion(value, &_value)
        for i in range(self.length):
            self.data[i] = _value

    cpdef append(self, value):
        if self.length >= self.capacity:
            self.grow(self.length + 1)
        self.tryConversion(value, self.data + self.length)
        self.length += 1

    cpdef extend(self, values):
        cdef Py_ssize_t oldLength, newLength, i
        if isinstance(values, UIntegerList):
            self.overwrite(values, self.length)
        elif isinstance(values, list):
            self.extendList(values)
        elif isinstance(values, tuple):
            self.extendTuple(values)
        elif hasattr(values, "__len__"):
            newLength = self.length + len(values)
            self.grow(newLength)
            for i, value in enumerate(values, start = self.length):
                self.tryConversion(value, self.data + i)
            self.length = newLength
        else:
            try:
                oldLength = self.length
                for value in values:
                    self.append(value)
            except:
                self.length = oldLength
                raise TypeError("invalid input")

    cdef extendList(self, list values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cdef extendTuple(self, tuple values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cpdef index(self, value):
        cdef unsigned int _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t index = self.searchIndex(_value)
        if index >= 0: return index
        raise ValueError("value not in list")

    cdef Py_ssize_t searchIndex(self, unsigned int value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef count(self, value):
        cdef unsigned int _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t i
        cdef Py_ssize_t amount = 0
        for i in range(self.length):
            if self.data[i] == _value:
                amount += 1
        return amount

    cpdef remove(self, value):
        cdef Py_ssize_t index = self.searchIndex(value)
        if index == -1:
            raise ValueError("value not in list")
        else:
            self.removeValueAtIndex(index)

    cpdef insert(self, Py_ssize_t index, value):
        cdef unsigned int _value
        if index >= self.length:
            self.append(value)
        else:
            self.tryConversion(value, &_value)
            self.grow(self.length + 1)
            if index < 0: index += self.length
            if index < 0: index = 0
            memmove(self.data + index + 1,
                    self.data + index,
                    sizeof(unsigned int) * (self.length - index))
            self.data[index] = _value
            self.length += 1



    # Get/Set/Remove single element
    ################################################

    cdef getValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        return self.data[index]

    cdef setValueAtIndex(self, Py_ssize_t index, unsigned int value):
        index = self.tryCorrectIndex(index)
        self.data[index] = value

    cdef removeValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        memmove(self.data + index,
                self.data + index + 1,
                (self.length - index) * sizeof(unsigned int))
        self.length -= 1


    # Get/Set/Remove elements in slice
    ################################################

    cdef UIntegerList getValuesInSlice(self, slice sliceObject):
        cdef:
            void* newArray
            Py_ssize_t newLength
            UIntegerList newList

        getValuesInSlice(self.data, self.length, sizeof(unsigned int),
                         &newArray, &newLength, sliceObject)

        newList = UIntegerList()
        newList.replaceArray(<unsigned int*>newArray, newLength, newLength)
        return newList

    cdef setValuesInSlice(self, slice sliceObject, values):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))

        if step == 1:
            self.setValuesInSimpleSlice(start, stop, values)
        else:
            self.setValuesInExtendedSlice(start, stop, step, values)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values):
        cdef:
            Py_ssize_t replacementLength = len(values)
            Py_ssize_t sliceLength = predictSliceLength(start, stop, 1)

        if replacementLength > sliceLength:
            self.grow(self.length + (replacementLength - sliceLength))
        if replacementLength != sliceLength:
            memmove(self.data + start + replacementLength,
                    self.data + stop,
                    sizeof(unsigned int) * (self.length - stop))
            self.length += replacementLength - sliceLength

        cdef Py_ssize_t i
        cdef unsigned int _value
        if isinstance(values, UIntegerList):
            self.overwrite(values, start)
        else:
            for i in range(replacementLength):
                self.tryConversion(values[i], self.data + start + i)

    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values):
        cdef Py_ssize_t sliceLength = predictSliceLength(start, stop, step)
        if sliceLength != len(values):
            raise ValueError("attempt to assign sequence of size {} to extended slice of size {}"
                             .format(len(values), sliceLength))

        # TODO: Speedup for specific list types + use while loop
        # range does not efficiently work with a variable step
        cdef Py_ssize_t i
        for i, value in zip(range(start, stop, step), values):
            self.tryConversion(value, self.data + i)

    cdef removeValuesInSlice(self, slice sliceObject):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))
        cdef Py_ssize_t removeAmount = removeValuesInSlice(
                      arrayStart = <char*>self.data,
                      arrayLength = self.length * sizeof(unsigned int),
                      elementSize = sizeof(unsigned int),
                      start = start, stop = stop, step = step)
        self.length -= removeAmount


    # Create new lists based on an existing list
    ###############################################

    cpdef UIntegerList reversed(self):
        cdef:
            UIntegerList newList = UIntegerList(self.length)
            Py_ssize_t i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def repeated(self, *, Py_ssize_t length = -1, Py_ssize_t amount = -1):
        if length < 0 and amount < 0:
            raise ValueError("Specify the 'length' or 'amount' parameter as keyword")
        elif length > 0 and amount > 0:
            raise ValueError("Can only evaluate one parameter of 'length' and 'amount'")

        if amount >= 0:
            length = self.length * amount

        if self.length == 0 and length > 0:
            raise ValueError("Cannot repeat a list with zero elements to something longer")

        cdef:
            UIntegerList newList = UIntegerList(length)
            Py_ssize_t copyAmount = length // self.length
            Py_ssize_t i

        # Full copy as often as possible
        for i in range(copyAmount):
            memcpy(newList.data + i * self.length,
                   self.data,
                   sizeof(unsigned int) * self.length)
        # Partial copy at the end
        memcpy(newList.data + self.length * copyAmount,
               self.data,
               sizeof(unsigned int) * (length % self.length))
        return newList


    # Low level utilities
    ###############################################

    cdef tryConversion(self, value, unsigned int* target):
        target[0] = value

    cdef tryCorrectIndex(self, Py_ssize_t index):
        if index < 0:
            index += self.length
        if index < 0 or index >= self.length:
            raise IndexError("list index out of range")
        return index

    cdef overwrite(self, UIntegerList other, Py_ssize_t index = 0):
        if self.capacity <= index + other.length:
            self.grow(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(unsigned int))
        self.length = max(self.length, index + other.length)

    cdef overwriteArray(self, unsigned int* array, Py_ssize_t arrayLength, Py_ssize_t index):
        if self.capacity <= index + arrayLength:
            self.grow(index + arrayLength)
        memcpy(self.data + index, array, arrayLength * sizeof(unsigned int))
        self.length = max(self.length, index + arrayLength)


    # Memory Views
    ###############################################

    cpdef getMemoryView(self):
        if "unsigned int" == "None":
            raise NotImplementedError("Cannot create memoryview for this type")

        cdef unsigned int[:] memview
        if self.length > 0:
            memview = <unsigned int[:self.length]>self.data
        else:
            # hack to make zero-length memview possible
            memview = (<unsigned int[:1]>self.data)[1:]
        return memview


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def join(cls, *sourceLists):
        cdef Py_ssize_t newLength = 0
        cdef Py_ssize_t offset = 0
        cdef UIntegerList source

        for source in sourceLists:
            newLength += len(source)
        newList = UIntegerList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, values):
        if isinstance(values, (list, tuple)):
            return cls.fromListOrTuple(values)

        try:
            from . convert import toUIntegerList
            return toUIntegerList(values)
        except TypeError: pass

        cdef UIntegerList newList = UIntegerList()
        newList.extend(values)
        return newList

    @classmethod
    def fromListOrTuple(cls, list_or_tuple values):
        cdef UIntegerList newList = UIntegerList(len(values))
        cdef Py_ssize_t i
        for i, value in enumerate(values):
            newList.tryConversion(value, newList.data + i)
        return newList


    # String Representations
    ###############################################

    def __repr__(self):
        if self.length < 20:
            return "<UIntegerList [{}]>".format(", ".join(str(self[i]) for i in range(self.length)))
        else:
            return "<UIntegerList [{}, ...]>".format(", ".join(str(self[i]) for i in range(20)))

    def status(self):
        return "Length: {}, Capacity: {}, Size: {} bytes".format(
            self.length, self.capacity, self.capacity * sizeof(unsigned int))


cdef class UIntegerListIterator:
    '''
    Implements the 'Iterator Protocol' that is used to allow iteration
    over a custom list object (eg with a for loop).
    An instance of this class is only created in the __iter__ method
    of the corresponding list type.
    https://docs.python.org/3.5/library/stdtypes.html#iterator-types
    '''
    cdef:
        UIntegerList source
        Py_ssize_t current

    def __cinit__(self, UIntegerList source):
        self.source = source
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef unsigned int currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue


cimport cython
from types import GeneratorType
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy, memmove, memcmp
from . utils cimport predictSliceLength, makeStepPositive, removeValuesInSlice, getValuesInSlice

@cython.freelist(10)
cdef class ShortList:

    # Initialization and Memory Management
    ###############################################

    def __cinit__(self, Py_ssize_t length = 0, Py_ssize_t capacity = -1):
        '''
        Initialize a new object with the given length.
        You can also directly allocate more memory from the beginning
        to allow faster appending/extending without memory reallocation.
        '''
        if length < 0:
            raise ValueError("Length has to be >= 0")
        if capacity < length:
            capacity = length
        self.data = <short*>malloc(sizeof(short) * capacity)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.capacity = capacity

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef grow(self, Py_ssize_t minCapacity):
        if minCapacity < self.capacity:
            return

        cdef Py_ssize_t newCapacity = minCapacity * 2 + 1
        self.data = <short*>realloc(self.data, sizeof(short) * newCapacity)
        if self.data == NULL:
            self.length = 0
            self.capacity = 0
            raise MemoryError()
        self.capacity = newCapacity

    cdef void shrinkToLength(self):
        cdef Py_ssize_t newCapacity = max(1, self.length)
        self.data = <short*>realloc(self.data, sizeof(short) * newCapacity)
        self.capacity = newCapacity

    cdef replaceArray(self, short* newData, Py_ssize_t newLength, Py_ssize_t newCapacity):
        free(self.data)
        self.data = newData
        self.length = newLength
        self.capacity = newCapacity


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getValueAtIndex(key)
        elif isinstance(key, slice):
            return self.getValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.setValueAtIndex(key, value)
        elif isinstance(key, slice):
            self.setValuesInSlice(key, value)
        else:
            raise TypeError("Expected int or slice object")

    def __delitem__(self, key):
        if isinstance(key, int):
            self.removeValueAtIndex(key)
        elif isinstance(key, slice):
            self.removeValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __add__(a, b):
        cdef ShortList newList
        try:
            newList = ShortList(capacity = len(a) + len(b))
            newList.extend(a)
            newList.extend(b)
        except:
            raise NotImplementedError()
        return newList

    def __mul__(ShortList self, Py_ssize_t amount):
        return self.repeated(amount = amount)

    def __iadd__(ShortList self, other):
        try:
            self.extend(other)
        except:
            raise NotImplementedError()
        return self

    def __iter__(self):
        return ShortListIterator(self)

    def __contains__(self, short value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    def __richcmp__(x, y, int operation):
        if operation == 2: # '=='
            if type(x) == type(y):
                return (<ShortList>x).equals_SameType(y)
            if len(x) == len(y):
                return all(a == b for a, b in zip(x, y))
            return False
        raise NotImplemented()

    cdef equals_SameType(self, ShortList other):
        if self.length != other.length:
            return False
        cdef Py_ssize_t i
        for i in range(self.length):
            if not self.data[i] == other.data[i]: return False
        return True


    # Base operations for lists - mimic python list
    ###############################################

    cpdef copy(self):
        newList = ShortList(self.length)
        newList.overwrite(self)
        return newList

    cpdef clear(self):
        self.length = 0
        self.shrinkToLength()

    cpdef fill(self, value):
        cdef Py_ssize_t i
        cdef short _value
        self.tryConversion(value, &_value)
        for i in range(self.length):
            self.data[i] = _value

    cpdef append(self, value):
        if self.length >= self.capacity:
            self.grow(self.length + 1)
        self.tryConversion(value, self.data + self.length)
        self.length += 1

    cpdef extend(self, values):
        cdef Py_ssize_t oldLength, newLength, i
        if isinstance(values, ShortList):
            self.overwrite(values, self.length)
        elif isinstance(values, list):
            self.extendList(values)
        elif isinstance(values, tuple):
            self.extendTuple(values)
        elif hasattr(values, "__len__"):
            newLength = self.length + len(values)
            self.grow(newLength)
            for i, value in enumerate(values, start = self.length):
                self.tryConversion(value, self.data + i)
            self.length = newLength
        else:
            try:
                oldLength = self.length
                for value in values:
                    self.append(value)
            except:
                self.length = oldLength
                raise TypeError("invalid input")

    cdef extendList(self, list values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cdef extendTuple(self, tuple values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cpdef index(self, value):
        cdef short _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t index = self.searchIndex(_value)
        if index >= 0: return index
        raise ValueError("value not in list")

    cdef Py_ssize_t searchIndex(self, short value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef count(self, value):
        cdef short _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t i
        cdef Py_ssize_t amount = 0
        for i in range(self.length):
            if self.data[i] == _value:
                amount += 1
        return amount

    cpdef remove(self, value):
        cdef Py_ssize_t index = self.searchIndex(value)
        if index == -1:
            raise ValueError("value not in list")
        else:
            self.removeValueAtIndex(index)

    cpdef insert(self, Py_ssize_t index, value):
        cdef short _value
        if index >= self.length:
            self.append(value)
        else:
            self.tryConversion(value, &_value)
            self.grow(self.length + 1)
            if index < 0: index += self.length
            if index < 0: index = 0
            memmove(self.data + index + 1,
                    self.data + index,
                    sizeof(short) * (self.length - index))
            self.data[index] = _value
            self.length += 1



    # Get/Set/Remove single element
    ################################################

    cdef getValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        return self.data[index]

    cdef setValueAtIndex(self, Py_ssize_t index, short value):
        index = self.tryCorrectIndex(index)
        self.data[index] = value

    cdef removeValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        memmove(self.data + index,
                self.data + index + 1,
                (self.length - index) * sizeof(short))
        self.length -= 1


    # Get/Set/Remove elements in slice
    ################################################

    cdef ShortList getValuesInSlice(self, slice sliceObject):
        cdef:
            void* newArray
            Py_ssize_t newLength
            ShortList newList

        getValuesInSlice(self.data, self.length, sizeof(short),
                         &newArray, &newLength, sliceObject)

        newList = ShortList()
        newList.replaceArray(<short*>newArray, newLength, newLength)
        return newList

    cdef setValuesInSlice(self, slice sliceObject, values):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))

        if step == 1:
            self.setValuesInSimpleSlice(start, stop, values)
        else:
            self.setValuesInExtendedSlice(start, stop, step, values)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values):
        cdef:
            Py_ssize_t replacementLength = len(values)
            Py_ssize_t sliceLength = predictSliceLength(start, stop, 1)

        if replacementLength > sliceLength:
            self.grow(self.length + (replacementLength - sliceLength))
        if replacementLength != sliceLength:
            memmove(self.data + start + replacementLength,
                    self.data + stop,
                    sizeof(short) * (self.length - stop))
            self.length += replacementLength - sliceLength

        cdef Py_ssize_t i
        cdef short _value
        if isinstance(values, ShortList):
            self.overwrite(values, start)
        else:
            for i in range(replacementLength):
                self.tryConversion(values[i], self.data + start + i)

    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values):
        cdef Py_ssize_t sliceLength = predictSliceLength(start, stop, step)
        if sliceLength != len(values):
            raise ValueError("attempt to assign sequence of size {} to extended slice of size {}"
                             .format(len(values), sliceLength))

        # TODO: Speedup for specific list types + use while loop
        # range does not efficiently work with a variable step
        cdef Py_ssize_t i
        for i, value in zip(range(start, stop, step), values):
            self.tryConversion(value, self.data + i)

    cdef removeValuesInSlice(self, slice sliceObject):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))
        cdef Py_ssize_t removeAmount = removeValuesInSlice(
                      arrayStart = <char*>self.data,
                      arrayLength = self.length * sizeof(short),
                      elementSize = sizeof(short),
                      start = start, stop = stop, step = step)
        self.length -= removeAmount


    # Create new lists based on an existing list
    ###############################################

    cpdef ShortList reversed(self):
        cdef:
            ShortList newList = ShortList(self.length)
            Py_ssize_t i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def repeated(self, *, Py_ssize_t length = -1, Py_ssize_t amount = -1):
        if length < 0 and amount < 0:
            raise ValueError("Specify the 'length' or 'amount' parameter as keyword")
        elif length > 0 and amount > 0:
            raise ValueError("Can only evaluate one parameter of 'length' and 'amount'")

        if amount >= 0:
            length = self.length * amount

        if self.length == 0 and length > 0:
            raise ValueError("Cannot repeat a list with zero elements to something longer")

        cdef:
            ShortList newList = ShortList(length)
            Py_ssize_t copyAmount = length // self.length
            Py_ssize_t i

        # Full copy as often as possible
        for i in range(copyAmount):
            memcpy(newList.data + i * self.length,
                   self.data,
                   sizeof(short) * self.length)
        # Partial copy at the end
        memcpy(newList.data + self.length * copyAmount,
               self.data,
               sizeof(short) * (length % self.length))
        return newList


    # Low level utilities
    ###############################################

    cdef tryConversion(self, value, short* target):
        target[0] = value

    cdef tryCorrectIndex(self, Py_ssize_t index):
        if index < 0:
            index += self.length
        if index < 0 or index >= self.length:
            raise IndexError("list index out of range")
        return index

    cdef overwrite(self, ShortList other, Py_ssize_t index = 0):
        if self.capacity <= index + other.length:
            self.grow(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(short))
        self.length = max(self.length, index + other.length)

    cdef overwriteArray(self, short* array, Py_ssize_t arrayLength, Py_ssize_t index):
        if self.capacity <= index + arrayLength:
            self.grow(index + arrayLength)
        memcpy(self.data + index, array, arrayLength * sizeof(short))
        self.length = max(self.length, index + arrayLength)


    # Memory Views
    ###############################################

    cpdef getMemoryView(self):
        if "short" == "None":
            raise NotImplementedError("Cannot create memoryview for this type")

        cdef short[:] memview
        if self.length > 0:
            memview = <short[:self.length]>self.data
        else:
            # hack to make zero-length memview possible
            memview = (<short[:1]>self.data)[1:]
        return memview


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def join(cls, *sourceLists):
        cdef Py_ssize_t newLength = 0
        cdef Py_ssize_t offset = 0
        cdef ShortList source

        for source in sourceLists:
            newLength += len(source)
        newList = ShortList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, values):
        if isinstance(values, (list, tuple)):
            return cls.fromListOrTuple(values)

        try:
            from . convert import toShortList
            return toShortList(values)
        except TypeError: pass

        cdef ShortList newList = ShortList()
        newList.extend(values)
        return newList

    @classmethod
    def fromListOrTuple(cls, list_or_tuple values):
        cdef ShortList newList = ShortList(len(values))
        cdef Py_ssize_t i
        for i, value in enumerate(values):
            newList.tryConversion(value, newList.data + i)
        return newList


    # String Representations
    ###############################################

    def __repr__(self):
        if self.length < 20:
            return "<ShortList [{}]>".format(", ".join(str(self[i]) for i in range(self.length)))
        else:
            return "<ShortList [{}, ...]>".format(", ".join(str(self[i]) for i in range(20)))

    def status(self):
        return "Length: {}, Capacity: {}, Size: {} bytes".format(
            self.length, self.capacity, self.capacity * sizeof(short))


cdef class ShortListIterator:
    '''
    Implements the 'Iterator Protocol' that is used to allow iteration
    over a custom list object (eg with a for loop).
    An instance of this class is only created in the __iter__ method
    of the corresponding list type.
    https://docs.python.org/3.5/library/stdtypes.html#iterator-types
    '''
    cdef:
        ShortList source
        Py_ssize_t current

    def __cinit__(self, ShortList source):
        self.source = source
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef short currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue


cimport cython
from types import GeneratorType
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy, memmove, memcmp
from . utils cimport predictSliceLength, makeStepPositive, removeValuesInSlice, getValuesInSlice

@cython.freelist(10)
cdef class UShortList:

    # Initialization and Memory Management
    ###############################################

    def __cinit__(self, Py_ssize_t length = 0, Py_ssize_t capacity = -1):
        '''
        Initialize a new object with the given length.
        You can also directly allocate more memory from the beginning
        to allow faster appending/extending without memory reallocation.
        '''
        if length < 0:
            raise ValueError("Length has to be >= 0")
        if capacity < length:
            capacity = length
        self.data = <unsigned short*>malloc(sizeof(unsigned short) * capacity)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.capacity = capacity

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef grow(self, Py_ssize_t minCapacity):
        if minCapacity < self.capacity:
            return

        cdef Py_ssize_t newCapacity = minCapacity * 2 + 1
        self.data = <unsigned short*>realloc(self.data, sizeof(unsigned short) * newCapacity)
        if self.data == NULL:
            self.length = 0
            self.capacity = 0
            raise MemoryError()
        self.capacity = newCapacity

    cdef void shrinkToLength(self):
        cdef Py_ssize_t newCapacity = max(1, self.length)
        self.data = <unsigned short*>realloc(self.data, sizeof(unsigned short) * newCapacity)
        self.capacity = newCapacity

    cdef replaceArray(self, unsigned short* newData, Py_ssize_t newLength, Py_ssize_t newCapacity):
        free(self.data)
        self.data = newData
        self.length = newLength
        self.capacity = newCapacity


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getValueAtIndex(key)
        elif isinstance(key, slice):
            return self.getValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.setValueAtIndex(key, value)
        elif isinstance(key, slice):
            self.setValuesInSlice(key, value)
        else:
            raise TypeError("Expected int or slice object")

    def __delitem__(self, key):
        if isinstance(key, int):
            self.removeValueAtIndex(key)
        elif isinstance(key, slice):
            self.removeValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __add__(a, b):
        cdef UShortList newList
        try:
            newList = UShortList(capacity = len(a) + len(b))
            newList.extend(a)
            newList.extend(b)
        except:
            raise NotImplementedError()
        return newList

    def __mul__(UShortList self, Py_ssize_t amount):
        return self.repeated(amount = amount)

    def __iadd__(UShortList self, other):
        try:
            self.extend(other)
        except:
            raise NotImplementedError()
        return self

    def __iter__(self):
        return UShortListIterator(self)

    def __contains__(self, unsigned short value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    def __richcmp__(x, y, int operation):
        if operation == 2: # '=='
            if type(x) == type(y):
                return (<UShortList>x).equals_SameType(y)
            if len(x) == len(y):
                return all(a == b for a, b in zip(x, y))
            return False
        raise NotImplemented()

    cdef equals_SameType(self, UShortList other):
        if self.length != other.length:
            return False
        cdef Py_ssize_t i
        for i in range(self.length):
            if not self.data[i] == other.data[i]: return False
        return True


    # Base operations for lists - mimic python list
    ###############################################

    cpdef copy(self):
        newList = UShortList(self.length)
        newList.overwrite(self)
        return newList

    cpdef clear(self):
        self.length = 0
        self.shrinkToLength()

    cpdef fill(self, value):
        cdef Py_ssize_t i
        cdef unsigned short _value
        self.tryConversion(value, &_value)
        for i in range(self.length):
            self.data[i] = _value

    cpdef append(self, value):
        if self.length >= self.capacity:
            self.grow(self.length + 1)
        self.tryConversion(value, self.data + self.length)
        self.length += 1

    cpdef extend(self, values):
        cdef Py_ssize_t oldLength, newLength, i
        if isinstance(values, UShortList):
            self.overwrite(values, self.length)
        elif isinstance(values, list):
            self.extendList(values)
        elif isinstance(values, tuple):
            self.extendTuple(values)
        elif hasattr(values, "__len__"):
            newLength = self.length + len(values)
            self.grow(newLength)
            for i, value in enumerate(values, start = self.length):
                self.tryConversion(value, self.data + i)
            self.length = newLength
        else:
            try:
                oldLength = self.length
                for value in values:
                    self.append(value)
            except:
                self.length = oldLength
                raise TypeError("invalid input")

    cdef extendList(self, list values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cdef extendTuple(self, tuple values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cpdef index(self, value):
        cdef unsigned short _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t index = self.searchIndex(_value)
        if index >= 0: return index
        raise ValueError("value not in list")

    cdef Py_ssize_t searchIndex(self, unsigned short value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef count(self, value):
        cdef unsigned short _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t i
        cdef Py_ssize_t amount = 0
        for i in range(self.length):
            if self.data[i] == _value:
                amount += 1
        return amount

    cpdef remove(self, value):
        cdef Py_ssize_t index = self.searchIndex(value)
        if index == -1:
            raise ValueError("value not in list")
        else:
            self.removeValueAtIndex(index)

    cpdef insert(self, Py_ssize_t index, value):
        cdef unsigned short _value
        if index >= self.length:
            self.append(value)
        else:
            self.tryConversion(value, &_value)
            self.grow(self.length + 1)
            if index < 0: index += self.length
            if index < 0: index = 0
            memmove(self.data + index + 1,
                    self.data + index,
                    sizeof(unsigned short) * (self.length - index))
            self.data[index] = _value
            self.length += 1



    # Get/Set/Remove single element
    ################################################

    cdef getValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        return self.data[index]

    cdef setValueAtIndex(self, Py_ssize_t index, unsigned short value):
        index = self.tryCorrectIndex(index)
        self.data[index] = value

    cdef removeValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        memmove(self.data + index,
                self.data + index + 1,
                (self.length - index) * sizeof(unsigned short))
        self.length -= 1


    # Get/Set/Remove elements in slice
    ################################################

    cdef UShortList getValuesInSlice(self, slice sliceObject):
        cdef:
            void* newArray
            Py_ssize_t newLength
            UShortList newList

        getValuesInSlice(self.data, self.length, sizeof(unsigned short),
                         &newArray, &newLength, sliceObject)

        newList = UShortList()
        newList.replaceArray(<unsigned short*>newArray, newLength, newLength)
        return newList

    cdef setValuesInSlice(self, slice sliceObject, values):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))

        if step == 1:
            self.setValuesInSimpleSlice(start, stop, values)
        else:
            self.setValuesInExtendedSlice(start, stop, step, values)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values):
        cdef:
            Py_ssize_t replacementLength = len(values)
            Py_ssize_t sliceLength = predictSliceLength(start, stop, 1)

        if replacementLength > sliceLength:
            self.grow(self.length + (replacementLength - sliceLength))
        if replacementLength != sliceLength:
            memmove(self.data + start + replacementLength,
                    self.data + stop,
                    sizeof(unsigned short) * (self.length - stop))
            self.length += replacementLength - sliceLength

        cdef Py_ssize_t i
        cdef unsigned short _value
        if isinstance(values, UShortList):
            self.overwrite(values, start)
        else:
            for i in range(replacementLength):
                self.tryConversion(values[i], self.data + start + i)

    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values):
        cdef Py_ssize_t sliceLength = predictSliceLength(start, stop, step)
        if sliceLength != len(values):
            raise ValueError("attempt to assign sequence of size {} to extended slice of size {}"
                             .format(len(values), sliceLength))

        # TODO: Speedup for specific list types + use while loop
        # range does not efficiently work with a variable step
        cdef Py_ssize_t i
        for i, value in zip(range(start, stop, step), values):
            self.tryConversion(value, self.data + i)

    cdef removeValuesInSlice(self, slice sliceObject):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))
        cdef Py_ssize_t removeAmount = removeValuesInSlice(
                      arrayStart = <char*>self.data,
                      arrayLength = self.length * sizeof(unsigned short),
                      elementSize = sizeof(unsigned short),
                      start = start, stop = stop, step = step)
        self.length -= removeAmount


    # Create new lists based on an existing list
    ###############################################

    cpdef UShortList reversed(self):
        cdef:
            UShortList newList = UShortList(self.length)
            Py_ssize_t i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def repeated(self, *, Py_ssize_t length = -1, Py_ssize_t amount = -1):
        if length < 0 and amount < 0:
            raise ValueError("Specify the 'length' or 'amount' parameter as keyword")
        elif length > 0 and amount > 0:
            raise ValueError("Can only evaluate one parameter of 'length' and 'amount'")

        if amount >= 0:
            length = self.length * amount

        if self.length == 0 and length > 0:
            raise ValueError("Cannot repeat a list with zero elements to something longer")

        cdef:
            UShortList newList = UShortList(length)
            Py_ssize_t copyAmount = length // self.length
            Py_ssize_t i

        # Full copy as often as possible
        for i in range(copyAmount):
            memcpy(newList.data + i * self.length,
                   self.data,
                   sizeof(unsigned short) * self.length)
        # Partial copy at the end
        memcpy(newList.data + self.length * copyAmount,
               self.data,
               sizeof(unsigned short) * (length % self.length))
        return newList


    # Low level utilities
    ###############################################

    cdef tryConversion(self, value, unsigned short* target):
        target[0] = value

    cdef tryCorrectIndex(self, Py_ssize_t index):
        if index < 0:
            index += self.length
        if index < 0 or index >= self.length:
            raise IndexError("list index out of range")
        return index

    cdef overwrite(self, UShortList other, Py_ssize_t index = 0):
        if self.capacity <= index + other.length:
            self.grow(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(unsigned short))
        self.length = max(self.length, index + other.length)

    cdef overwriteArray(self, unsigned short* array, Py_ssize_t arrayLength, Py_ssize_t index):
        if self.capacity <= index + arrayLength:
            self.grow(index + arrayLength)
        memcpy(self.data + index, array, arrayLength * sizeof(unsigned short))
        self.length = max(self.length, index + arrayLength)


    # Memory Views
    ###############################################

    cpdef getMemoryView(self):
        if "unsigned short" == "None":
            raise NotImplementedError("Cannot create memoryview for this type")

        cdef unsigned short[:] memview
        if self.length > 0:
            memview = <unsigned short[:self.length]>self.data
        else:
            # hack to make zero-length memview possible
            memview = (<unsigned short[:1]>self.data)[1:]
        return memview


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def join(cls, *sourceLists):
        cdef Py_ssize_t newLength = 0
        cdef Py_ssize_t offset = 0
        cdef UShortList source

        for source in sourceLists:
            newLength += len(source)
        newList = UShortList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, values):
        if isinstance(values, (list, tuple)):
            return cls.fromListOrTuple(values)

        try:
            from . convert import toUShortList
            return toUShortList(values)
        except TypeError: pass

        cdef UShortList newList = UShortList()
        newList.extend(values)
        return newList

    @classmethod
    def fromListOrTuple(cls, list_or_tuple values):
        cdef UShortList newList = UShortList(len(values))
        cdef Py_ssize_t i
        for i, value in enumerate(values):
            newList.tryConversion(value, newList.data + i)
        return newList


    # String Representations
    ###############################################

    def __repr__(self):
        if self.length < 20:
            return "<UShortList [{}]>".format(", ".join(str(self[i]) for i in range(self.length)))
        else:
            return "<UShortList [{}, ...]>".format(", ".join(str(self[i]) for i in range(20)))

    def status(self):
        return "Length: {}, Capacity: {}, Size: {} bytes".format(
            self.length, self.capacity, self.capacity * sizeof(unsigned short))


cdef class UShortListIterator:
    '''
    Implements the 'Iterator Protocol' that is used to allow iteration
    over a custom list object (eg with a for loop).
    An instance of this class is only created in the __iter__ method
    of the corresponding list type.
    https://docs.python.org/3.5/library/stdtypes.html#iterator-types
    '''
    cdef:
        UShortList source
        Py_ssize_t current

    def __cinit__(self, UShortList source):
        self.source = source
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef unsigned short currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue


cimport cython
from types import GeneratorType
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy, memmove, memcmp
from . utils cimport predictSliceLength, makeStepPositive, removeValuesInSlice, getValuesInSlice

@cython.freelist(10)
cdef class LongLongList:

    # Initialization and Memory Management
    ###############################################

    def __cinit__(self, Py_ssize_t length = 0, Py_ssize_t capacity = -1):
        '''
        Initialize a new object with the given length.
        You can also directly allocate more memory from the beginning
        to allow faster appending/extending without memory reallocation.
        '''
        if length < 0:
            raise ValueError("Length has to be >= 0")
        if capacity < length:
            capacity = length
        self.data = <long long*>malloc(sizeof(long long) * capacity)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.capacity = capacity

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef grow(self, Py_ssize_t minCapacity):
        if minCapacity < self.capacity:
            return

        cdef Py_ssize_t newCapacity = minCapacity * 2 + 1
        self.data = <long long*>realloc(self.data, sizeof(long long) * newCapacity)
        if self.data == NULL:
            self.length = 0
            self.capacity = 0
            raise MemoryError()
        self.capacity = newCapacity

    cdef void shrinkToLength(self):
        cdef Py_ssize_t newCapacity = max(1, self.length)
        self.data = <long long*>realloc(self.data, sizeof(long long) * newCapacity)
        self.capacity = newCapacity

    cdef replaceArray(self, long long* newData, Py_ssize_t newLength, Py_ssize_t newCapacity):
        free(self.data)
        self.data = newData
        self.length = newLength
        self.capacity = newCapacity


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getValueAtIndex(key)
        elif isinstance(key, slice):
            return self.getValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.setValueAtIndex(key, value)
        elif isinstance(key, slice):
            self.setValuesInSlice(key, value)
        else:
            raise TypeError("Expected int or slice object")

    def __delitem__(self, key):
        if isinstance(key, int):
            self.removeValueAtIndex(key)
        elif isinstance(key, slice):
            self.removeValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __add__(a, b):
        cdef LongLongList newList
        try:
            newList = LongLongList(capacity = len(a) + len(b))
            newList.extend(a)
            newList.extend(b)
        except:
            raise NotImplementedError()
        return newList

    def __mul__(LongLongList self, Py_ssize_t amount):
        return self.repeated(amount = amount)

    def __iadd__(LongLongList self, other):
        try:
            self.extend(other)
        except:
            raise NotImplementedError()
        return self

    def __iter__(self):
        return LongLongListIterator(self)

    def __contains__(self, long long value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    def __richcmp__(x, y, int operation):
        if operation == 2: # '=='
            if type(x) == type(y):
                return (<LongLongList>x).equals_SameType(y)
            if len(x) == len(y):
                return all(a == b for a, b in zip(x, y))
            return False
        raise NotImplemented()

    cdef equals_SameType(self, LongLongList other):
        if self.length != other.length:
            return False
        cdef Py_ssize_t i
        for i in range(self.length):
            if not self.data[i] == other.data[i]: return False
        return True


    # Base operations for lists - mimic python list
    ###############################################

    cpdef copy(self):
        newList = LongLongList(self.length)
        newList.overwrite(self)
        return newList

    cpdef clear(self):
        self.length = 0
        self.shrinkToLength()

    cpdef fill(self, value):
        cdef Py_ssize_t i
        cdef long long _value
        self.tryConversion(value, &_value)
        for i in range(self.length):
            self.data[i] = _value

    cpdef append(self, value):
        if self.length >= self.capacity:
            self.grow(self.length + 1)
        self.tryConversion(value, self.data + self.length)
        self.length += 1

    cpdef extend(self, values):
        cdef Py_ssize_t oldLength, newLength, i
        if isinstance(values, LongLongList):
            self.overwrite(values, self.length)
        elif isinstance(values, list):
            self.extendList(values)
        elif isinstance(values, tuple):
            self.extendTuple(values)
        elif hasattr(values, "__len__"):
            newLength = self.length + len(values)
            self.grow(newLength)
            for i, value in enumerate(values, start = self.length):
                self.tryConversion(value, self.data + i)
            self.length = newLength
        else:
            try:
                oldLength = self.length
                for value in values:
                    self.append(value)
            except:
                self.length = oldLength
                raise TypeError("invalid input")

    cdef extendList(self, list values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cdef extendTuple(self, tuple values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cpdef index(self, value):
        cdef long long _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t index = self.searchIndex(_value)
        if index >= 0: return index
        raise ValueError("value not in list")

    cdef Py_ssize_t searchIndex(self, long long value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef count(self, value):
        cdef long long _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t i
        cdef Py_ssize_t amount = 0
        for i in range(self.length):
            if self.data[i] == _value:
                amount += 1
        return amount

    cpdef remove(self, value):
        cdef Py_ssize_t index = self.searchIndex(value)
        if index == -1:
            raise ValueError("value not in list")
        else:
            self.removeValueAtIndex(index)

    cpdef insert(self, Py_ssize_t index, value):
        cdef long long _value
        if index >= self.length:
            self.append(value)
        else:
            self.tryConversion(value, &_value)
            self.grow(self.length + 1)
            if index < 0: index += self.length
            if index < 0: index = 0
            memmove(self.data + index + 1,
                    self.data + index,
                    sizeof(long long) * (self.length - index))
            self.data[index] = _value
            self.length += 1



    # Get/Set/Remove single element
    ################################################

    cdef getValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        return self.data[index]

    cdef setValueAtIndex(self, Py_ssize_t index, long long value):
        index = self.tryCorrectIndex(index)
        self.data[index] = value

    cdef removeValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        memmove(self.data + index,
                self.data + index + 1,
                (self.length - index) * sizeof(long long))
        self.length -= 1


    # Get/Set/Remove elements in slice
    ################################################

    cdef LongLongList getValuesInSlice(self, slice sliceObject):
        cdef:
            void* newArray
            Py_ssize_t newLength
            LongLongList newList

        getValuesInSlice(self.data, self.length, sizeof(long long),
                         &newArray, &newLength, sliceObject)

        newList = LongLongList()
        newList.replaceArray(<long long*>newArray, newLength, newLength)
        return newList

    cdef setValuesInSlice(self, slice sliceObject, values):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))

        if step == 1:
            self.setValuesInSimpleSlice(start, stop, values)
        else:
            self.setValuesInExtendedSlice(start, stop, step, values)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values):
        cdef:
            Py_ssize_t replacementLength = len(values)
            Py_ssize_t sliceLength = predictSliceLength(start, stop, 1)

        if replacementLength > sliceLength:
            self.grow(self.length + (replacementLength - sliceLength))
        if replacementLength != sliceLength:
            memmove(self.data + start + replacementLength,
                    self.data + stop,
                    sizeof(long long) * (self.length - stop))
            self.length += replacementLength - sliceLength

        cdef Py_ssize_t i
        cdef long long _value
        if isinstance(values, LongLongList):
            self.overwrite(values, start)
        else:
            for i in range(replacementLength):
                self.tryConversion(values[i], self.data + start + i)

    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values):
        cdef Py_ssize_t sliceLength = predictSliceLength(start, stop, step)
        if sliceLength != len(values):
            raise ValueError("attempt to assign sequence of size {} to extended slice of size {}"
                             .format(len(values), sliceLength))

        # TODO: Speedup for specific list types + use while loop
        # range does not efficiently work with a variable step
        cdef Py_ssize_t i
        for i, value in zip(range(start, stop, step), values):
            self.tryConversion(value, self.data + i)

    cdef removeValuesInSlice(self, slice sliceObject):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))
        cdef Py_ssize_t removeAmount = removeValuesInSlice(
                      arrayStart = <char*>self.data,
                      arrayLength = self.length * sizeof(long long),
                      elementSize = sizeof(long long),
                      start = start, stop = stop, step = step)
        self.length -= removeAmount


    # Create new lists based on an existing list
    ###############################################

    cpdef LongLongList reversed(self):
        cdef:
            LongLongList newList = LongLongList(self.length)
            Py_ssize_t i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def repeated(self, *, Py_ssize_t length = -1, Py_ssize_t amount = -1):
        if length < 0 and amount < 0:
            raise ValueError("Specify the 'length' or 'amount' parameter as keyword")
        elif length > 0 and amount > 0:
            raise ValueError("Can only evaluate one parameter of 'length' and 'amount'")

        if amount >= 0:
            length = self.length * amount

        if self.length == 0 and length > 0:
            raise ValueError("Cannot repeat a list with zero elements to something longer")

        cdef:
            LongLongList newList = LongLongList(length)
            Py_ssize_t copyAmount = length // self.length
            Py_ssize_t i

        # Full copy as often as possible
        for i in range(copyAmount):
            memcpy(newList.data + i * self.length,
                   self.data,
                   sizeof(long long) * self.length)
        # Partial copy at the end
        memcpy(newList.data + self.length * copyAmount,
               self.data,
               sizeof(long long) * (length % self.length))
        return newList


    # Low level utilities
    ###############################################

    cdef tryConversion(self, value, long long* target):
        target[0] = value

    cdef tryCorrectIndex(self, Py_ssize_t index):
        if index < 0:
            index += self.length
        if index < 0 or index >= self.length:
            raise IndexError("list index out of range")
        return index

    cdef overwrite(self, LongLongList other, Py_ssize_t index = 0):
        if self.capacity <= index + other.length:
            self.grow(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(long long))
        self.length = max(self.length, index + other.length)

    cdef overwriteArray(self, long long* array, Py_ssize_t arrayLength, Py_ssize_t index):
        if self.capacity <= index + arrayLength:
            self.grow(index + arrayLength)
        memcpy(self.data + index, array, arrayLength * sizeof(long long))
        self.length = max(self.length, index + arrayLength)


    # Memory Views
    ###############################################

    cpdef getMemoryView(self):
        if "long long" == "None":
            raise NotImplementedError("Cannot create memoryview for this type")

        cdef long long[:] memview
        if self.length > 0:
            memview = <long long[:self.length]>self.data
        else:
            # hack to make zero-length memview possible
            memview = (<long long[:1]>self.data)[1:]
        return memview


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def join(cls, *sourceLists):
        cdef Py_ssize_t newLength = 0
        cdef Py_ssize_t offset = 0
        cdef LongLongList source

        for source in sourceLists:
            newLength += len(source)
        newList = LongLongList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, values):
        if isinstance(values, (list, tuple)):
            return cls.fromListOrTuple(values)

        try:
            from . convert import toLongLongList
            return toLongLongList(values)
        except TypeError: pass

        cdef LongLongList newList = LongLongList()
        newList.extend(values)
        return newList

    @classmethod
    def fromListOrTuple(cls, list_or_tuple values):
        cdef LongLongList newList = LongLongList(len(values))
        cdef Py_ssize_t i
        for i, value in enumerate(values):
            newList.tryConversion(value, newList.data + i)
        return newList


    # String Representations
    ###############################################

    def __repr__(self):
        if self.length < 20:
            return "<LongLongList [{}]>".format(", ".join(str(self[i]) for i in range(self.length)))
        else:
            return "<LongLongList [{}, ...]>".format(", ".join(str(self[i]) for i in range(20)))

    def status(self):
        return "Length: {}, Capacity: {}, Size: {} bytes".format(
            self.length, self.capacity, self.capacity * sizeof(long long))


cdef class LongLongListIterator:
    '''
    Implements the 'Iterator Protocol' that is used to allow iteration
    over a custom list object (eg with a for loop).
    An instance of this class is only created in the __iter__ method
    of the corresponding list type.
    https://docs.python.org/3.5/library/stdtypes.html#iterator-types
    '''
    cdef:
        LongLongList source
        Py_ssize_t current

    def __cinit__(self, LongLongList source):
        self.source = source
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef long long currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue


cimport cython
from types import GeneratorType
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy, memmove, memcmp
from . utils cimport predictSliceLength, makeStepPositive, removeValuesInSlice, getValuesInSlice

@cython.freelist(10)
cdef class ULongLongList:

    # Initialization and Memory Management
    ###############################################

    def __cinit__(self, Py_ssize_t length = 0, Py_ssize_t capacity = -1):
        '''
        Initialize a new object with the given length.
        You can also directly allocate more memory from the beginning
        to allow faster appending/extending without memory reallocation.
        '''
        if length < 0:
            raise ValueError("Length has to be >= 0")
        if capacity < length:
            capacity = length
        self.data = <unsigned long long*>malloc(sizeof(unsigned long long) * capacity)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.capacity = capacity

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef grow(self, Py_ssize_t minCapacity):
        if minCapacity < self.capacity:
            return

        cdef Py_ssize_t newCapacity = minCapacity * 2 + 1
        self.data = <unsigned long long*>realloc(self.data, sizeof(unsigned long long) * newCapacity)
        if self.data == NULL:
            self.length = 0
            self.capacity = 0
            raise MemoryError()
        self.capacity = newCapacity

    cdef void shrinkToLength(self):
        cdef Py_ssize_t newCapacity = max(1, self.length)
        self.data = <unsigned long long*>realloc(self.data, sizeof(unsigned long long) * newCapacity)
        self.capacity = newCapacity

    cdef replaceArray(self, unsigned long long* newData, Py_ssize_t newLength, Py_ssize_t newCapacity):
        free(self.data)
        self.data = newData
        self.length = newLength
        self.capacity = newCapacity


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getValueAtIndex(key)
        elif isinstance(key, slice):
            return self.getValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.setValueAtIndex(key, value)
        elif isinstance(key, slice):
            self.setValuesInSlice(key, value)
        else:
            raise TypeError("Expected int or slice object")

    def __delitem__(self, key):
        if isinstance(key, int):
            self.removeValueAtIndex(key)
        elif isinstance(key, slice):
            self.removeValuesInSlice(key)
        else:
            raise TypeError("Expected int or slice object")

    def __add__(a, b):
        cdef ULongLongList newList
        try:
            newList = ULongLongList(capacity = len(a) + len(b))
            newList.extend(a)
            newList.extend(b)
        except:
            raise NotImplementedError()
        return newList

    def __mul__(ULongLongList self, Py_ssize_t amount):
        return self.repeated(amount = amount)

    def __iadd__(ULongLongList self, other):
        try:
            self.extend(other)
        except:
            raise NotImplementedError()
        return self

    def __iter__(self):
        return ULongLongListIterator(self)

    def __contains__(self, unsigned long long value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    def __richcmp__(x, y, int operation):
        if operation == 2: # '=='
            if type(x) == type(y):
                return (<ULongLongList>x).equals_SameType(y)
            if len(x) == len(y):
                return all(a == b for a, b in zip(x, y))
            return False
        raise NotImplemented()

    cdef equals_SameType(self, ULongLongList other):
        if self.length != other.length:
            return False
        cdef Py_ssize_t i
        for i in range(self.length):
            if not self.data[i] == other.data[i]: return False
        return True


    # Base operations for lists - mimic python list
    ###############################################

    cpdef copy(self):
        newList = ULongLongList(self.length)
        newList.overwrite(self)
        return newList

    cpdef clear(self):
        self.length = 0
        self.shrinkToLength()

    cpdef fill(self, value):
        cdef Py_ssize_t i
        cdef unsigned long long _value
        self.tryConversion(value, &_value)
        for i in range(self.length):
            self.data[i] = _value

    cpdef append(self, value):
        if self.length >= self.capacity:
            self.grow(self.length + 1)
        self.tryConversion(value, self.data + self.length)
        self.length += 1

    cpdef extend(self, values):
        cdef Py_ssize_t oldLength, newLength, i
        if isinstance(values, ULongLongList):
            self.overwrite(values, self.length)
        elif isinstance(values, list):
            self.extendList(values)
        elif isinstance(values, tuple):
            self.extendTuple(values)
        elif hasattr(values, "__len__"):
            newLength = self.length + len(values)
            self.grow(newLength)
            for i, value in enumerate(values, start = self.length):
                self.tryConversion(value, self.data + i)
            self.length = newLength
        else:
            try:
                oldLength = self.length
                for value in values:
                    self.append(value)
            except:
                self.length = oldLength
                raise TypeError("invalid input")

    cdef extendList(self, list values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cdef extendTuple(self, tuple values):
        cdef Py_ssize_t newLength, i
        newLength = self.length + len(values)
        self.grow(newLength)
        for i in range(len(values)):
            self.tryConversion(values[i], self.data + self.length + i)
        self.length = newLength

    cpdef index(self, value):
        cdef unsigned long long _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t index = self.searchIndex(_value)
        if index >= 0: return index
        raise ValueError("value not in list")

    cdef Py_ssize_t searchIndex(self, unsigned long long value):
        cdef Py_ssize_t i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef count(self, value):
        cdef unsigned long long _value
        self.tryConversion(value, &_value)
        cdef Py_ssize_t i
        cdef Py_ssize_t amount = 0
        for i in range(self.length):
            if self.data[i] == _value:
                amount += 1
        return amount

    cpdef remove(self, value):
        cdef Py_ssize_t index = self.searchIndex(value)
        if index == -1:
            raise ValueError("value not in list")
        else:
            self.removeValueAtIndex(index)

    cpdef insert(self, Py_ssize_t index, value):
        cdef unsigned long long _value
        if index >= self.length:
            self.append(value)
        else:
            self.tryConversion(value, &_value)
            self.grow(self.length + 1)
            if index < 0: index += self.length
            if index < 0: index = 0
            memmove(self.data + index + 1,
                    self.data + index,
                    sizeof(unsigned long long) * (self.length - index))
            self.data[index] = _value
            self.length += 1



    # Get/Set/Remove single element
    ################################################

    cdef getValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        return self.data[index]

    cdef setValueAtIndex(self, Py_ssize_t index, unsigned long long value):
        index = self.tryCorrectIndex(index)
        self.data[index] = value

    cdef removeValueAtIndex(self, Py_ssize_t index):
        index = self.tryCorrectIndex(index)
        memmove(self.data + index,
                self.data + index + 1,
                (self.length - index) * sizeof(unsigned long long))
        self.length -= 1


    # Get/Set/Remove elements in slice
    ################################################

    cdef ULongLongList getValuesInSlice(self, slice sliceObject):
        cdef:
            void* newArray
            Py_ssize_t newLength
            ULongLongList newList

        getValuesInSlice(self.data, self.length, sizeof(unsigned long long),
                         &newArray, &newLength, sliceObject)

        newList = ULongLongList()
        newList.replaceArray(<unsigned long long*>newArray, newLength, newLength)
        return newList

    cdef setValuesInSlice(self, slice sliceObject, values):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))

        if step == 1:
            self.setValuesInSimpleSlice(start, stop, values)
        else:
            self.setValuesInExtendedSlice(start, stop, step, values)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values):
        cdef:
            Py_ssize_t replacementLength = len(values)
            Py_ssize_t sliceLength = predictSliceLength(start, stop, 1)

        if replacementLength > sliceLength:
            self.grow(self.length + (replacementLength - sliceLength))
        if replacementLength != sliceLength:
            memmove(self.data + start + replacementLength,
                    self.data + stop,
                    sizeof(unsigned long long) * (self.length - stop))
            self.length += replacementLength - sliceLength

        cdef Py_ssize_t i
        cdef unsigned long long _value
        if isinstance(values, ULongLongList):
            self.overwrite(values, start)
        else:
            for i in range(replacementLength):
                self.tryConversion(values[i], self.data + start + i)

    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values):
        cdef Py_ssize_t sliceLength = predictSliceLength(start, stop, step)
        if sliceLength != len(values):
            raise ValueError("attempt to assign sequence of size {} to extended slice of size {}"
                             .format(len(values), sliceLength))

        # TODO: Speedup for specific list types + use while loop
        # range does not efficiently work with a variable step
        cdef Py_ssize_t i
        for i, value in zip(range(start, stop, step), values):
            self.tryConversion(value, self.data + i)

    cdef removeValuesInSlice(self, slice sliceObject):
        cdef Py_ssize_t start, stop, step
        start, stop, step = sliceObject.indices(len(self))
        cdef Py_ssize_t removeAmount = removeValuesInSlice(
                      arrayStart = <char*>self.data,
                      arrayLength = self.length * sizeof(unsigned long long),
                      elementSize = sizeof(unsigned long long),
                      start = start, stop = stop, step = step)
        self.length -= removeAmount


    # Create new lists based on an existing list
    ###############################################

    cpdef ULongLongList reversed(self):
        cdef:
            ULongLongList newList = ULongLongList(self.length)
            Py_ssize_t i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def repeated(self, *, Py_ssize_t length = -1, Py_ssize_t amount = -1):
        if length < 0 and amount < 0:
            raise ValueError("Specify the 'length' or 'amount' parameter as keyword")
        elif length > 0 and amount > 0:
            raise ValueError("Can only evaluate one parameter of 'length' and 'amount'")

        if amount >= 0:
            length = self.length * amount

        if self.length == 0 and length > 0:
            raise ValueError("Cannot repeat a list with zero elements to something longer")

        cdef:
            ULongLongList newList = ULongLongList(length)
            Py_ssize_t copyAmount = length // self.length
            Py_ssize_t i

        # Full copy as often as possible
        for i in range(copyAmount):
            memcpy(newList.data + i * self.length,
                   self.data,
                   sizeof(unsigned long long) * self.length)
        # Partial copy at the end
        memcpy(newList.data + self.length * copyAmount,
               self.data,
               sizeof(unsigned long long) * (length % self.length))
        return newList


    # Low level utilities
    ###############################################

    cdef tryConversion(self, value, unsigned long long* target):
        target[0] = value

    cdef tryCorrectIndex(self, Py_ssize_t index):
        if index < 0:
            index += self.length
        if index < 0 or index >= self.length:
            raise IndexError("list index out of range")
        return index

    cdef overwrite(self, ULongLongList other, Py_ssize_t index = 0):
        if self.capacity <= index + other.length:
            self.grow(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(unsigned long long))
        self.length = max(self.length, index + other.length)

    cdef overwriteArray(self, unsigned long long* array, Py_ssize_t arrayLength, Py_ssize_t index):
        if self.capacity <= index + arrayLength:
            self.grow(index + arrayLength)
        memcpy(self.data + index, array, arrayLength * sizeof(unsigned long long))
        self.length = max(self.length, index + arrayLength)


    # Memory Views
    ###############################################

    cpdef getMemoryView(self):
        if "unsigned long long" == "None":
            raise NotImplementedError("Cannot create memoryview for this type")

        cdef unsigned long long[:] memview
        if self.length > 0:
            memview = <unsigned long long[:self.length]>self.data
        else:
            # hack to make zero-length memview possible
            memview = (<unsigned long long[:1]>self.data)[1:]
        return memview


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def join(cls, *sourceLists):
        cdef Py_ssize_t newLength = 0
        cdef Py_ssize_t offset = 0
        cdef ULongLongList source

        for source in sourceLists:
            newLength += len(source)
        newList = ULongLongList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, values):
        if isinstance(values, (list, tuple)):
            return cls.fromListOrTuple(values)

        try:
            from . convert import toULongLongList
            return toULongLongList(values)
        except TypeError: pass

        cdef ULongLongList newList = ULongLongList()
        newList.extend(values)
        return newList

    @classmethod
    def fromListOrTuple(cls, list_or_tuple values):
        cdef ULongLongList newList = ULongLongList(len(values))
        cdef Py_ssize_t i
        for i, value in enumerate(values):
            newList.tryConversion(value, newList.data + i)
        return newList


    # String Representations
    ###############################################

    def __repr__(self):
        if self.length < 20:
            return "<ULongLongList [{}]>".format(", ".join(str(self[i]) for i in range(self.length)))
        else:
            return "<ULongLongList [{}, ...]>".format(", ".join(str(self[i]) for i in range(20)))

    def status(self):
        return "Length: {}, Capacity: {}, Size: {} bytes".format(
            self.length, self.capacity, self.capacity * sizeof(unsigned long long))


cdef class ULongLongListIterator:
    '''
    Implements the 'Iterator Protocol' that is used to allow iteration
    over a custom list object (eg with a for loop).
    An instance of this class is only created in the __iter__ method
    of the corresponding list type.
    https://docs.python.org/3.5/library/stdtypes.html#iterator-types
    '''
    cdef:
        ULongLongList source
        Py_ssize_t current

    def __cinit__(self, ULongLongList source):
        self.source = source
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef unsigned long long currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue
