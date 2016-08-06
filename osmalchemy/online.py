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

""" Utility code for OSMAlchemy's online functionality. """

import overpass

def _generate_overpass_api(endpoint=None):
    """ Create and initialise the Overpass API object.

    Passing the endpoint argument will override the default
    endpoint URL.
    """

    # Create API object with default settings
    api = overpass.API()

    # Change endpoint if desired
    if endpoint is not None:
        api.endpoint = endpoint

    return api

def _get_single_element_by_id(api, type, id, recurse_down=True):
    """ Retrieves a single OpenStreetMap element by its id.

      api - an initialised Overpass API object
      type - the element type to query, one of node, way or relation
      id - the id of the element to retrieve
      recurse_down - whether to get child nodes of ways and relations
    """

    # Construct query
    q = "%s(%d);%s" % (type, id, "(._;>;);" if recurse_down else "")

    # Run query
    r = api.Get(q, responseformat="xml")

    # Return data
    return r
