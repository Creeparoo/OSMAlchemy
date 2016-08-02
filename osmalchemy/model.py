# ~*~ coding: utf-8 ~*~

""" Simple representation of OpenStreetMap's conceptual data model.
(cf. http://wiki.openstreetmap.org/wiki/Elements)

This implementation of the model assumes that only current data is used,
not historic data.
"""

class Node():
    id = None
    latitude = None
    longitude = None
    # tags

class Way():
    id = None
    # nodes (2 - 2000)
    # tags

class Relation():
    id = None
    # tags
    # members (with role)

class Tag():
    key = None
    value = None
