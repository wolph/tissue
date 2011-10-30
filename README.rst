tissue - PEP8 automated checker for nose
========================================

tissue integrates running pep8 on source files as they are imported by nose.

Installation
------------

    pip install tissue

Usage
-----

Once installed pep8 tissue will run pep8 checks on your source tree. The
following options are availible:

    --with-tissue         Enable plugin Tissue: Automated PEP8 checked for nose
                          [NOSE_WITH_TISSUE]
    --tissue-package=PACKAGE
                          Restrict pep8 output to selected packages
                          [NOSE_TISSUE_PACKAGE]
    --tissue-inclusive    Include all python files under working directory in
                          pep8 run. [NOSE_TISSUE_INCLUSIVE]
    --tissue-repeat       Show all occurrences of the same error
                          [NOSE_TISSUE_REPEAT]
    --tissue-select=ERRORS
                          Select errors and warnings (e.g. E,W6)
                          [NOSE_TISSUE_SELECT]
    --tissue-ignore=ERRORS
                          Skip errors and warnings (e.g. E,W6)
                          [NOSE_TISSUE_IGNORE]
    --tissue-show-source  Show source code for each error
                          [NOSE_TISSUE_SHOW_SOURCE]
    --tissue-show-pep8    Show text of PEP 8 for each error
                          [NOSE_TISSUE_SHOW_TISSUE]
    --tissue-statistics   Count errors and warnings [NOSE_TISSUE_STATISTICS]
    --tissue-color        Show errors and warnings using colors
                          [NOSE_TISSUE_COLOR]

Options map to the pep8 options of the same name (sans prefix)

Source
------

Fork me on teh githubs

https://github.com/jkoelker/tissue
