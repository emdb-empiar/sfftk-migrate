import importlib
import os

from lxml import etree

from . import VERSION_LIST, XSL, MIGRATIONS_PACKAGE


def get_stylesheet(source, target, prefix="migrate"):
    stylesheet = os.path.join(XSL,
                              "{prefix}_v{source}_to_v{target}.xsl".format(prefix=prefix, source=source, target=target))
    assert os.path.exists(os.path.join(XSL, stylesheet))
    return stylesheet


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


def get_migration_path(source_version, target_version, version_list=VERSION_LIST):
    """Given the source, target versions and VERSION_LIST determine the migration path,
    which is a subset of the VERSION_LIST"""
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


def get_source_version(fn, path="/segmentation/version"):
    """
    Return the version of the document

    The version will always be in /segmentation/version

    :param str fn: filename as a string
    :param str path: the XPath description to the version string
    :return: version
    :rtype: str
    """
    source_tree = etree.parse(fn)
    source_version = source_tree.xpath("{path}/text()".format(path=path))[0]
    return source_version
