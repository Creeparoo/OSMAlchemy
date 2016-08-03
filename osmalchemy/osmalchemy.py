# ~*~ coding: utf-8 ~*~

""" Simple representation of OpenStreetMap's conceptual data model.
(cf. http://wiki.openstreetmap.org/wiki/Elements)

This implementation of the model assumes that only current data is used,
not historic data.
"""

import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, relationship
from sqlalchemy.ext.declarative import declarative_base

class OSMAlchemy():
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
            base = declarativ_base()
        elif hasattr(base, "Model"):
            # Unwrap Flask-SQLAlchemy object if we got one
            base = base.Model

        class OSMElement(base):
            """ Base class for all the conceptual OSM elements. """

            __abstract__ = True

            id = Column(Integer, primary_key=True)
            updated = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

        class OSMNode(OSMElement):
            """ An OSM node element.

            A node hast a latitude and longitude, which are non-optional,
            and a list of zero or more tags.
            """

            __tablename__ = prefix + "nodes"

            latitude = Column(Float, nullable=False)
            longitude = Column(Float, nullable=False)
            tags = relationship('OSMTag')

        class OSMWay(OSMElement):
            """ An OSM way element (also area).

            Contains a list of two or more nodes and a list of zero or more
            tags.
            """

            __tablename__ = prefix + "ways"

            nodes = relationship('OSMNode')
            tags = relationship('OSMTag')

        class OSMRelation(OSMElement):
            """ An OSM relation element.

            Contains zero or more members (ways, nodes or other relations)
            with associated, optional roles and zero or more tags.
            """

            __tablename__ = prefix + "relations"

            # members (with role)
            tags = relationship('OSMTag')

        class OSMTag(base):
            """ An OSM tag element.

            Simple key/value pair.
            """

            __tablename__ = prefix + "tags" 

            # Not inheriting from OSMElement but defining our own, internal
            # id, as the tag element does not really exist and we only need
            # this id to track in SQL and above all, we do not need tracking
            # of update time and the like.
            id = Column(Integer, primary_key=True)

            key = Column(String)
            value = Column(String)

        # Set the classes as members of the wrapper object
        self.Node = OSMNode
        self.Way = OSMWay
        self.Relation = OSMRelation
        self.Tag = OSMTag