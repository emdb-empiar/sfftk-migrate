import argparse
import os
import shlex
import sys

from . import VERSION_LIST
from .migrate import do_migration
from .utils import _print


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
    args = parse_args(sys.argv[1:], use_shlex=False) # no shlex for list of args
    if args.verbose:
        _print("migrating {} to {}...".format(args.infile, args.outfile))
    status = do_migration(args)
    return status


if __name__ == "__main__":
    sys.exit(main())
