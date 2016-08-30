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


    #cdef tryConversion(self, value, int* target):
    #    if TRY_CONVERT_TO_C(value, &_value) != 0:
    #        raise TypeError("Value cannot be element of IntegerList")

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
