import codec
import utils


class Pointer:
    __value = None

    def __init__(self, position, size, type):
        self.__position = position
        self.__size = size
        self.__type = type

    @property
    def position(self):
        return self.__position

    def shift(self, offset):
        self.__position += offset

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        self.__size = size

    @property
    def type(self):
        return self.__type

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __str__(self):
        if self.type == 'utf16':
            length = utils.bytes_to_uint(self.value[:4])
            value = self.value[4:].decode(codec.UNICODE).rstrip('\x00')
            return "{{pos: {:X}, type: {}, size: {}, len: {}, value: \"{}\"}}" \
                .format(self.position, self.type, self.size, length, value)
        elif self.type == 'str':
            return "{{pos: {:X}, type: {}, size: {}, value: \"{}\"}}" \
                .format(self.position, self.type, self.size, self.value)
        else:
            return "{{pos: {:X}, type: {}, size: {}, value: {}}}"\
                .format(self.position, self.type, self.size, self.value)
