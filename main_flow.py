# "orthodox_xmas_angel_test.psd"

from Mapper import *
import codec
import utils
from WritePointer import *

DUPLICATE_SUFFIX = '_DUP_'


class Reader:
    def __init__(self, file):
        self.f = file

    def handle_file_header(self):
        signature = self.f.read_bytes(4)
        print(signature)
        if signature != b'8BPS':
            raise Exception("Bad format")
        version = f.read_int(2)
        if version == 1:
            pass
        elif version == 2:
            raise Exception('Unsupported file format (PSB)')
        else:
            raise Exception('Bad version')

        self.f.move_on(20)

    def handle_color_mode_data(self):
        color_data_length = self.f.read_int(4)
        self.f.move_on(color_data_length)

    def handle_image_resources(self):
        img_res_length = self.f.read_int(4)
        self.f.move_on(img_res_length)

    def handle_layer_pre(self):
        self.f.move_on(16)
        channel_count = self.f.read_int(2)
        self.f.move_on(channel_count * 6 + 12)
        extra_fields_len = self.f.mark_uint32()
        mask_data_length = self.f.read_int(4)
        self.f.move_on(mask_data_length)
        br_data_length = self.f.read_int(4)
        self.f.move_on(br_data_length)
        d = 4 + mask_data_length + 4 + br_data_length
        return extra_fields_len, d


# f = Mapper("orthodox_xmas_angel_test.psd")
f = Mapper("test.psd")

r = Reader(f)
r.handle_file_header()
r.handle_color_mode_data()
r.handle_image_resources()

lm_data_length = f.mark_uint32()
print(f'lm_data_length: {lm_data_length}')
l_data_length = f.mark_uint32()
print(f'l_data_length: {l_data_length}')

layer_count = abs(f.read_int(2, True))
print(f'layer_count: {layer_count}')

layer_pointers = list()
layer_names = dict()

print('----')
for i in range(0, layer_count):

    # print('###{} layer###'.format(i+1))
    (extra_fields_length, delta) = r.handle_layer_pre()
    layer_name = f.mark_str()
    sh = extra_fields_length.value - delta - layer_name.size

    while sh > 8:
        a_signature = f.read_bytes(4)
        if a_signature != b'8BIM' and a_signature != b'8B64':
            raise Exception("File is corrupted")
        a_key = f.read_bytes(4)
        a_value = f.mark_utf16()
        if a_key == b'luni':
            u_layer_name = a_value.value[4:].decode(codec.UNICODE).rstrip('\x00')

            new_layer_name = codec.translate_name(u_layer_name)

            if not new_layer_name.startswith('</') and new_layer_name != layer_name.value:
                utils.inc(layer_names, new_layer_name)

                layer_pointers.append((extra_fields_length, layer_name, a_value))

        sh = sh - 8 - a_value.size

    if sh > 0:
        f.move_on(sh)

# f.save("orthodox_xmas_angel_test_ch.psd")
# f.save("golden_wheel_ch.psd")

print(layer_names)
layer_wpointers = list()

for p in layer_pointers:
    (ex, layer, u_layer) = p
    # print(layer, u_layer)
    new_layer_name = codec.translate_name(layer.value)
    p = layer_names[new_layer_name]
    layer_names[new_layer_name] = p - 1
    if p > 1:
        new_layer_name = new_layer_name + DUPLICATE_SUFFIX + str(p)

    ln = WritePointer(layer, new_layer_name, utils.get_padded_length(new_layer_name))

    u_b = len(new_layer_name).to_bytes(4, 'big') + bytes(new_layer_name, codec.UNICODE) + b'\x00\x00'
    u_l = len(u_b).to_bytes(4, 'big')
    un = WritePointer(u_layer, u_l + u_b, len(u_b) + 4)

    n_ex = WritePointer(ex, ex.value + ln.offset() + un.offset(), ex.size)

    layer_wpointers.append((n_ex, ln, un))

sh = 0

for p in layer_wpointers:
    (ex, ln, un) = p
    ex.shift(sh)
    sh = sh + ex.offset()
    # print(ex)

    ln.shift(sh)
    sh = sh + ln.offset()
    # print(ln)

    un.shift(sh)
    sh = sh + un.offset()
    # print(un)

print(f'Summary size shift : {sh}')

lmd = WritePointer(lm_data_length, lm_data_length.value + sh, lm_data_length.size)
ld = WritePointer(l_data_length, l_data_length.value + sh, l_data_length.size)

f.write_pointer(lmd)
f.write_pointer(ld)

l = 1
for p in layer_wpointers:
    (ex, ln, un) = p
    f.write_pointer(ex)
    f.write_pointer(ln)
    f.write_pointer(un)
    print(ex)
    print(ln)
    print(un)
    print('{} of {}'.format(l, len(layer_wpointers)))
    l = l+1

f.save('test_handled.psd')


