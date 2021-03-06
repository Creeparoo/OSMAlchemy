#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
#-
# OSMAlchemy - OpenStreetMap to SQLAlchemy bridge
# Copyright (c) 2016 Dominik George <nik@naturalnet.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Alternatively, you are free to use OSMAlchemy under Simplified BSD, The
# MirOS Licence, GPL-2+, LGPL-2.1+, AGPL-3+ or the same terms as Python
# itself.

from setuptools import setup

setup(
    # Basic information
    name = 'OSMAlchemy',
    version = '0.1',
    keywords = 'osm openstreetmap proxy caching orm',
    description = 'OpenStreetMap to SQLAlchemy bridge',
    url = 'https://github.com/Natureshadow/OSMAlchemy',

    # Author information
    author = 'Dominik George',
    author_email = 'nik@naturalnet.de',

    # Included code
    packages = ["osmalchemy"],

    # Distribution information
    zip_safe = True,
    install_requires = [
                        'SQLAlchemy>=1.0.0',
                        'python-dateutil',
                        'overpass'
                       ],
    tests_require = [
                     'SQLAlchemy>=1.0.0',
                     'python-dateutil',
                     'overpass',
                     'psycopg2',
                     'Flask>=0.10',
                     'Flask-SQLAlchemy',
                     'testing.postgresql',
                     'testing.mysqld'
                    ],
    extras_require = {
                      'Flask': [
                                'Flask>=0.10',
                                'Flask-SQLAlchemy'
                               ]
                     },
    test_suite = 'tests',
    classifiers = [
                   'Development Status :: 3 - Alpha',
                   'Environment :: Plugins',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Topic :: Database',
                   'Topic :: Scientific/Engineering :: GIS',
                   'Topic :: Software Development :: Libraries :: Python Modules'
                  ]
)
