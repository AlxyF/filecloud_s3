import base64, magic


def is_base64(_bytes):
    try:
        return base64.b64encode(base64.b64decode(_bytes)) == _bytes
    except Exception:
        return False

def decode_base64(_bytes):
    return base64.b64decode(_bytes)

def encode_base64(_bytes):
    return base64.b64encode(_bytes)

def get_binary_file_info(_bytes) -> (str, str):
    info = magic.from_buffer(_bytes)
    info_list = info.split(',')
    file_main_info = info_list[0]
    file_aux_info = ''.join([str(item) + ',' for item in info_list[1:]]).strip(',').strip(' ')
    return file_main_info, file_aux_info

def get_mime_type(_bytes) -> str:
    return magic.from_buffer(_bytes, mime=True)