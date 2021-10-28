class WritePointer:

    def __init__(self, origin, new_value, new_size):
        self.__origin = origin
        self.__new_position = origin.position
        self.__new_value = new_value
        self.__new_size = new_size

    @property
    def origin(self):
        return self.__origin

    @property
    def new_position(self):
        return self.__new_position

    @property
    def new_value(self):
        return self.__new_value

    @property
    def new_size(self):
        return self.__new_size

    @property
    def type(self):
        return self.__origin.type

    def shift(self, offset):
        self.__new_position = self.__new_position + offset

    def offset(self):
        return self.new_size - self.origin.size

    def __str__(self):
        body = ''
        if self.type == 'uint':
            body = body + '{{new_pos: {:X}, orig: {}, value: {}, size: {}}}' \
                .format(self.__new_position, self.origin, self.new_value, self.new_size)
        elif self.type == 'utf16':
            body = body + '{{new_pos: {:X}, orig: {}, value: {}, size: {}}}'\
                    .format(self.__new_position, self.origin, '$UTF16', self.new_size)
        else:
            body = body + '{{new_pos: {:X}, orig: {}, value: "{}", size: {}}}' \
                .format(self.__new_position, self.origin, self.new_value, self.new_size)
        return '{}'.format(body)
