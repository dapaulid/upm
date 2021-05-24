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
import os
import sys
import argparse
import urllib.request
import urllib.parse
import json
import re

#-------------------------------------------------------------------------------
# constants
#-------------------------------------------------------------------------------
#
CONFIG_FILENAME = ".upm.json"

REGEX_SEMVER = re.compile(r'(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?')

def find_version(inp):
	for line in inp:
		m = REGEX_SEMVER.search(line)
		if m:
			return m.group(0)
	# end for
	return None
# end function

class Config:

	def __init__(self, can_create=False, directory=os.getcwd()):
		self.directory = None
		self.deps = {}
		self.find(os.path.abspath(directory))
		if self.exists():
			self.load()
		elif not can_create:
			fail("no upm config file found")
		# end if
	# end function

	def save(self):
		state = {
			'deps': self.deps
		}
		with open(self.get_filename(), 'w', encoding='utf-8') as out:
			json.dump(state, out, ensure_ascii=False, indent=2)
	# end function

	def load(self):
		with open(self.get_filename(), 'r', encoding='utf-8') as inp:
			state = json.load(inp)
			self.deps = state['deps']
		# end with 
	# end function

	def find(self, directory):
		# find existing config file
		self.directory = directory	
		while not self.exists():
			# check parent directory
			old_dir = self.directory
			self.directory = os.path.dirname(self.directory)
			if self.directory == old_dir:
				# root reached
				self.directory = directory
				return False
			# end if
		# end while
		return True
	# end function

	def get_filename(self):
		return os.path.join(self.directory, CONFIG_FILENAME)
	# end function

	def exists(self):
		return os.path.exists(self.get_filename())
	# end function

	def from_user(self, path):
		path = os.path.normpath(path)
		path = os.path.abspath(path)
		path = os.path.relpath(path, self.directory)
		path = path.replace(os.path.sep, '/')
		return path
	# end function

	def to_user(self, path):
		path = path.replace('/', os.path.sep)
		path = os.path.join(self.directory, path)
		path = os.path.relpath(path)
		return path
	# end function
	
# end class

#-------------------------------------------------------------------------------
# commands
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
#
def cmd_install(args):
	url = args.url
	path = args.path

	config = Config(can_create=True)
	
	# path points to a directory?
	if os.path.isdir(path):
		# yes -> append file name from URL
		path = os.path.join(path, os.path.basename(urllib.parse.urlparse(url).path))
	else:
		# no -> is a file -> parent directory must exist
		dir = os.path.dirname(path)
		if not os.path.isdir(dir):
			fail("directory does not exist: %s" % dir)
		# end if
	# end if

	path = os.path.normpath(path)

	# example: upm.py install animate.css https://raw.githubusercontent.com/animate-css/animate.css/main/animate.min.css
	fetch(url, path)

	with open(path, 'r', encoding='utf-8') as inp:
		version = find_version(inp)
	# end with

	# add entry
	config.deps[config.from_user(path)] = {
		'url': url,
		'version': version,
	}

	config.save()

	print("installed %s -> version %s" % (path, version))

# end function

#-------------------------------------------------------------------------------
#
def cmd_uninstall(args):

	path = os.path.normpath(args.path)

	# check if in config
	config = Config()
	cpath = config.from_user(path)
	if not cpath in config.deps:
		fail("not a dependency: %s" % path)
	# end if

	# remove from file system
	if os.path.exists(path):
		os.remove(path)
	# end if

	# remove from config
	del config.deps[cpath]
	config.save()

	# success
	print("uninstalled %s" % (path))

# end function

#-------------------------------------------------------------------------------
#
def cmd_list(args):
	config = Config()
	for path, entry in config.deps.items():
		print("%s (%s)" % (config.to_user(path), entry['version']))
	# end for
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
#
def fetch(url, filename):
	try:
		# TODO may become deprecated for Python 3
		urllib.request.urlretrieve(url, filename)
	except urllib.error.HTTPError as e:
		fail("failed to fetch %s (%s)" % (url, e))
	# end try
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
		sys.stderr.write("[error] %s\n" % e)
	# end try
# end if

#-------------------------------------------------------------------------------
# end of file
