#  Copyright (c) 2004 Gavin E. Crooks <gec@compbio.berkeley.edu>
#
#  This software is distributed under the MIT Open Source License.
#  <http://www.opensource.org/licenses/mit-license.html>
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#

"""Custom extensions to OptionParse for parsing command line options."""

# FIXME: Docstring

# TODO: Add profiling option

# DeOptionParser :
#
#  http://docs.python.org/lib/module-optparse.html
#
# Random_options :
#   Set random generator and seed. Use options.random as
#   source of random numbers
# Copyright :
#   print copyright information

# Documentation :
#   print extended document information
#
# Additional file_in and file_out types

import sys
from copy import copy
from optparse import IndentedHelpFormatter, Option, OptionParser, OptionValueError
from typing import Any, Iterable, Optional, TextIO, Type


def _copyright_callback(
    option: Any, opt: Any, value: Any, parser: "DeOptionParser"
) -> None:
    if option or opt or value or parser:
        pass  # Shut up lint checker
    print(parser.copyright)
    sys.exit()


def _doc_callback(option: Any, opt: Any, value: Any, parser: "DeOptionParser") -> None:
    if option or opt or value or parser:
        pass  # Shut up lint checker
    print(parser.long_description)
    sys.exit()


class DeHelpFormatter(IndentedHelpFormatter):
    def __init__(
        self,
        indent_increment: int = 2,
        max_help_position: int = 32,
        width: int = 78,
        short_first: int = 1,
    ):
        IndentedHelpFormatter.__init__(
            self, indent_increment, max_help_position, width, short_first
        )

    def format_option_strings(self, option: Option) -> str:
        """Return a comma-separated list of option strings & metavariables."""
        if option.takes_value():
            dest = option.dest
            assert dest is not None
            metavar = option.metavar or dest.upper()
            short_opts = option._short_opts
            long_opts = [lopt + " " + metavar for lopt in option._long_opts]
        else:
            short_opts = option._short_opts
            long_opts = option._long_opts

        if not short_opts:
            short_opts = [
                "  ",
            ]

        if self.short_first:
            opts = short_opts + long_opts
        else:
            opts = long_opts + short_opts

        return " ".join(opts)


def _check_file_in(option: Any, opt: Any, value: str) -> TextIO:
    if option or opt or value:
        pass  # Shut up lint checker
    try:
        return open(value, "r")
    except IOError:
        raise OptionValueError("option %s: cannot open file: %s" % (opt, value))


def _check_file_out(option: Any, opt: Any, value: str) -> TextIO:
    if option or opt or value:
        pass  # Shut up lint checker
    try:
        return open(value, "w+")
    except IOError:
        raise OptionValueError("option %s: cannot open file: %s" % (opt, value))


def _check_boolean(option: Any, opt: Any, value: str) -> bool:
    if option or opt or value:
        pass  # Shut up lint checker
    v = value.lower()
    choices = {
        "no": False,
        "false": False,
        "0": False,
        "yes": True,
        "true": True,
        "1": True,
    }
    try:
        return choices[v]
    except KeyError:
        raise OptionValueError(
            "option %s: invalid choice: '%s' (choose from 'yes' or 'no', 'true' or 'false')"
            % (opt, value)
        )


def _check_dict(option: Any, opt: Any, value: str) -> str:
    if option or opt or value:
        pass  # Shut up lint checker
    v = value.lower()
    choices = option.choices
    try:
        return choices[v]
    except KeyError:
        raise OptionValueError(
            "option %s: invalid choice: '%s' (choose from '%s')"
            % (opt, value, "', '".join(choices))
        )


class DeOption(Option):
    TYPES = Option.TYPES + ("file_in", "file_out", "boolean", "dict")
    TYPE_CHECKER = copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["file_in"] = _check_file_in
    TYPE_CHECKER["file_out"] = _check_file_out
    TYPE_CHECKER["boolean"] = _check_boolean
    TYPE_CHECKER["dict"] = _check_dict
    choices = None

    def _new_check_choice(self) -> None:
        if self.type == "dict":
            if self.choices is None:
                raise OptionValueError(
                    "must supply a dictionary of choices for type 'dict'"
                )
            elif not isinstance(self.choices, dict):
                raise OptionValueError(
                    "choices must be a dictionary ('%s' supplied)"
                    % str(type(self.choices)).split("'")[1]
                )
            return
        self._check_choice()

    # Have to override _check_choices so that we can parse
    # a dict through to check_dict
    CHECK_METHODS = Option.CHECK_METHODS
    CHECK_METHODS[2] = _new_check_choice  # type: ignore


class DeOptionParser(OptionParser):
    def __init__(
        self,
        usage: Optional[str] = None,
        option_list: Optional[Iterable[Option]] = None,
        option_class: Type[Option] = DeOption,
        version: Optional[str] = None,
        conflict_handler: str = "error",
        description: Optional[str] = None,
        long_description: Optional[str] = None,
        formatter: IndentedHelpFormatter = DeHelpFormatter(),
        add_help_option: bool = True,
        prog: Optional[str] = None,
        copyright: Optional[str] = None,
        add_verbose_options: bool = True,
    ):
        OptionParser.__init__(
            self,
            usage,
            option_list,
            option_class,
            version,
            conflict_handler,
            description,
            formatter,
            add_help_option,
            prog,
        )

        if long_description:
            self.long_description = long_description
            self.add_option(
                "--doc",
                action="callback",
                callback=_doc_callback,
                help="Detailed documentation",
            )

        if copyright:
            self.copyright = copyright
            self.add_option(
                "--copyright", action="callback", callback=_copyright_callback, help=""
            )

        if add_verbose_options:
            self.add_option(
                "-q",
                "--quite",
                action="store_false",
                dest="verbose",
                default=False,
                help="Run quietly (default)",
            )

            self.add_option(
                "-v",
                "--verbose",
                action="store_true",
                dest="verbose",
                default=False,
                help="Verbose output (Not quite)",
            )
