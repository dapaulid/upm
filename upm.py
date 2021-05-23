#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
"""
	Minimalistic dependency manager for arbitrary files you get from the web.

    @license
    Copyright (c) Daniel Pauli <dapaulid@gmail.com>

    This source code is licensed under the MIT license found in the
    LICENSE file in the root directory of this source tree.
"""
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# package info
#-------------------------------------------------------------------------------
#
__version__ = '1.0.0'

#-------------------------------------------------------------------------------
# imports
#-------------------------------------------------------------------------------
#
import sys
import argparse

#-------------------------------------------------------------------------------
# commands
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
#
def cmd_install(args):
	fail("[TODO] implement install command, path=%s, url=%s" % (args.path, args.url))
# end function

#-------------------------------------------------------------------------------
#
def cmd_uninstall(args):
	fail("[TODO] implement uninstall command, path=%s" % (args.path))
# end function

#-------------------------------------------------------------------------------
#
def cmd_list(args):
	fail("[TODO] implement list command, path=%s" % (args.path))
# end function

#-------------------------------------------------------------------------------
# helpers
#-------------------------------------------------------------------------------
#
""" custom exception class for terminating script with error """
class Failed(Exception):
    pass
# end class

#-------------------------------------------------------------------------------
""" terminate script with error """
def fail(msg):
	raise Failed(msg)
# end function

#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
#
def main():
	
	# create command line parser
	parser = argparse.ArgumentParser()
	parser.set_defaults(func=lambda x: parser.print_help())	# print help by default
	subparsers = parser.add_subparsers(title="subcommands")
	
	# create "install" subcommand
	install_parser = subparsers.add_parser('install', 
		help="download and track dependencies")
	install_parser.add_argument('path', nargs='?', 
		help="file path to dependency")
	install_parser.add_argument('url', nargs='?', 
		help="URL for downloading the dependency")
	install_parser.set_defaults(func=cmd_install)	

	# create "uninstall" subcommand
	uninstall_parser = subparsers.add_parser('uninstall', 
		help="remove and untrack dependencies")
	uninstall_parser.add_argument('path', nargs='?', 
		help="file path to dependency")
	uninstall_parser.set_defaults(func=cmd_uninstall)

	# create "list" subcommand
	list_parser = subparsers.add_parser('list', 
		help="show info about tracked dependencies")
	list_parser.add_argument('path', nargs='?', 
		help="file path to dependency")
	list_parser.set_defaults(func=cmd_list)		

	# parse command line
	args = parser.parse_args()
	# run requested subcommand
	args.func(args)

# end function

#-------------------------------------------------------------------------------
# entry point
#-------------------------------------------------------------------------------
#
if __name__ == "__main__":
	try:
		main()
	except Failed as e:
		sys.stderr.write("error: %s\n" % e)
	# end try
# end if

#-------------------------------------------------------------------------------
# end of file
