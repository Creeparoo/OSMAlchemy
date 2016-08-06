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

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session
try:
    from flask_sqlalchemy import SQLAlchemy as FlaskSQLAlchemy
except ImportError:
    # non-fatal, Flask-SQLAlchemy support is optional
    # Create stub to avoid bad code later on
    class FlaskSQLAlchemy(object):
        pass

from .model import _generate_model
from .online import _generate_overpass_api
from .util import _import_osm_file
from .triggers import _generate_triggers

class OSMAlchemy(object):
    """ Wrapper class for the OSMAlchemy model and logic

    This class holds all the SQLAlchemy classes and logic that make up
    OSMAlchemy. It is contained in a separate class because it is a
    template that can be modified as needed by users, e.g. by using a
    different table prefix or a different declarative base.
    """

    def __init__(self, sa, prefix="osm_", overpass=None, maxage=60*60*24):
        """ Initialise the table definitions in the wrapper object

        This function generates the OSM element classes as SQLAlchemy table
        declaratives.

        Positional arguments:

          sa - reference to SQLAlchemy stuff; can be either of…
                 …an Engine instance, or…
                 …a tuple of (Engine, Base), or…
                 …a tuple of (Engine, Base, ScopedSession), or…
                 …a Flask-SQLAlchemy instance.
          prefix - optional; prefix for table names, defaults to "osm_"
          overpass - optional; API endpoint URL for Overpass API. Can be…
                      …None to disable loading data from Overpass (the default), or…
                      …True to enable the default endpoint URL, or…
                      …a string with a custom endpoint URL.
          maxage - optional; the maximum age after which elements are refreshed from
                   Overpass, in seconds, defaults to 86400s (1d)
        """

        # Create fields for SQLAlchemy stuff
        self.base = None
        self.engine = None
        self.session = None

        # Inspect sa argument
        if type(sa) is tuple:
            self._engine = sa[0]
            self._base = sa[1]
            if len(sa) == 3:
                self._session = sa[2]
        elif type(sa) is Engine:
            self._engine = sa
            self._base = declarative_base(bind=self._engine)
            self._session = scoped_session(sessionmaker(bind=self._engine))
        elif type(sa) is FlaskSQLAlchemy:
            self._engine = sa.engine
            self._base = sa.Model
            self._session = sa.session
        else:
            raise TypeError("Invalid argument passed to sa parameter.")

        # Store prefix
        self._prefix = prefix

        # Store API endpoint for Overpass
        if overpass is not None:
            if overpass is True:
                self._overpass = _generate_overpass_api()
            else:
                self._overpass = _generate_overpass_api(overpass)
        else:
            self._overpass = None

        # Generate model and store as instance members
        self.Node, self.Way, self.Relation, self.Element = _generate_model(self._base,
                                                                           self._prefix)

        # Add triggers if online functionality is enabled
        if self._overpass is not None:
            _generate_triggers(self, maxage)

    def import_osm_file(self, session, path):
        _import_osm_file(self, session, path)
