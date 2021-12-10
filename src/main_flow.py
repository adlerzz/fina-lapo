from Mapper import *
import codec
import utils
from WritePointer import *
import logging

DUPLICATE_SUFFIX = '_DUP_'
LOG_FORMAT = '%(asctime)s [%(levelname)-5s] %(funcName)s : %(message)s'

logging.basicConfig(filename='logs/app.log', level=logging.DEBUG, format=LOG_FORMAT)


class Reader:
    def __init__(self, file):
        self.f = file

    def read_file_header(self):
        signature = self.f.read_bytes(4)
        if signature != b'8BPS':
            raise Exception("Bad format")
        version = self.f.read_uint16()
        if version == 1:
            pass
        elif version == 2:
            raise Exception('Unsupported file format (PSB)')
        else:
            raise Exception('Bad version')

        self.f.move_on(20)

    def read_color_mode_data(self):
        color_data_length = self.f.read_uint32()
        self.f.move_on(color_data_length)

    def read_image_resources(self):
        img_res_length = self.f.read_uint32()
        self.f.move_on(img_res_length)

    def read_layer_pre(self):
        self.f.move_on(16)
        channel_count = self.f.read_uint16()
        self.f.move_on(channel_count * 6 + 12)
        extra_fields_len = self.f.mark_uint32()
        mask_data_length = self.f.read_uint32()
        self.f.move_on(mask_data_length)
        br_data_length = self.f.read_uint32()
        self.f.move_on(br_data_length)
        d = 4 + mask_data_length + 4 + br_data_length
        return extra_fields_len, d


class ActionComposer:

    def __init__(self):
        self.__filemap = None
        self.__lm_data_length = None
        self.__l_data_length = None
        self.__layer_names = dict()
        self.__layer_pointers = list()
        self.__layer_wpointers = list()
        self.__lmd = None
        self.__ld = None

    def do_read(self, filename):
        logging.info(f'start reading with "{filename}"')
        self.__filemap = Mapper(filename)
        r = Reader(self.__filemap)
        r.read_file_header()
        r.read_color_mode_data()
        r.read_image_resources()

        self.__lm_data_length = self.__filemap.mark_uint32()
        logging.debug(f'lm_data_length: {self.__lm_data_length}')

        self.__l_data_length = self.__filemap.mark_uint32()
        logging.debug(f'l_data_length: {self.__l_data_length}')

        layer_count = abs(self.__filemap.read_int16())
        logging.debug(f'layer_count: {layer_count}')

        for i in range(0, layer_count):

            # print('###{} layer###'.format(i+1))
            (extra_fields_length, delta) = r.read_layer_pre()
            layer_name = self.__filemap.mark_str()
            shift = extra_fields_length.value - delta - layer_name.size

            while shift > 8:
                a_signature = self.__filemap.read_bytes(4)
                if a_signature != b'8BIM' and a_signature != b'8B64':
                    raise Exception("File is corrupted")
                a_key = self.__filemap.read_bytes(4)
                a_value = self.__filemap.mark_utf16()
                if a_key == b'luni':
                    u_layer_name = a_value.value[4:].decode(codec.UNICODE).rstrip('\x00')

                    new_layer_name = codec.translate_name(u_layer_name)

                    if not new_layer_name.startswith('</') and new_layer_name != layer_name.value:
                        utils.count(self.__layer_names, new_layer_name)
                        self.__layer_pointers.append((extra_fields_length, layer_name, a_value))

                shift -= 8 + a_value.size

        logging.debug(f'layer_names: {self.__layer_names}')

    def do_translate(self):

        for ptr in self.__layer_pointers:
            (extra, layer, u_layer) = ptr
            # print(layer, u_layer)
            new_layer_name = codec.translate_name(layer.value)
            repeats = self.__layer_names[new_layer_name]
            self.__layer_names[new_layer_name] = repeats - 1
            if repeats > 1:
                new_layer_name += DUPLICATE_SUFFIX + str(repeats)

            ln = WritePointer(layer, new_layer_name, utils.get_padded_length(new_layer_name))

            u_b = utils.uint32_to_bytes(len(new_layer_name)) + utils.str_to_ubytes(new_layer_name) + b'\x00\x00'
            u_l = utils.uint32_to_bytes(len(u_b))

            un = WritePointer(u_layer, u_l + u_b, len(u_b) + 4)

            n_ex = WritePointer(extra, extra.value + ln.offset() + un.offset(), extra.size)

            self.__layer_wpointers.append(n_ex)
            self.__layer_wpointers.append(ln)
            self.__layer_wpointers.append(un)

    def do_shifts(self):
        sh = 0

        for p in self.__layer_wpointers:
            p.shift(sh)
            sh += p.offset()

        logging.debug(f'Summary size shift : {sh}')

        self.__lmd = WritePointer(self.__lm_data_length, self.__lm_data_length.value + sh, self.__lm_data_length.size)
        self.__ld = WritePointer(self.__l_data_length, self.__l_data_length.value + sh, self.__l_data_length.size)

    def do_write(self, filename):
        self.__filemap.write_pointer(self.__lmd)
        self.__filemap.write_pointer(self.__ld)

        counter = 1
        all_of = len(self.__layer_wpointers)
        for p in self.__layer_wpointers:
            self.__filemap.write_pointer(p)

            logging.debug(p)
            logging.debug('{} of {}'.format(counter, all_of))
            print('{} of {}'.format(counter, all_of))
            counter += 1
        self.__filemap.save(filename)
        logging.info(f'stored to "{filename}"')


try:
    ac = ActionComposer()
    ac.do_read('nymph.psd')
    ac.do_translate()
    ac.do_shifts()
    ac.do_write('hymph_handled.psd')
except Exception as ex:
    logging.error(ex)
    print(ex)
