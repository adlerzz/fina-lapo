class WritePointer:

    def __init__(self, pointer, new_value, new_size):
        self.__pointer = pointer
        self.__new_position = pointer.position
        self.__new_value = new_value
        self.__new_size = new_size

    @property
    def pointer(self):
        return self.__pointer

    @property
    def new_position(self):
        return self.__new_position

    @property
    def new_value(self):
        return self.__new_value

    @property
    def new_size(self):
        return self.__new_size

    def shift(self, offset):
        self.__new_position = self.__new_position + offset

    def offset(self):
        return self.new_size - self.pointer.size

    def __str__(self):
        body = ''
        if self.pointer.type == 'uint':
            body = body + '{{new_pos: {:X}, pt: {}, value: {}, size: {}}}' \
                .format(self.__new_position, self.pointer, self.new_value, self.new_size)
        elif self.pointer.type == 'utf16':
            body = body + '{{new_pos: {:X}, pt: {}, value: {}, size: {}}}'\
                    .format(self.__new_position, self.pointer, '$UTF16', self.new_size)
        else:
            body = body + '{{new_pos: {:X}, pt: {}, value: "{}", size: {}}}' \
                .format(self.__new_position, self.pointer, self.new_value, self.new_size)
        return '{}'.format(body)
