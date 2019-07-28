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

    cmd = 'glualint --stdin'
    config_file = ('--config', 'glualint.json')
    regex = (
        r'^.+?: \[((?P<error>Error)|(?P<warning>Warning))\] '
        r'line (?P<line>\d+), column (?P<col>\d+)( - line \d+, column \d+)?: '
        r'(?P<message>.+)'
    )
    defaults = { 'selector': 'source.lua' }
    multiline = False
    line_col_base = (1, 1)
    error_stream = util.STREAM_STDOUT

