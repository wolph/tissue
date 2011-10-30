from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='tissue',
      version=version,
      description="Tissue - automated pep8 checker for nose",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jason K\xc3\xb6lker',
      author_email='jason@koelker.net',
      url='https://github.com/jkoelker/tissue',
      license='GNU LGPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
