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

""" Module that holds the main OSMAlchemy class.

The classe encapsulates the model and accompanying logic.
"""

from .model import _generate_model
from .util import _import_osm_file

class OSMAlchemy(object):
    """ Wrapper class for the OSMAlchemy model and logic

    This class holds all the SQLAlchemy classes and logic that make up
    OSMAlchemy. It is contained in a separate class because it is a
    template that can be modified as needed by users, e.g. by using a
    different table prefix or a different declarative base.
    """

    def __init__(self, base=None, prefix="osm_"):
        """ Initialise the table definitions in the wrapper object

        This function generates the OSM element classes as SQLAlchemy table
        declaratives. If called without an argument, it uses a newly created
        declarative base.

        The base argument, if provided, can be either a declarative base or
        a Flask-SQLAlchemy object.
        """

        # Check what we got as declarative base
        if base is None:
            # Nothing, so create one
            self._base = declarative_base()
        elif hasattr(base, "Model"):
            # Unwrap Flask-SQLAlchemy object if we got one
            self._base = base.Model
        else:
            self._base = base

        # Store prefix
        self._prefix = prefix

        # Generate model and store as instance members
        self.Node, self.Way, self.Relation, self.Element = _generate_model(self._base,
                                                                           self._prefix)

    def import_osm_file(self, path):
        _import_osm_file(self, path)
