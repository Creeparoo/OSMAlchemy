# ~*~ coding: utf-8 ~*~

""" Simple representation of OpenStreetMap's conceptual data model.
(cf. http://wiki.openstreetmap.org/wiki/Elements)

This implementation of the model assumes that only current data is used,
not historic data.
"""

import datetime
from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

class OSMAlchemy(object):
    """ Wrapper class for the OSMAlchemy model """

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
            base = declarative_base()
        elif hasattr(base, "Model"):
            # Unwrap Flask-SQLAlchemy object if we got one
            base = base.Model

        class OSMElement(base):
            """ Base class for all the conceptual OSM elements. """

            __tablename__ = prefix + "elements"

            element_id = Column(Integer, primary_key=True)
            updated = Column(DateTime, default=datetime.datetime.now,
                             onupdate=datetime.datetime.now)
            type = Column(String)
            tags = relationship('OSMTag', secondary=prefix+'elements_tags')

            __mapper_args__ = {
                'polymorphic_identity': prefix + 'elements',
                'polymorphic_on': type,
                'with_polymorphic': '*'
            }

        class OSMNode(OSMElement):
            """ An OSM node element.

            A node hast a latitude and longitude, which are non-optional,
            and a list of zero or more tags.
            """

            __tablename__ = prefix + "nodes"

            element_id = Column(Integer, ForeignKey(prefix + 'elements.element_id'),
                                primary_key=True)
            latitude = Column(Float, nullable=False)
            longitude = Column(Float, nullable=False)

            __mapper_args__ = {
                'polymorphic_identity': prefix + 'nodes',
            }

            def __init__(self, latitude=0.0, longitude=0.0, **kwargs):
                """ Initialisation with two main positional arguments. """

                self.latitude = latitude
                self.longitude = longitude

                # Pass rest on to default constructor
                OSMElement.__init__(self, **kwargs)

        class OSMWay(OSMElement):
            """ An OSM way element (also area).

            Contains a list of two or more nodes and a list of zero or more
            tags.
            """

            __tablename__ = prefix + "ways"

            element_id = Column(Integer, ForeignKey(prefix + 'elements.element_id'),
                                primary_key=True)
            nodes = relationship('OSMNode', secondary=prefix+'ways_nodes')

            __mapper_args__ = {
                'polymorphic_identity': prefix + 'ways',
            }

        class OSMElementsTags(base):
            """ Secondary mapping table for elements and tags """

            __tablename__ = prefix + "elements_tags"

            map_id = Column(Integer, primary_key=True)
            element_id = Column(Integer, ForeignKey(prefix + 'elements.element_id'))
            tag_id = Column(Integer, ForeignKey(prefix + 'tags.tag_id'))

        class OSMWaysNodes(base):
            """ Secondary mapping table for ways and nodes """

            __tablename__ = prefix + "ways_nodes"

            map_id = Column(Integer, primary_key=True)
            way_id = Column(Integer, ForeignKey(prefix + 'ways.element_id'))
            node_id = Column(Integer, ForeignKey(prefix + 'nodes.element_id'))

        class OSMRelationsElements(base):
            """ Secondary mapping table for relation members """

            __tablename__ = prefix + "relations_elements"

            map_id = Column(Integer, primary_key=True)
            relation_id = Column(Integer, ForeignKey(prefix + 'relations.element_id'))
            element_id = Column(Integer, ForeignKey(prefix + 'elements.element_id'))
            role = Column(String)

        class OSMRelation(OSMElement):
            """ An OSM relation element.

            Contains zero or more members (ways, nodes or other relations)
            with associated, optional roles and zero or more tags.
            """

            __tablename__ = prefix + "relations"

            element_id = Column(Integer, ForeignKey(prefix + 'elements.element_id'),
                                primary_key=True)
            members = relationship("OSMElement", secondary=prefix+"relations_elements")

            __mapper_args__ = {
                'polymorphic_identity': prefix + 'relations',
            }

        class OSMTag(base):
            """ An OSM tag element.

            Simple key/value pair.
            """

            __tablename__ = prefix + "tags"

            tag_id = Column(Integer, primary_key=True)
            key = Column(String)
            value = Column(String)

            def __init__(self, key="", value="", **kwargs):
                """ Initialisation with two main positional arguments. """

                self.key = key
                self.value = value

                # Pass rest on to default constructor
                base.__init__(self, **kwargs)


        # Set the classes as members of the wrapper object
        self.Node = OSMNode #pylint: disable=invalid-name
        self.Way = OSMWay #pylint: disable=invalid-name
        self.Relation = OSMRelation #pylint: disable=invalid-name
        self.Tag = OSMTag #pylint: disable=invalid-name

        # Store generation attributes
        self._base = base
        self._prefix = prefix
