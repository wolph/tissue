"""
PEP8 automated checker for nose. Based on coverage plugin
"""
import logging

from nose import plugins
from nose import util


log = logging.getLogger("nose.plugins.tissue")


class Tissue(plugins.Plugin):
    name = "tissue"

    def begin(self):
        self.messages = []

    def beforeImport(self, filename, module):
        self.input_file(filename)

    def configure(self, options, config):
        try:
            self.status.pop("active")
        except KeyError:
            pass
        plugins.Plugin.configure(self, options, config)
        if self.enabled:
            try:
                import pep8
            except ImportError:
                log.error("PEP8 not availible: "
                          "unable to import pep8 module")
                self.enabled = False
                return
        self.conf = config
        self.pep8_packages = []
        self.pep8_tests = options.pep8_tests
        self.pep8_statistics = options.pep8_statistics
        if options.pep8_packages:
            for pkgs in [util.tolist(x) for x in options.pep8_packages]:
                self.pep8_packages.exted(pkgs)
        self.pep8_inclusive = options.pep8_inclusive
        if self.pep8_packages:
            log.info("PEP8 report will include only packages: %s",
                     self.coverPackages)
        if self.enabled:
            self.status["active"] = True

        # NOTE(jkoelker) Monkey-patch pep8 to not print directly
        def message(text):
            self.messages.append(text)

        pep8.message = message
        self.get_statistics = pep8.get_statistics
        self.input_file = pep8.input_file

        # NOTE(jkoelker) Urgh! Really? Global options? At least there is a
        #                function that takes the arglist ;(
        arglist = []
        if options.pep8_repeat:
            arglist.append("--repeat")

        if options.pep8_select:
            arglist.append("--select")
            arglist.append(options.select)

        if options.pep8_ignore:
            arglist.append("--ignore")
            arglist.append(options.ignore)

        if options.pep8_show_source:
            arglist.append("--show-source")

        if options.pep8_show_pep8:
            arglist.append("--show-pep8")

        pep8_options, pep8_args = pep8.process_options(arglist)

    def options(self, parser, env):
        plugins.Plugin.options(self, parser, env)
        parser.add_option("--pep8-package", action="append",
                          default=env.get("NOSE_PEP8_PACKAGE"),
                          metavar="PACKAGE",
                          dest="pep8_packages",
                          help="Restrict pep8 output to selected packages "
                               "[NOSE_PEP8_PACKAGE]")
        parser.add_option("--pep8-tests", action="store_true",
                          dest="pep8_tests",
                          default=env.get("NOSE_PEP8_TESTS"),
                          help="Include test modules in pep8 "
                               "[NOSE_PEP8_TESTS]")
        parser.add_option("--pep8-inclusive", action="store_true",
                          dest="pep8_inclusive",
                          default=env.get("NOSE_pep8_INCLUSIVE"),
                          help="Include all python files under working "
                               "directory in pep8 run. "
                               "[NOSE_PEP8_INCLUSIVE]")
        parser.add_option("--pep8-repeat", action="store_true",
                          default=env.get("NOSE_PEP8_REPEAT"),
                          metavar="ERRORS",
                          dest="pep8_repeat",
                          help="Show all occurrences of the same error "
                               "[NOSE_PEP8_REPEAT]")
        parser.add_option("--pep8-select",
                          default=env.get("NOSE_PEP8_SELECT"),
                          metavar="ERRORS",
                          dest="pep8_select",
                          help="Select errors and warnings (e.g. E,W6) "
                               "[NOSE_PEP8_SELECT]")
        parser.add_option("--pep8-ignore",
                          default=env.get("NOSE_PEP8_ignore"),
                          metavar="ERRORS",
                          dest="pep8_ignore",
                          help="Skip errors and warnings (e.g. E,W6) "
                               "[NOSE_PEP8_IGNORE]")
        parser.add_option("--pep8-show-source", action="store_true",
                          dest="pep8_show_source",
                          default=env.get("NOSE_PEP8_SHOW_SOURCE"),
                          help="Show source code for each error "
                               "[NOSE_PEP8_SHOW_SOURCE]")
        parser.add_option("--pep8-show-pep8", action="store_true",
                          dest="pep8_show_pep8",
                          default=env.get("NOSE_PEP8_SHOW_PEP8"),
                          help="Show text of PEP 8 for each error "
                               "[NOSE_PEP8_SHOW_PEP8]")
        parser.add_option("--pep8-statistics", action="store_true",
                          dest="pep8_statistics",
                          default=env.get("NOSE_PEP8_STATISTICS"),
                          help="Count errors and warnings "
                               "[NOSE_PEP8_STATISTICS]")

    def report(self, stream):
        output = '\n'.join(self.messages)
        stream.write('\n' + output + '\n')
        if self.pep8_statistics:
            stats = '\n'.join(self.get_statistics())
            stream.write(stats + '\n')

    def wantFile(self, file, package=None):
        if self.inclusive:
            if file.endswith(".py"):
                if package and self.pep8_packages:
                    for want in self.pep8_packages:
                        if package.startswith(want):
                            return True
                else:
                    return True
        return None


