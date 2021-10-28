import codec


def get_pad_length(given_length):
    return (4 - (given_length + 1) % 4) % 4


def get_padded_length(s):
    return 1 + len(s) + get_pad_length(len(s))


def inc(dictionary, key):
    if key not in dictionary:
        dictionary[key] = 1
    else:
        dictionary[key] += 1


def bytes_to_uint(bytedata):
    return int.from_bytes(bytedata, codec.BYTE_ORDER)


def bytes_to_int(bytedata):
    return int.from_bytes(bytedata, codec.BYTE_ORDER, signed=True)


def bytes_to_str(bytedata):
    return str(bytedata, encoding=codec.NO_UNICODE)

def uint8_to_bytes(value):
    return value.to_bytes(1, codec.BYTE_ORDER)


def uint32_to_bytes(value):
    return value.to_bytes(4, codec.BYTE_ORDER)


def str_to_bytes(value):
    return bytes(value, codec.NO_UNICODE)
