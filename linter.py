#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Falco,,,,
# Copyright (c) 2015 Falco,,,,
#
# License: MIT
#

"""This module exports the Glualint plugin class."""

from SublimeLinter.lint import Linter, util


class Glualint(Linter):

    """Provides an interface to glualint."""

    syntax = 'lua'
    cmd = 'glualint'
    config_file = ('--config', 'glualint.json')
    version_args = '--version'
    version_re = r'(?P<version>\d+\.\d+\.\d+)'
    version_requirement = '>= 1.0, < 2.0'
    regex = (
        r'^.+?: \[((?P<error>Error)|(?P<warning>Warning))\] '
        r'line (?P<line>\d+), column (?P<col>\d+): '
        r'(?P<message>.+)'
    )
    multiline = False
    line_col_base = (1, 1)
    tempfile_suffix = 'lua'
    error_stream = util.STREAM_STDOUT

