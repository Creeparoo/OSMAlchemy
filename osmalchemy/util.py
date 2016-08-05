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
import xml.dom.minidom as minidom

def _import_osm_dom(osma, session, dom):
    """ Import a DOM tree from OSM XML into an OSMAlchemy model.

    Not called directly; used by _import_osm_xml and _import_osm_file.
    """

    def _dom_attrs_to_any(e, element):
        if "version" in e.attributes.keys():
            element.version = e.attributes["version"].value
        if "changeset" in e.attributes.keys():
            element.changeset = e.attributes["changeset"].value
        if "user" in e.attributes.keys():
            element.user = e.attributes["user"].value
        if "uid" in e.attributes.keys():
            element.uid = e.attributes["uid"].value
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
        # Get mandatory node id
        id = e.attributes["id"].value

        # Find object in database and create if non-existent
        node = session.query(osma.Node).filter_by(id=id).scalar()
        if node is None:
            node = osma.Node(id=id)

        # Store mandatory latitude and longitude
        node.latitude = e.attributes["lat"].value
        node.longitude = e.attributes["lon"].value

        # Store other attributes and tags
        _dom_attrs_to_any(e, node)
        _dom_tags_to_any(e, node)

        # Add to session
        session.add(node)

    def _dom_to_way(e):
        # Get mandatory way id
        id = e.attributes["id"].value

        # Find object in database and create if non-existent
        way = session.query(osma.Way).filter_by(id=id).scalar()
        if way is None:
            way = osma.Way(id=id)

        # Find all related nodes
        for n in e.getElementsByTagName("nd"):
            # Get node id and find object
            nid = n.attributes["ref"].value
            node = session.query(osma.Node).filter_by(id=nid).one()
            # Append to nodes in way
            way.nodes.append(node)

        # Store other attributes and tags
        _dom_attrs_to_any(e, way)
        _dom_tags_to_any(e, way)

        # Add to session
        session.add(way)

    def _dom_to_relation(e):
        # Get mandatory way id
        id = e.attributes["id"].value

        # Find object in database and create if non-existent
        relation = session.query(osma.Relation).filter_by(id=id).scalar()
        if relation is None:
            relation = osma.Relation(id=id)

        # Find all members
        for m in e.getElementsByTagName("member"):
            # Get member attributes
            ref = m.attributes["ref"].value
            type = m.attributes["type"].value
            if "role" in m.attributes.keys():
                role = m.attributes["role"].value
            else:
                role = ""
            element = session.query(osma.Element).filter_by(id=ref, type=type).one()
            # Append to members
            relation.members.append((element, role))

        # Store other attributes and tags
        _dom_attrs_to_any(e, relation)
        _dom_tags_to_any(e, relation)

        # Add to session
        session.add(relation)

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

    # Commit session
    session.commit()

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