#!/usr/bin/env python

from setuptools import setup

setup(name='BnW',
    version='0.1',
    description='Microblogging service',
    author='Stiletto',
    author_email='blasux@blasux.ru',
    url='http://github.com/stiletto/bnw',
    packages=['bnw', 'bnw.core', 'bnw.handlers', 'bnw.scripts', 'bnw.search', 'bnw.web', 'bnw.xmpp'],
    install_requires=['tornado>=2.0', 'twisted', 'Pillow', 'PyRSS2Gen', 'misaka'],
    entry_points = {
        'console_scripts': [
            'bnw = bnw.scripts.entry:instance',
            'bnw-search = bnw.scripts.entry:search',
        ],
    }
)
