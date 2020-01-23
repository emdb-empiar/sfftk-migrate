import os
import warnings

from lxml import etree

from . import VERSION_LIST
from .core import get_source_version, get_migration_path, get_module, get_stylesheet, get_output_name
from .utils import _check, _print


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


def migrate_by_stylesheet(original, stylesheet, verbose=False, **kwargs):
    """Migrate `original` according to `stylesheet`

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
