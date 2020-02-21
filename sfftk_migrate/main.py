import argparse
import os
import shlex
import sys

from . import VERSION_LIST
from .core import get_output_name, get_source_version
from .migrate import do_migration
from .utils import _print


def list_versions():
    """
    List the EMDB-SFF versions that are migratable to the current version
    :return: status
    :return: version_count
    """
    version_count = len(VERSION_LIST)
    for version in VERSION_LIST[:-1]:
        _print('* {version}'.format(version=version))
    return os.EX_OK, version_count


def parse_args(args, use_shlex=True):
    """Perform argument parsing as well as

    :param args: commands with options
    :type args: list or str
    :param bool use_shlex: use shell lexing on the input (string) [default: True]
    :return: an argument namespace
    :rtype: `argparse.Namespace`
    """
    if use_shlex:
        _args = shlex.split(args)
    else:
        _args = args

    parser = argparse.ArgumentParser(
        prog='sff-migrate',
        description='Upgrade EMDB-SFF files to more recent schema',
    )
    parser.add_argument('infile', nargs='?', default='', help='input XML file')
    parser.add_argument('-t', '--target-version', default=VERSION_LIST[-1],
                        help='the target version to migrate to [default: {}]'.format(VERSION_LIST[-1]))
    parser.add_argument('-o', '--outfile', required=False, help='outfile file [default: <infile>_<target>.xml]')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='verbose output [default: False]')
    parser.add_argument(
        '-l', '--list-versions',
        default=False,
        action='store_true',
        help='list supported versions [default: False]'
    )
    parser.add_argument(
        '-s', '--show-version',
        default=False,
        action='store_true',
        help='show the version of the input file [default: False]'
    )

    args = parser.parse_args(_args)

    if args.outfile is None and args.infile != '':
        args.outfile = get_output_name(args.infile, args.target_version, prefix="")
    return args


def main():
    args = parse_args(sys.argv[1:], use_shlex=False)  # no shlex for list of args
    if args.list_versions:
        _print("versions migratable to {current_version}:".format(
            current_version=VERSION_LIST[-1],
        ))
        status, _ = list_versions()
    elif args.show_version:
        _print("file {infile} is of version {version}".format(
            infile=args.infile,
            version=get_source_version(args.infile)
        ))
        status = os.EX_OK
    else:
        if args.verbose:
            _print("migrating {} to {}...".format(args.infile, args.outfile))
        status = do_migration(args)
    return status


if __name__ == "__main__":
    sys.exit(main())
