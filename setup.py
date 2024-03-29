#!/usr/bin/env python

from setuptools import setup

setup(name='BnW',
    version='0.1',
    description='Microblogging service',
    author='Stiletto',
    author_email='blasux@blasux.ru',
    url='http://github.com/stiletto/bnw',
    packages=['bnw', 'bnw.core', 'bnw.formatting', 'bnw.handlers', 'bnw.scripts', 'bnw.search', 'bnw.web', 'bnw.xmpp'],
    dependency_links=['http://github.com/mongodb/motor/tarball/master#egg=motor-0.1.2',
                      'http://github.com/mongodb/mongo-python-driver/tarball/master#egg=pymongo-2.6',
                      'https://github.com/stiletto/linkshit/archive/refs/tags/0.2.tar.gz#egg=linkshit-0.2'],

    install_requires=['tornado>=2.0,<6.0', 'twisted<16.3.0', 'Pillow<7', 'PyRSS2Gen', 'python-dateutil', 'misaka<2.0.0', 'motor==0.7', 'linkshit', 'libthumbor', 'singledispatch<3.6'],
    package_data={'bnw.web': ['templates/*.html','static/*.*', 'static/flot/*', 'static/web-socket-js/*']},
    entry_points = {
        'console_scripts': [
            'bnw = bnw.scripts.entry:instance',
            'bnw-search = bnw.scripts.entry:search',
            'bnw-admin = bnw.scripts.admin:main',
        ],
    }
)
