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

""" Trigger code for live OSMAlchemy/Overpass integration. """

import datetime
from sqlalchemy import inspect
from sqlalchemy.event import listens_for
from sqlalchemy.orm import Query
from weakref import WeakSet

from .online import _get_single_element_by_id
from .util import _import_osm_xml

def _generate_triggers(osmalchemy, maxage=60*60*24):
    """ Generates the triggers for online functionality.

      osmalchemy - reference to the OSMAlchemy instance to be configured
      maxage - maximum age of objects before they are updated online, in seconds
    """

    _visited_queries = WeakSet()

    @listens_for(Query, "before_compile")
    def _query_compiling(query):
        # Get the session associated with the query:
        session = query.session

        # Prevent recursion by skipping already-seen queries
        if query in _visited_queries:
            return
        else:
            _visited_queries.add(query)

        # FIXME actually implement
        return
