#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

from setuptools import setup, find_packages

setup(
    # Basic information
    name = 'OSMAlchemy',
    version = '0.1',
    license = 'MIT',
    keywords = 'osm openstreetmap proxy caching orm',
    description = 'OpenStreetMap to SQLAlchemy bridge',
    url = 'https://github.com/Natureshadow/OSMAlchemy',

    # Author information
    author = 'Dominik George',
    author_email = 'nik@naturalnet.de',

    # Included code
    packages = find_packages(),

    # Distribution information
    zip_safe = True,
    install_requires = [
                        'SQLAlchemy>=1.0.0',
                       ],
    tests_require = [
                     'testing.postgresql'
                    ],
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
