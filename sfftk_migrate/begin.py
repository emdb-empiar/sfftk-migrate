import argparse
import base64
import importlib
import os
import shlex
import struct
import sys
import warnings
from functools import partial

from lxml import etree

_print = partial(print, file=sys.stderr)

# the sequence of versions and how to proceed with a migration
VERSION_LIST = [
    '0.7.0.dev0',
    '0.8.0.dev0'
]
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__))
XSL = os.path.join(TEST_DATA_PATH, 'xsl')
XML = os.path.join(TEST_DATA_PATH, 'xml')
MIGRATIONS_PACKAGE = 'sfftk_migrate.migrations'
ENDIANNESS = {
    "little": "<",
    "big": ">",
}
MODE = {
    "int8": "b",
    "uint8": "B",
    "int16": "h",
    "uint16": "H",
    "int32": "i",
    "uint32": "I",
    "int64": "q",
    "uint64": "Q",
    "float32": "f",
    "float64": "d"
}
"""
Lessons learned in using `lxml`
---------------------------------
etree.parse() takes XML files/file objects and returns an ElementTree
etree.XML() takes a string and returns an Element regardless of the content
etree.ElementTree(root_element) converts an element into an ElementTree
etree.XSLT() takes an ElementTree or Element object and returns a transformer object
a transformer object should take an ElementTree (but seems to also take Element objects)
the result of a transformation is an _XSLTResultTree which behaves like an ElementTree but submits to str()
"""

# todo: editing complex elements
"""
from: https://lxml.de/xpathxslt.html#xslt-result-objects
It is possible to pass parameters, in the form of XPath expressions, to the XSLT template:

>>> xslt_tree = etree.XML('''\
... <xsl:stylesheet version="1.0"
...     xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
...     <xsl:param name="a" />
...     <xsl:template match="/">
...         <foo><xsl:value-of select="$a" /></foo>
...     </xsl:template>
... </xsl:stylesheet>''')
>>> transform = etree.XSLT(xslt_tree)
>>> doc_root = etree.XML('<a><b>Text</b></a>')

The parameters are passed as keyword parameters to the transform call. First, let's try passing in a simple integer expression:

>>> result = transform(doc_root, a="5")
>>> str(result)
'<?xml version="1.0"?>\n<foo>5</foo>\n'

"""


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


def migrate_by_stylesheet(original, stylesheet, verbose=False, **kwargs):
    """
    Migrate `original` according to `stylesheet`

    :param str original: the name of an XML file
    :param str stylesheet: the name of an XSLT file
    :return: the transformed XML document
    :rtype: bytes
    """
    _check(original, str, TypeError)
    _check(stylesheet, str, TypeError)
    original_doc = etree.parse(original)  # ElementTree
    original_elements = set([original_doc.getpath(element) for element in original_doc.iter()])
    # _print('original_doc:', original_elements)
    stylesheet_doc = etree.parse(stylesheet)  # ElementTree
    transform = etree.XSLT(stylesheet_doc)  # transformer
    _kwargs = dict()
    for kw in kwargs:
        _kwargs[kw] = etree.XSLT.strparam(kwargs[kw])
    migrated = transform(original_doc, **_kwargs)  # XSLTResultTree (like ElementTree)
    migrated_elements = set([migrated.getpath(element) for element in migrated.iter()])
    # _print('migrated_doc:', migrated_elements)
    dropped_fields = original_elements.difference(migrated_elements)
    # _print('difference:', dropped_fields)
    if dropped_fields and len(original_elements) > len(migrated_elements) and verbose:
        warnings.warn(
            UserWarning('the migration has resulted in the following fields being dropped: {}'.format(
                ', '.join(dropped_fields))),
        )
    return etree.tostring(migrated, pretty_print=True, xml_declaration=True)


def get_source_version(fn):
    """
    Return the version of the document

    The version will always be in /segmentation/version

    :param str fn: filename as a string
    :return: version
    :rtype: str
    """
    source_tree = etree.parse(fn)
    source_version = source_tree.xpath("/segmentation/version/text()")[0]
    return source_version


def get_migration_path(source_version, target_version, version_list=VERSION_LIST):
    """Given the source, target versions and VERSION_LIST determine the migration path, which is a subset of the VERSION_LIST"""
    try:
        start = version_list.index(source_version)
    except ValueError:
        raise ValueError(
            "invalid migration start: '{}' not found in VERSION_LIST={}".format(source_version, version_list))
    try:
        end = version_list.index(target_version)
    except ValueError:
        raise ValueError(
            "invalid migration end: '{}' not found in VERSION_LIST={}".format(target_version, version_list))
    migration_path = [(version_list[i], version_list[i + 1]) for i in range(start, end)]
    return migration_path


def get_output_name(input, target):
    _input = input.split('.')
    root = '.'.join(_input[:-1])
    ext = _input[-1]
    output = '{root}_v{target}.{ext}'.format(
        root=root,
        target=target,
        ext=ext,
    )
    return output


# Alternative implementation of do_migrate that calls additional functions e.g. for migrating meshes
def do_migration(args, value_list=None, version_list=VERSION_LIST):
    """Top-level function to effect a migration given args

    Effect the requested migration according to the `version_list`. Passes all `kwargs` on to the
    actual `migrate` function. `kwargs` should be a dictionary with string values.
    """
    source_version = get_source_version(args.infile)
    migration_path = get_migration_path(source_version, args.target_version, version_list=version_list)
    if args.verbose:
        _print("migration path: ")
        for _path in migration_path:
            _print("\t* {} ---> {}".format(*_path))
    input = args.infile
    for source, target in migration_path:
        if args.verbose:
            _print("preparing to migrate v{source} to v{target}...".format(
                source=source,
                target=target,
            ))
        module = get_module(source, target)
        if 'PARAM_LIST' in dir(module):
            params = get_params(module.PARAM_LIST, value_list=value_list)
        else:
            params = dict()  # empty dictionary
        stylesheet = get_stylesheet(source, target)
        if args.verbose:
            _print("using stylesheet {}...".format(stylesheet))
        outfile = get_output_name(input, target)
        if args.verbose:
            _print("migrating to {}".format(outfile))
        input = module.migrate(input, outfile, stylesheet, args, **params)
    return os.EX_OK


def get_module(source, target, prefix="migrate"):
    ".{prefix}_v{source}_to_v{target}"
    module_name = "{package}.{prefix}_v{source}_to_v{target}".format(
        package=MIGRATIONS_PACKAGE,
        prefix=prefix,
        source=source.replace('.', '_'),
        target=target.replace('.', '_'),
    )
    module = importlib.import_module(module_name)
    return module


def get_params(param_list, value_list=None):
    params = dict()
    for i, param in enumerate(param_list):
        if value_list:
            try:
                assert len(param_list) == len(value_list)
            except AssertionError:
                raise ValueError("incompatible lengths for param_list and value_list; they should be equal")
            param_value = value_list[i]
        else:
            param_value = input("{}: ".format(param))
        params[param] = param_value
    return params


def get_stylesheet(source, target, prefix="migrate"):
    stylesheet = os.path.join(XSL,
                              "{prefix}_v{source}_to_v{target}.xsl".format(prefix=prefix, source=source, target=target))
    assert os.path.exists(os.path.join(XSL, stylesheet))
    return stylesheet


def parse_args(args, use_shlex=True):
    if use_shlex:
        _args = shlex.split(args)
    else:
        _args = args

    parser = argparse.ArgumentParser(prog='sff-migrate', description='Upgrade EMDB-SFF files to more recent schema')
    parser.add_argument('infile', help='input XML file')
    parser.add_argument('-t', '--target-version', default=VERSION_LIST[-1],
                        help='the target version to migrate to [default: {}]'.format(VERSION_LIST[-1]))
    parser.add_argument('-o', '--outfile', required=False, help='outfile file [default: <infile>_<target>.xml]')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='verbose output [default: False]')

    args = parser.parse_args(_args)

    if args.outfile is None:
        input_fn = args.infile.split('.')
        root, ext = '.'.join(input_fn[:-1]), input_fn[-1]
        args.outfile = os.path.join(
            os.path.dirname(args.infile),
            '{root}_{target}.{ext}'.format(
                root=root,
                target=args.target_version,
                ext=ext
            )
        )
    return args


def main():
    # migrated = migrate('original.xml', 'original_to_add_field.xsl')
    # _migrated = migrate_by_stylesheet(os.path.join(XML, 'original.xml'),
    #                                   os.path.join(XSL, 'original_to_drop_field.xsl'))  # bytes
    # convert the migrated result to a byte sequence
    # migrated = etree.ElementTree(etree.XML(_migrated))
    # pp = etree.tostring(migrated, pretty_print=True, xml_declaration=True, encoding='utf-8')
    # sys.stderr.write(pp.decode('utf-8'))
    args = parse_args(sys.argv[1:], use_shlex=False)
    if args.verbose:
        _print("migrating {} to {}...".format(args.infile, args.outfile))
    status = do_migration(args)
    return status


if __name__ == "__main__":
    sys.exit(main())
