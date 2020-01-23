import base64
import struct
import sys
from functools import partial

from . import ENDIANNESS, MODE

_print = partial(print, file=sys.stderr)


def _check(obj, klass, exception=Exception, message="object '{}' is not of class {}"):
    """
    Check that `obj` is of type `klass` else raise `exception`
    :param obj: some object
    :param type klass: some class
    :param Exception exception: the exception to raise
    """
    try:
        assert isinstance(obj, klass)
    except AssertionError:
        if message.find("{}"):
            raise exception(message.format(obj, klass))
        else:
            raise exception(message)


def _decode_data(data64, length, mode, endianness="little"):
    bin_data = base64.b64decode(data64)
    data = struct.unpack("{}{}{}".format(ENDIANNESS[endianness], length * 3, MODE[mode]), bin_data)
    return data
