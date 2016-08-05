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

""" Simple representation of OpenStreetMap's conceptual data model.
(cf. http://wiki.openstreetmap.org/wiki/Elements)

This implementation of the model assumes that only current data is used,
not historic data.
"""

import datetime
from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Float, String, DateTime, Boolean,
                       UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection

def _generate_model(base, prefix="osm_"):
    """ Generates the data model.

    The model classes are generated dynamically to allow passing in a
    declarative base and a prefix.
    """

    class OSMTag(base):
        """ An OSM tag element.

        Simple key/value pair.
        """

        # Name of the table in the database, prefix provided by user
        __tablename__ = prefix + "tags"

        # The internal ID of the element, only for structural use
        tag_id = Column(BigInteger, primary_key=True)

        # Key/value pair
        key = Column(String(256))
        value = Column(String(256))

        def __init__(self, key="", value="", **kwargs):
            """ Initialisation with two main positional arguments.

            Shorthand for OSMTag(key, value)
            """

            self.key = key
            self.value = value

            # Pass rest on to default constructor
            base.__init__(self, **kwargs)

    class OSMElement(base):
        """ Base class for all the conceptual OSM elements. """

        # Name of the table in the database, prefix provided by user
        __tablename__ = prefix + "elements"

        # The internal ID of the element, only for structural use
        element_id = Column(BigInteger, primary_key=True)

        # Track element modification for OSMAlchemy caching
        osmalchemy_updated = Column(DateTime, default=datetime.datetime.now,
                                    onupdate=datetime.datetime.now)

        # The type of the element, used by SQLAlchemy for polymorphism
        type = Column(String(256))

        # ID of the element in OSM, not to be confused with the primary key element_id
        id = Column(BigInteger)

        # Tags belonging to the element
        # Accessed as a dictionary like {'name': 'value', 'name2': 'value2',…}
        # Uses proxying across several tables to OSMTag
        tags = association_proxy(prefix+"elements_tags", "tag_value",
                                 creator=lambda k, v: OSMElementsTags(tag_key=k, tag_value=v))

        # Metadata shared by all element types
        version = Column(Integer)
        changeset = Column(BigInteger)
        user = Column(String(256))
        uid = Column(BigInteger)
        visible = Column(Boolean)
        timestamp = Column(DateTime)

        # OSM ids are unique per type
        _u_type_id = UniqueConstraint("type", "id")

        # Configure polymorphism
        __mapper_args__ = {
            'polymorphic_identity': 'element',
            'polymorphic_on': type,
            'with_polymorphic': '*'
        }

    class OSMElementsTags(base):
        """ Secondary mapping table for elements and tags """

        # Name of the table in the database, prefix provided by user
        __tablename__ = prefix + "elements_tags"

        # Internal ID of the mapping, only for structural use
        map_id = Column(BigInteger, primary_key=True)

        # Foreign key columns for the element and tag of the mapping
        element_id = Column(BigInteger, ForeignKey(prefix + 'elements.element_id'))
        tag_id = Column(BigInteger, ForeignKey(prefix + 'tags.tag_id'))

        # Relationship with all the tags mapped to the element
        # The backref is the counter-part to the tags association proxy
        # in OSMElement to form the dictionary
        element = relationship(OSMElement, foreign_keys=[element_id],
                               backref=backref(prefix+"elements_tags",
                                               collection_class=attribute_mapped_collection("tag_key"),
                                               cascade="all, delete-orphan"))

        # Relationship to the tag object and short-hand for its key and value
        # for use in the association proxy
        tag = relationship(OSMTag, foreign_keys=[tag_id])
        tag_key = association_proxy("tag", "key")
        tag_value = association_proxy("tag", "value")

    class OSMNode(OSMElement):
        """ An OSM node element.

        A node hast a latitude and longitude, which are non-optional,
        and a list of zero or more tags.
        """

        # Name of the table in the database, prefix provided by user
        __tablename__ = prefix + "nodes"

        # The internal ID of the element, only for structural use
        # Synchronised with the id of the parent table OSMElement through polymorphism
        element_id = Column(BigInteger, ForeignKey(prefix + 'elements.element_id'),
                            primary_key=True)


        # Geographical coordinates of the node
        latitude = Column(Float, nullable=False)
        longitude = Column(Float, nullable=False)

        # Configure polymorphism with OSMElement
        __mapper_args__ = {
            'polymorphic_identity': 'node',
        }

        def __init__(self, latitude=0.0, longitude=0.0, **kwargs):
            """ Initialisation with two main positional arguments.

            Shorthand for OSMNode(lat, lon).
            """

            self.latitude = latitude
            self.longitude = longitude

            # Pass rest on to default constructor
            OSMElement.__init__(self, **kwargs)

    class OSMWaysNodes(base):
        """ Secondary mapping table for ways and nodes """

        # Name of the table in the database, prefix provided by user
        __tablename__ = prefix + "ways_nodes"

        # Internal ID of the mapping, only for structural use
        map_id = Column(BigInteger, primary_key=True)

        # Foreign key columns for the connected way and node
        way_id = Column(BigInteger, ForeignKey(prefix + 'ways.element_id'))
        node_id = Column(BigInteger, ForeignKey(prefix + 'nodes.element_id'))
        # Relationships for proxy access
        node = relationship(OSMNode, foreign_keys=[node_id])

        # Index of the node in the way to maintain ordered list, structural use only
        position = Column(Integer)

    class OSMWay(OSMElement):
        """ An OSM way element (also area).

        Contains a list of two or more nodes and a list of zero or more
        tags.
        """

        # Name of the table in the database, prefix provided by user
        __tablename__ = prefix + "ways"

        # The internal ID of the element, only for structural use
        # Synchronised with the id of the parent table OSMElement through polymorphism
        element_id = Column(BigInteger, ForeignKey(prefix + 'elements.element_id'),
                            primary_key=True)

        # Relationship with all nodes in the way
        # Uses association proxy and a collection class to maintain an ordered list,
        # synchronised with the position field of OSMWaysNodes
        _nodes = relationship(OSMWaysNodes, order_by="OSMWaysNodes.position",
                              collection_class=ordering_list("position"))
        nodes = association_proxy("_nodes", "node",
                                  creator=lambda _n: OSMWaysNodes(node=_n))

        # Configure polymorphism with OSMElement
        __mapper_args__ = {
            'polymorphic_identity': 'way',
        }

    class OSMRelationsElements(base):
        """ Secondary mapping table for relation members """

        # Name of the table in the database, prefix provided by user
        __tablename__ = prefix + "relations_elements"

        # Internal ID of the mapping, only for structural use
        map_id = Column(BigInteger, primary_key=True)

        # Foreign ley columns for the relation and other element of the mapping
        relation_id = Column(BigInteger, ForeignKey(prefix + 'relations.element_id'))
        element_id = Column(BigInteger, ForeignKey(prefix + 'elements.element_id'))
        # Relationships for proxy access
        element = relationship(OSMElement, foreign_keys=[element_id])

        # Role of the element in the relationship
        role = Column(String(256))

        # Index of element in the relationship to maintain ordered list, structural use only
        position = Column(Integer)

        # Produce (element, role) tuple for proxy access in OSMRelation
        @property
        def role_tuple(self):
            return (self.element, self.role)

    class OSMRelation(OSMElement):
        """ An OSM relation element.

        Contains zero or more members (ways, nodes or other relations)
        with associated, optional roles and zero or more tags.
        """

        # Name of the table in the database, prefix provided by user
        __tablename__ = prefix + "relations"

        # The internal ID of the element, only for structural use
        # Synchronised with the id of the parent table OSMElement through polymorphism
        element_id = Column(BigInteger, ForeignKey(prefix + 'elements.element_id'),
                            primary_key=True)

        # Relationship to the members of the relationship, proxied across OSMRelationsElements
        _members = relationship(OSMRelationsElements,
                                order_by="OSMRelationsElements.position",
                                collection_class=ordering_list("position"))
        # Accessed as a list like [(element, "role"), (element2, "role2")]
        members = association_proxy("_members", "role_tuple",
                                    creator=lambda _m: OSMRelationsElements(element=_m[0],
                                                                            role=_m[1]))

        # Configure polymorphism with OSMElement
        __mapper_args__ = {
            'polymorphic_identity': 'relation',
        }

    # Return the relevant generated objects
    return (OSMNode, OSMWay, OSMRelation, OSMElement)
