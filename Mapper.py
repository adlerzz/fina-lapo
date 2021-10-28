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
            pointer.value = utils.bytes_to_uint(raw)
        elif pointer.type == 'int':
            pointer.value = utils.bytes_to_int(raw)
        elif pointer.type == 'str':
            length = self.__content[p]
            raw = self.__content[p+1: p+length+1]
            pointer.value = utils.bytes_to_str(raw)
            size = utils.get_padded_length(pointer.value)
            pointer.size = size

        elif pointer.type == 'utf16':
            size = int.from_bytes(self.__content[p: p+4], codec.BYTE_ORDER) + 4
            pointer.size = size
            pointer.value = self.__content[p+4: p+size]
        self.__pointer = self.__pointer + size

    def read_bytes(self, size):
        p = self.__pointer
        res = self.__content[p: p + size]
        self.__pointer = p + size
        return res

    def read_uint16(self):
        abytes = self.read_bytes(2)
        return utils.bytes_to_uint(abytes)

    def read_int16(self):
        abytes = self.read_bytes(2)
        return utils.bytes_to_int(abytes)

    def read_uint32(self):
        abytes = self.read_bytes(4)
        return utils.bytes_to_uint(abytes)

    def write_pointer(self, wpointer):
        p = wpointer.new_position
        c = self.__content
        n = None
        if wpointer.type == 'uint':
            if wpointer.origin.size == 4:
                n = utils.uint32_to_bytes(wpointer.new_value)
        elif wpointer.type == 'str':
            new_len = utils.uint8_to_bytes(len(wpointer.new_value))
            new_str = utils.str_to_bytes(wpointer.new_value).ljust(wpointer.new_size - 1, b'\x00')
            n = new_len + new_str
        elif wpointer.type == 'utf16':
            new_len = utils.uint32_to_bytes(wpointer.new_size - 4)
            n = new_len + wpointer.new_value[4:]
        self.__content = c[:p] + n + c[p+wpointer.origin.size:]

    def move_on(self, offset):
        self.__pointer += offset

    def move_to(self, position):
        self.__pointer = position

    def where(self):
        return self.__pointer

    def save(self, save_as=None):
        filename = save_as if save_as is not None else self.__filename
        print(filename)
        with open(filename, "wb") as f:
            f.write(self.__content)
