def get_pad_length(given_length):
    return (4 - (given_length + 1) % 4) % 4


def get_padded_length(s):
    return 1 + len(s) + get_pad_length(len(s))


def inc(dictionary, key):
    if key not in dictionary:
        dictionary[key] = 1
    else:
        dictionary[key] = dictionary[key] + 1
