from setuptools import setup

version = '0.9.1'

setup(
    name='tissue',
    version=version,
    description='Tissue - automated pep8 checker for nose',
    long_description=open('README.rst').read(),
    classifiers=[],
    keywords='pep8 nose',
    author='Jason K\xc3\xb6lker & Rick van Hattem',
    author_email='rick@wol.ph',
    url='https://github.com/jkoelker/tissue',
    license='GNU LGPL',
    py_modules=['tissue'],
    install_requires=[
        'nose',
        'pep8',
    ],
    entry_points={
        'nose.plugins': [
            'tissue = tissue:Tissue',
        ],
    },
)
