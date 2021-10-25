import codec
import utils
from Pointer import *


class Mapper:

    def __init__(self, filename):
        self.__filename = filename
        with open(self.__filename, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(0, 0)
            self.__content = f.read(size)
        self.__pointer = 0

    def mark_uint8(self):
        p = Pointer(self.__pointer, 1, 'uint')
        self.read_pointer(p)
        return p

    def mark_uint32(self):
        p = Pointer(self.__pointer, 4, 'uint')
        self.read_pointer(p)
        return p

    def mark_str(self):
        p = Pointer(self.__pointer, 1, 'str')
        self.read_pointer(p)
        return p

    def mark_utf16(self):
        p = Pointer(self.__pointer, 4, 'utf16')
        self.read_pointer(p)
        return p

    def read_pointer(self, pointer):
        p = pointer.position
        size = pointer.size
        raw = self.__content[p:p + size]
        if pointer.type == 'uint':
            pointer.value = int.from_bytes(raw, 'big')
        elif pointer.type == 'int':
            pointer.value = int.from_bytes(raw, 'big', signed=True)
        elif pointer.type == 'str':
            length = self.__content[p]
            raw = self.__content[p+1: p+length+1]
            pointer.value = str(raw, encoding=codec.NO_UNICODE)
            size = utils.get_padded_length(pointer.value)
            pointer.size = size

        elif pointer.type == 'utf16':
            size = int.from_bytes(self.__content[p: p+4], 'big') + 4
            pointer.size = size
            pointer.value = self.__content[p+4: p+size]
        self.__pointer = self.__pointer + size

    def read_bytes(self, size):
        p = self.__pointer
        res = self.__content[p: p + size]
        self.__pointer = p + size
        return res

    def read_int(self, size, signed=False):
        abytes = self.read_bytes(size)
        res = int.from_bytes(abytes, 'big', signed=signed)
        return res

    def read_str(self, size):
        bytes = self.read_bytes(size)
        res = str(bytes, encoding=codec.NO_UNICODE)
        return res

    def write_bytes(self, value, instead=None):
        p = self.__pointer
        c = self.__content
        offset = instead if instead is not None else len(value)
        self.__content = c[:p] + value + c[p + offset:]
        self.__pointer = self.__pointer + len(value)

    def write_int(self, value, size):
        self.write_bytes(value.to_bytes(size, 'big'))

    def write_str(self, value, instead=None):
        b = bytes(value, codec.NO_UNICODE)
        self.write_bytes(b, instead)

    def write_pointer(self, pointer):
        p = pointer.new_position
        c = self.__content
        if pointer.pointer.type == 'uint':
            self.__content = c[:p] + pointer.new_value.to_bytes(pointer.new_size, 'big') + c[p+pointer.pointer.size:]
        elif pointer.pointer.type == 'str':
            nl = len(pointer.new_value).to_bytes(1, 'big')
            ns = bytes(pointer.new_value, codec.NO_UNICODE).ljust(pointer.new_size - 1, b'\x00')
            self.__content = c[:p] + nl + ns + c[p+pointer.pointer.size:]
        elif pointer.pointer.type == 'utf16':
            nl = (pointer.new_size - 4).to_bytes(4, 'big')
            self.__content = c[:p] + nl + pointer.new_value[4:] + c[p+pointer.pointer.size:]

    def move_on(self, offset):
        self.__pointer = self.__pointer + offset

    def move_to(self, position):
        self.__pointer = position

    def where(self):
        return self.__pointer

    def save(self, save_as=None):
        filename = save_as if save_as is not None else self.__filename
        print(filename)
        with open(filename, "wb") as f:
            f.write(self.__content)
