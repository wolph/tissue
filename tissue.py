"""
PEP8 automated checker for nose. Based on coverage plugin
"""
import logging
import os

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


class Tissue(plugins.Plugin):
    """Automated PEP8 checked for nose"""

    name = "tissue"

    def begin(self):
        self.messages = []
        self.seen = []

    def beforeDirectory(self, path):
        def seen_runner(filename):
            if filename not in self.seen:
                pep8.input_file(filename)
                self.seen.append(filename)
        pep8.input_dir(path, runner=seen_runner)

    def beforeImport(self, filename, module):
        if filename.endswith(".py") and filename not in self.seen:
            pep8.input_file(filename)
            self.seen.append(filename)

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
                     self.coverPackages)

        # NOTE(jkoelker) Monkey-patch pep8 to not print directly
        def message(text):
            # if the output has a filename, then it should be colored if
            # the tissue_color option is used
            if ':' in text and os.path.exists(text.split(':')[0]):
                if options.tissue_color:
                    if 'E' in text.split(':')[-1]:
                        text = in_color('red', text)
                    else:
                        text = in_color('yellow', text)

                # if using the tissue_show_source or tissue_show_pep8, it
                # should separate the filename from the information
                if options.tissue_show_pep8 or options.tissue_show_source:
                    text = "\n%s\n" % text

            self.messages.append(text)

        pep8.message = message

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

        # NOTE(jkoelker) PEP8 requires something to be left over in args
        arglist.append("hozer")

        tissue_options, tissue_args = pep8.process_options(arglist)

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
                          default=env.get("NOSE_tissue_INCLUSIVE"),
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
        if not self.messages:
            return
        stream.write('\n' + "PEP8:" + '\n')
        output = '\n'.join(self.messages)
        stream.write(output + '\n')
        if self.tissue_statistics:
            stats = '\n'.join(pep8.get_statistics())
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
