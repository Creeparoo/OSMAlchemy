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

""" Utility code for OSMAlchemy. """

import dateutil.parser
import operator
import xml.dom.minidom as minidom
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList, BindParameter
from sqlalchemy.sql.annotation import AnnotatedColumn

def _import_osm_dom(osma, session, dom):
    """ Import a DOM tree from OSM XML into an OSMAlchemy model.

    Not called directly; used by _import_osm_xml and _import_osm_file.
    """

    def _dom_attrs_to_any(e, element):
        if "version" in e.attributes.keys():
            element.version = int(e.attributes["version"].value)
        if "changeset" in e.attributes.keys():
            element.changeset = int(e.attributes["changeset"].value)
        if "user" in e.attributes.keys():
            element.user = e.attributes["user"].value
        if "uid" in e.attributes.keys():
            element.uid = int(e.attributes["uid"].value)
        if "visible" in e.attributes.keys():
            element.visible = True if e.attributes["visible"].value == "true" else False
        if "timestamp" in e.attributes.keys():
            element.timestamp = dateutil.parser.parse(e.attributes["timestamp"].value)

    def _dom_tags_to_any(e, element):
        # Target dictionary
        tags = {}

        # Iterate over all <tag /> nodes in the DOM element
        for t in e.getElementsByTagName("tag"):
            # Append data to tags
            tags[t.attributes["k"].value] = t.attributes["v"].value

        # Store tags dictionary in object
        element.tags = tags

    def _dom_to_node(e):
        with session.no_autoflush:
            # Get mandatory node id
            id = int(e.attributes["id"].value)

            # Find object in database and create if non-existent
            node = session.query(osma.node).filter_by(id=id).scalar()
            if node is None:
                node = osma.node(id=id)

            # Store mandatory latitude and longitude
            node.latitude = e.attributes["lat"].value
            node.longitude = e.attributes["lon"].value

            # Store other attributes and tags
            _dom_attrs_to_any(e, node)
            _dom_tags_to_any(e, node)

        # Add to session
        session.add(node)
        session.commit()

    def _dom_to_way(e):
        with session.no_autoflush:
            # Get mandatory way id
            id = int(e.attributes["id"].value)

            # Find object in database and create if non-existent
            way = session.query(osma.way).filter_by(id=id).scalar()
            if way is None:
                way = osma.way(id=id)

            # Find all related nodes
            for n in e.getElementsByTagName("nd"):
                # Get node id and find object
                ref = int(n.attributes["ref"].value)
                node = session.query(osma.node).filter_by(id=ref).one()
                # Append to nodes in way
                way.nodes.append(node)

            # Store other attributes and tags
            _dom_attrs_to_any(e, way)
            _dom_tags_to_any(e, way)

        # Add to session
        session.add(way)
        session.commit()

    def _dom_to_relation(e):
        with session.no_autoflush:
            # Get mandatory way id
            id = int(e.attributes["id"].value)

            # Find object in database and create if non-existent
            relation = session.query(osma.relation).filter_by(id=id).scalar()
            if relation is None:
                relation = osma.relation(id=id)

            # Find all members
            for m in e.getElementsByTagName("member"):
                # Get member attributes
                ref = int(m.attributes["ref"].value)
                type = m.attributes["type"].value

                if "role" in m.attributes.keys():
                    role = m.attributes["role"].value
                else:
                    role = ""
                element = session.query(osma.element).filter_by(id=ref, type=type).scalar()
                if element is None:
                    # We do not know the member yet, create a stub
                    if type == "node":
                        element = osma.node(id=ref)
                    elif type == "way":
                        element = osma.way(id=ref)
                    elif type == "relation":
                        element = osma.relation(id=ref)
                    # We need to commit here because element could be repeated
                    session.add(element)
                    session.commit()
                # Append to members
                relation.members.append((element, role))

            # Store other attributes and tags
            _dom_attrs_to_any(e, relation)
            _dom_tags_to_any(e, relation)

        # Add to session
        session.add(relation)
        session.commit()

    # Get root element
    osm = dom.documentElement

    # Iterate over children to find nodes, ways and relations
    for e in osm.childNodes:
        # Determine element type
        if e.nodeName == "node":
            _dom_to_node(e)
        elif e.nodeName == "way":
            _dom_to_way(e)
        elif e.nodeName == "relation":
            _dom_to_relation(e)

        # Rmove children
        e.unlink()

def _import_osm_xml(osma, session, xml):
    """ Import a string in OSM XML format into an OSMAlchemy model.

      osma - reference to the OSMAlchemy model instance
      session - an SQLAlchemy session
      xml - string containing the XML data
    """

    # Parse string into DOM structure
    dom = minidom.parseString(xml)

    return _import_osm_dom(osma, session, dom)

def _import_osm_file(osma, session, file):
    """ Import a file in OSM XML format into an OSMAlchemy model.

      osma - reference to the OSMAlchemy model instance
      session - an SQLAlchemy session
      path - path to the file to import or open file object
    """

    # Parse document into DOM structure
    dom = minidom.parse(file)

    return _import_osm_dom(osma, session, dom)

# Define operator to string mapping
_ops = {operator.eq: "==",
        operator.ne: "!=",
        operator.lt: "<",
        operator.gt: ">",
        operator.le: "<=",
        operator.ge: ">=",
        operator.and_: "&&",
        operator.or_: "||"}

def _analyse_clause(clause, target):
    if type(clause) is BinaryExpression:
        # This is something like "latitude >= 51.0"
        left = clause.left
        right = clause.right
        op = clause.operator

        # Left part should be a column
        if type(left) is AnnotatedColumn:
            # Get table class and field
            model = left._annotations["parentmapper"].class_
            field = left

            # Only use if we are looking for this model
            if model is target:
                # Store field name
                left = field.name
            else:
                return None
        else:
            # Right now, we cannot cope with anything but a column on the left
            return None

        # Right part should be a literal value
        if type(right) is BindParameter:
            # Extract literal value
            right = right.value
        else:
            # Right now, we cannot cope with something else here
            return None

        # Look for a known operator
        if op in _ops.keys():
            # Get string representation
            op = _ops[op]
        else:
            # Right now, we cannot cope with other operators
            return None

        # Return polish notation tuple of this clause
        return (op, left, right)
    elif type(clause) is BooleanClauseList:
        # This is an AND or OR operation
        op = clause.operator
        clauses = []

        # Iterate over all the clauses in this operation
        for clause in clause.clauses:
            # Recursively analyse clauses
            res = _analyse_clause(clause, target)
            # None is returned for unsupported clauses or operations
            if res is not None:
                # Append polish notation result to clauses list
                clauses.append(res)

        # Look for a known operator
        if op in _ops.keys():
            # Get string representation
            op = _ops[op]
        else:
            # Right now, we cannot cope with anything else
            return None

        # Return polish notation tuple of this clause
        return (op, clauses)
    else:
        # We hit an unsupported type of clause
        return None
