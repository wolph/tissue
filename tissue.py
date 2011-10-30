"""
PEP8 automated checker for nose. Based on coverage plugin
"""
import logging

import pep8

from nose import plugins
from nose import util


log = logging.getLogger("nose.plugins.tissue")


class Tissue(plugins.Plugin):
    """Automated PEP8 checked for nose"""

    name = "tissue"

    def begin(self):
        self.messages = []

    def beforeImport(self, filename, module):
        if filename.endswith(".py"):
            pep8.input_file(filename)

    def configure(self, options, config):
        plugins.Plugin.configure(self, options, config)
        self.conf = config
        self.tissue_packages = []
        self.tissue_statistics = options.tissue_statistics
        if options.tissue_packages:
            for pkgs in [util.tolist(x) for x in options.tissue_packages]:
                self.tissue_packages.exted(pkgs)
        self.tissue_inclusive = options.tissue_inclusive
        if self.tissue_packages:
            log.info("PEP8 report will include only packages: %s",
                     self.coverPackages)

        # NOTE(jkoelker) Monkey-patch pep8 to not print directly
        def message(text):
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

    def report(self, stream):
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
