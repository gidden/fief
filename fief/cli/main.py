#! /usr/bin/env python

import os
import sys

if sys.version_info[0] == 3 or sys.version_info[:2] == (2, 7):
    import argparse
else:
    from . import _argparse as argparse

HOME = os.path.expanduser('~')

CONFIGS = [os.path.join(HOME, '.config', 'fiefconf'),
           os.path.join(HOME, '.config', 'fiefconf.py'),
           os.path.abspath('fiefconf'), 
           os.path.abspath('fiefconf.py'), 
           ]


def main(args=None):
    """Entry point for fief command line interface."""
    # Parse the command line arguments
    parser = _make_argparser()
    ns = parser.parse_args(args)
    if hasattr(ns, 'options'):
        ns.options = ns.options[1:] if ['--'] == ns.options[:1] else ns.options

    conf = {}
    CONFIGS.append(ns.conf)
    for conffile in CONFIGS:
        if os.path.isfile(conffile):
            execfile(conffile, conf, conf)

    # Run the fief command, use dynamic import
    if '.' not in sys.path:
        sys.path.insert(0, '.')
    cmdmod = __import__(ns.cmd, globals(), locals(), fromlist=[None])
    mainfunc = getattr(cmdmod, 'main')
    rtn = mainfunc(ns, conf)

    # Handle some edge cases
    if rtn is NotImplemented:
        print "Command '{0}' has not yet been implemented.".format(cmd)
        raise SystemExit(1)
    elif 0 < rtn:
        print "fief encountered an error."
        raise SystemExit(rtn)


def _make_argparser():
    """Creates agrument parser for fief."""
    commands = set(['realize'])

    cmds = set()
    parser = argparse.ArgumentParser(description='FLASH make utility.', )
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       dest="cmd",
                                       help='sub-command help')

    # convenience addition functions
    add_dry_run = lambda p: p.add_argument('--dry-run', default=False, 
                                           action='store_true', 
                                           help='simulates running this command', 
                                           required=False, dest="dry_run")
    add_nprocs  = lambda p: p.add_argument('-n', '-np', '--n', '--np', '--nprocs',
                                           default=None, dest='nprocs')
    add_target  = lambda p: p.add_argument('-t', '--target', type=str, dest='target', 
                                           help='target file/dir name', default=None)
    add_source  = lambda p: p.add_argument('src', type=str, help='source file or dir')
    add_destin  = lambda p: p.add_argument('dst', type=str, 
                                           help='destination file or dir')
    add_ifcs = lambda p: p.add_argument('ifcs', type=str, nargs='+', metavar='ifc', 
                                        help='activate additional interfaces')
    add_activate = lambda p: p.add_argument('-a', '--activate', type=str, nargs='+',
                                           metavar='ifc', dest='activate',
                                           help='additional interfaces to activate')
    add_deactivate = lambda p: p.add_argument('-d', '--deactivate', type=str, 
                                              nargs='+', metavar='ifc', 
                                              dest='deactivate',
                                              help='interfaces to deactivate')
    add_conf = lambda p: p.add_argument('--conf', type=str, dest='conf', 
                                        required=False,
                                        help='configuration file path', 
                                        default='<conf-file>')
    add_verbose = lambda p: p.add_argument('-v', '--verbose', 
                                           dest='verbose', action='store_true',
                                           help='show more information', default=False)

    # add build command
    cmds.add('realize')
    subparser = subparsers.add_parser('realize')
    add_conf(subparser)
    add_verbose(subparser)

    # add activate
    cmds.add('activate')
    subparser = subparsers.add_parser('activate')
    add_conf(subparser)
    add_verbose(subparser)
    add_ifcs(subparser)

    # add default parser for remaining commands
    for key in set(commands) - cmds:
        subparser = subparsers.add_parser(key)
        add_conf(subparser)
    return parser


if __name__ == '__main__':
    main()
