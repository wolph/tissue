"""
PEP8 automated checker for nose. Based on coverage plugin
"""
import logging
import os
import sys

import pep8

from nose import plugins
from nose import util


log = logging.getLogger("nose.plugins.tissue")


# thanks pinocchio nose plugin for this code
color_end = "\x1b[1;0m"
colors = dict(green="\x1b[1;32m", red="\x1b[1;31m", yellow="\x1b[1;33m")


def in_color(color, text):
    """
    Colorize text, adding color to each line so that the color shows up
    correctly with the less -R as well as more and normal shell.
    """
    return "".join("%s%s%s" % (colors[color], line, color_end)
                            for line in text.splitlines(True))


class TissueReport(pep8.StandardReport):
    '''pep8's Standard report with a get_file_results that accepts an optional stream arg to output to'''

    def get_file_results(self, stream=sys.stdout):
        """Write the result to stream and return the overall count for this file."""
        self._deferred_print.sort()
        for line_number, offset, code, text, doc in self._deferred_print:
            stream.write(self._fmt % {
                'path': self.filename,
                'row': self.line_offset + line_number, 'col': offset + 1,
                'code': code, 'text': text,
            } + '\n')
            if self._show_source:
                if line_number > len(self.lines):
                    line = ''
                else:
                    line = self.lines[line_number - 1]
                stream.write(line.rstrip() + '\n')
                stream.write(' ' * offset + '^\n')
            if self._show_pep8 and doc:
                stream.write(doc.lstrip('\n').rstrip() + '\n')
        return self.file_errors


class Tissue(plugins.Plugin):
    """Automated PEP8 checked for nose"""

    name = "tissue"

    def begin(self):
        self.messages = []
        self.seen_files = []

    def seen(self, filename):
        if filename not in self.seen_files:
            self.seen_files.append(filename)
            return False
        return True

    def want_file(self, filename):
        if self.tissue_packages:
            file_pkg = util.getpackage(filename)
            for package in self.tissue_packages:
                if package in file_pkg and not self.seen(filename):
                    return True
        else:
            if not self.seen(filename):
                return True
        return False

    def beforeDirectory(self, path):
        def seen_runner(filename):
            if self.want_file(filename):
                self.pep8.input_file(filename)
        self.pep8.runner = seen_runner
        self.pep8.input_dir(path)

    def beforeImport(self, filename, module):
        if filename.endswith(".py") and self.want_file(filename):
            self.pep8.input_file(filename)

    def configure(self, options, config):
        plugins.Plugin.configure(self, options, config)
        self.conf = config
        self.tissue_packages = []
        self.tissue_statistics = options.tissue_statistics
        if options.tissue_packages:
            for pkgs in [util.tolist(x) for x in options.tissue_packages]:
                self.tissue_packages.extend(pkgs)
        self.tissue_inclusive = options.tissue_inclusive
        if self.tissue_packages:
            log.info("PEP8 report will include only packages: %s",
                     self.tissue_packages)

        # NOTE(jkoelker) Urgh! Really? Global options? At least there is a
        #                function that takes the arglist ;(
        arglist = []
        if options.tissue_repeat:
            arglist.append("--repeat")

        if options.tissue_select:
            arglist.append("--select")
            arglist.append(options.tissue_select)

        if options.tissue_ignore:
            arglist.append("--ignore")
            arglist.append(options.tissue_ignore)

        if options.tissue_show_source:
            arglist.append("--show-source")

        if options.tissue_show_pep8:
            arglist.append("--show-pep8")

        options, paths = pep8.process_options(arglist)
        self.pep8 = pep8.StyleGuide(**options.__dict__)
        self.pep8.init_report(TissueReport)

    def options(self, parser, env):
        plugins.Plugin.options(self, parser, env)
        parser.add_option("--tissue-package", action="append",
                          default=env.get("NOSE_TISSUE_PACKAGE"),
                          metavar="PACKAGE",
                          dest="tissue_packages",
                          help="Restrict pep8 output to selected packages "
                               "[NOSE_TISSUE_PACKAGE]")
        parser.add_option("--tissue-inclusive", action="store_true",
                          dest="tissue_inclusive",
                          default=env.get("NOSE_TISSUE_INCLUSIVE"),
                          help="Include all python files under working "
                               "directory in pep8 run. "
                               "[NOSE_TISSUE_INCLUSIVE]")
        parser.add_option("--tissue-repeat", action="store_true",
                          default=env.get("NOSE_TISSUE_REPEAT"),
                          metavar="ERRORS",
                          dest="tissue_repeat",
                          help="Show all occurrences of the same error "
                               "[NOSE_TISSUE_REPEAT]")
        parser.add_option("--tissue-select",
                          default=env.get("NOSE_TISSUE_SELECT"),
                          metavar="ERRORS",
                          dest="tissue_select",
                          help="Select errors and warnings (e.g. E,W6) "
                               "[NOSE_TISSUE_SELECT]")
        parser.add_option("--tissue-ignore",
                          default=env.get("NOSE_TISSUE_ignore"),
                          metavar="ERRORS",
                          dest="tissue_ignore",
                          help="Skip errors and warnings (e.g. E,W6) "
                               "[NOSE_TISSUE_IGNORE]")
        parser.add_option("--tissue-show-source", action="store_true",
                          dest="tissue_show_source",
                          default=env.get("NOSE_TISSUE_SHOW_SOURCE"),
                          help="Show source code for each error "
                               "[NOSE_TISSUE_SHOW_SOURCE]")
        parser.add_option("--tissue-show-pep8", action="store_true",
                          dest="tissue_show_pep8",
                          default=env.get("NOSE_TISSUE_SHOW_TISSUE"),
                          help="Show text of PEP 8 for each error "
                               "[NOSE_TISSUE_SHOW_TISSUE]")
        parser.add_option("--tissue-statistics", action="store_true",
                          dest="tissue_statistics",
                          default=env.get("NOSE_TISSUE_STATISTICS"),
                          help="Count errors and warnings "
                               "[NOSE_TISSUE_STATISTICS]")
        parser.add_option("--tissue-color", action="store_true",
                          dest="tissue_color",
                          default=env.get("NOSE_TISSUE_COLOR"),
                          help="Show errors and warnings using colors "
                               "[NOSE_TISSUE_COLOR]")

    def report(self, stream):
        report = self.pep8.check_files()
        stream.write('\n' + "PEP8:" + '\n')
        report.get_file_results(stream)
        if self.tissue_statistics:
            stats = '\n'.join(report.get_statistics())
            stream.write(stats + '\n')

    def wantFile(self, file, package=None):
        if self.tissue_inclusive:
            if file.endswith(".py"):
                if package and self.tissue_packages:
                    for want in self.tissue_packages:
                        if package.startswith(want):
                            return True
                else:
                    return True
        return None
