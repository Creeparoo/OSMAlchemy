#!/usr/bin/env python
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

""" Tests concerning the OSM data model implementation. """

# Standard unit testing framework
import unittest

# We want to profile test cases
import time

# Helper libraries for different database engines
from testing.mysqld import MysqldFactory
from testing.postgresql import PostgresqlFactory

# Module to be tested
from osmalchemy import OSMAlchemy

# SQLAlchemy for working with model and data
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Flask for testing integration with Flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy as FlaskSQLAlchemy

# Create database engine factories to enable caching
Postgresql = PostgresqlFactory(cache_initialized_db=True)
Mysqld = MysqldFactory(cache_initialized_db=True)

# Dictionary to store profiling information about tests
profile = {}

def tearDownModule():
    """ Global test suite tear down code """

    # Purge caches of database engines
    Postgresql.clear_cache()
    Mysqld.clear_cache()

    # Print profiling info
    print("Database model test times")
    print("=========================")
    print("")
    for suite in profile:
        print("%8.3f s\t%s" % (sum([profile[suite][test] for test in profile[suite]]), suite))
        for test in profile[suite]:
            print("\t%8.3f s\t%s" % (profile[suite][test], test))

class OSMAlchemyModelTests(object):
    """ Incomplete base class for common test routines.

    Subclassed in engine-dependent test classes.
    """

    def setUp(self):
        if not self.__class__.__name__ in profile:
            profile[self.__class__.__name__] = {}
        profile[self.__class__.__name__][self.id().split(".")[-1]] = time.time()

    def tearDown(self):
        profile[self.__class__.__name__][self.id().split(".")[-1]] -= time.time()
        profile[self.__class__.__name__][self.id().split(".")[-1]] *= -1

    def test_create_node(self):
        # Create node
        node = self.osmalchemy.node()
        node.latitude = 51.0
        node.longitude = 7.0

        # Store node
        self.session.add(node)
        self.session.commit()
        # Ensure removal from ORM
        self.session.remove()

        # Query for node and check
        node = self.session.query(self.osmalchemy.node).filter_by(latitude=51.0).first()
        self.assertEqual(node.latitude, 51.0)
        self.assertEqual(node.longitude, 7.0)
        self.assertEqual(len(node.tags), 0)

    def test_create_node_with_tags(self):
        # Create node and tags
        node = self.osmalchemy.node(51.0, 7.0)
        node.tags = {u"name": u"test", u"foo": u"bar"}

        # Store everything
        self.session.add(node)
        self.session.commit()
        # Ensure removal from ORM
        self.session.remove()

        # Query for node and check
        node = self.session.query(self.osmalchemy.node).filter_by(latitude=51.0).first()
        self.assertEqual(node.latitude, 51.0)
        self.assertEqual(node.longitude, 7.0)
        self.assertEqual(len(node.tags), 2)
        self.assertEqual(node.tags[u"name"], u"test")
        self.assertEqual(node.tags[u"foo"], u"bar")

    def test_create_way_with_nodes(self):
        # Create way and nodes
        way = self.osmalchemy.way()
        way.nodes = [self.osmalchemy.node(51.0, 7.0),
                     self.osmalchemy.node(51.1, 7.1),
                     self.osmalchemy.node(51.2, 7.2),
                     self.osmalchemy.node(51.3, 7.3),
                     self.osmalchemy.node(51.4, 7.4)]

        # Store everything
        self.session.add(way)
        self.session.commit()
        # Ensure removal from ORM
        self.session.remove()

        # Query for way and check
        way = self.session.query(self.osmalchemy.way).first()
        self.assertEqual(len(way.nodes), 5)
        self.assertEqual((way.nodes[0].latitude, way.nodes[0].longitude), (51.0, 7.0))
        self.assertEqual((way.nodes[1].latitude, way.nodes[1].longitude), (51.1, 7.1))
        self.assertEqual((way.nodes[2].latitude, way.nodes[2].longitude), (51.2, 7.2))
        self.assertEqual((way.nodes[3].latitude, way.nodes[3].longitude), (51.3, 7.3))
        self.assertEqual((way.nodes[4].latitude, way.nodes[4].longitude), (51.4, 7.4))

    def test_create_way_with_nodes_and_tags(self):
        # Create way and nodes
        way = self.osmalchemy.way()
        way.nodes = [self.osmalchemy.node(51.0, 7.0),
                     self.osmalchemy.node(51.1, 7.1),
                     self.osmalchemy.node(51.2, 7.2),
                     self.osmalchemy.node(51.3, 7.3),
                     self.osmalchemy.node(51.4, 7.4)]
        way.tags = {u"name": u"Testway", u"foo": u"bar"}

        # Store everything
        self.session.add(way)
        self.session.commit()
        # Ensure removal from ORM
        self.session.remove()

        # Query for way and check
        way = self.session.query(self.osmalchemy.way).first()
        self.assertEqual(len(way.nodes), 5)
        self.assertEqual((way.nodes[0].latitude, way.nodes[0].longitude), (51.0, 7.0))
        self.assertEqual((way.nodes[1].latitude, way.nodes[1].longitude), (51.1, 7.1))
        self.assertEqual((way.nodes[2].latitude, way.nodes[2].longitude), (51.2, 7.2))
        self.assertEqual((way.nodes[3].latitude, way.nodes[3].longitude), (51.3, 7.3))
        self.assertEqual((way.nodes[4].latitude, way.nodes[4].longitude), (51.4, 7.4))
        self.assertEqual(len(way.tags), 2)
        self.assertEqual(way.tags[u"name"], u"Testway")
        self.assertEqual(way.tags[u"foo"], u"bar")

    def test_create_way_with_nodes_and_tags_and_tags_on_node(self):
        # Create way and nodes
        way = self.osmalchemy.way()
        way.nodes = [self.osmalchemy.node(51.0, 7.0),
                     self.osmalchemy.node(51.1, 7.1),
                     self.osmalchemy.node(51.2, 7.2),
                     self.osmalchemy.node(51.3, 7.3),
                     self.osmalchemy.node(51.4, 7.4)]
        way.tags = {u"name": u"Testway", u"foo": u"bar"}
        way.nodes[2].tags = {u"name": u"Testampel", u"foo": u"bar"}

        # Store everything
        self.session.add(way)
        self.session.commit()
        # Ensure removal from ORM
        self.session.remove()

        # Query for way and check
        way = self.session.query(self.osmalchemy.way).first()
        self.assertEqual(len(way.nodes), 5)
        self.assertEqual((way.nodes[0].latitude, way.nodes[0].longitude), (51.0, 7.0))
        self.assertEqual((way.nodes[1].latitude, way.nodes[1].longitude), (51.1, 7.1))
        self.assertEqual((way.nodes[2].latitude, way.nodes[2].longitude), (51.2, 7.2))
        self.assertEqual((way.nodes[3].latitude, way.nodes[3].longitude), (51.3, 7.3))
        self.assertEqual((way.nodes[4].latitude, way.nodes[4].longitude), (51.4, 7.4))
        self.assertEqual(len(way.tags), 2)
        self.assertEqual(way.tags[u"name"], u"Testway")
        self.assertEqual(way.tags[u"foo"], u"bar")
        self.assertEqual(len(way.nodes[2].tags), 2)
        self.assertEqual(way.nodes[2].tags[u"name"], u"Testampel")
        self.assertEqual(way.nodes[2].tags[u"foo"], u"bar")

    def test_create_relation_with_nodes(self):
        # Create way and add nodes
        relation = self.osmalchemy.relation()
        relation.members = [(self.osmalchemy.node(51.0, 7.0), u""),
                            (self.osmalchemy.node(51.1, 7.1), u""),
                            (self.osmalchemy.node(51.2, 7.2), u""),
                            (self.osmalchemy.node(51.3, 7.3), u""),
                            (self.osmalchemy.node(51.4, 7.4), u"")]

        # Store everything
        self.session.add(relation)
        self.session.commit()
        # Ensure removal from ORM
        self.session.remove()

        # Query for way and check
        relation = self.session.query(self.osmalchemy.relation).first()
        self.assertEqual((relation.members[0][0].latitude, relation.members[0][0].longitude),
                         (51.0, 7.0))
        self.assertEqual((relation.members[1][0].latitude, relation.members[1][0].longitude),
                         (51.1, 7.1))
        self.assertEqual((relation.members[2][0].latitude, relation.members[2][0].longitude),
                         (51.2, 7.2))
        self.assertEqual((relation.members[3][0].latitude, relation.members[3][0].longitude),
                         (51.3, 7.3))
        self.assertEqual((relation.members[4][0].latitude, relation.members[4][0].longitude),
                         (51.4, 7.4))

    def test_create_relation_with_nodes_and_ways(self):
        # Create way and add nodes and ways
        relation = self.osmalchemy.relation()
        relation.members = [(self.osmalchemy.node(51.0, 7.0), u''),
                            (self.osmalchemy.way(), u''),
                            (self.osmalchemy.node(51.1, 7.1), u''),
                            (self.osmalchemy.way(), u''),
                            (self.osmalchemy.node(51.2, 7.2), u''),
                            (self.osmalchemy.way(), u''),
                            (self.osmalchemy.node(51.3, 7.3), u''),
                            (self.osmalchemy.way(), u''),
                            (self.osmalchemy.node(51.4, 7.4), u'')]
        relation.members[3][0].nodes.append(relation.members[8][0])

        # Store everything
        self.session.add(relation)
        self.session.commit()
        # Ensure removal from ORM
        self.session.remove()

        # Query for way and check
        relation = self.session.query(self.osmalchemy.relation).first()
        self.assertEqual((relation.members[0][0].latitude, relation.members[0][0].longitude),
                         (51.0, 7.0))
        self.assertEqual((relation.members[2][0].latitude, relation.members[2][0].longitude),
                         (51.1, 7.1))
        self.assertEqual((relation.members[4][0].latitude, relation.members[4][0].longitude),
                         (51.2, 7.2))
        self.assertEqual((relation.members[6][0].latitude, relation.members[6][0].longitude),
                         (51.3, 7.3))
        self.assertEqual((relation.members[8][0].latitude, relation.members[8][0].longitude),
                         (51.4, 7.4))
        self.assertIs(relation.members[3][0].nodes[0], relation.members[8][0])

    def test_create_relation_with_nodes_and_ways_and_tags_everywhere(self):
        # Create way and add nodes and ways
        relation = self.osmalchemy.relation()
        relation.members = [(self.osmalchemy.node(51.0, 7.0), u''),
                            (self.osmalchemy.way(), u''),
                            (self.osmalchemy.node(51.1, 7.1), u''),
                            (self.osmalchemy.way(), u''),
                            (self.osmalchemy.node(51.2, 7.2), u''),
                            (self.osmalchemy.way(), u''),
                            (self.osmalchemy.node(51.3, 7.3), u''),
                            (self.osmalchemy.way(), u''),
                            (self.osmalchemy.node(51.4, 7.4), u'')]
        relation.tags = {u"name": u"weirdest roads in Paris"}
        relation.members[3][0].nodes.append(relation.members[8][0])
        relation.members[7][0].tags = {u"foo": u"bar", u"bang": u"baz"}
        relation.members[8][0].tags = {u"name": u"Doppelknoten"}

        # Store everything
        self.session.add(relation)
        self.session.commit()
        # Ensure removal from ORM
        self.session.remove()

        # Query for way and check
        relation = self.session.query(self.osmalchemy.relation).first()
        self.assertEqual((relation.members[0][0].latitude, relation.members[0][0].longitude),
                         (51.0, 7.0))
        self.assertEqual((relation.members[2][0].latitude, relation.members[2][0].longitude),
                         (51.1, 7.1))
        self.assertEqual((relation.members[4][0].latitude, relation.members[4][0].longitude),
                         (51.2, 7.2))
        self.assertEqual((relation.members[6][0].latitude, relation.members[6][0].longitude),
                         (51.3, 7.3))
        self.assertEqual((relation.members[8][0].latitude, relation.members[8][0].longitude),
                         (51.4, 7.4))
        self.assertIs(relation.members[3][0].nodes[0], relation.members[8][0])
        self.assertEqual(relation.tags[u"name"], u"weirdest roads in Paris")
        self.assertEqual(relation.members[7][0].tags[u"foo"], u"bar")
        self.assertEqual(relation.members[7][0].tags[u"bang"], u"baz")
        self.assertEqual(relation.members[8][0].tags, relation.members[3][0].nodes[0].tags)

class OSMAlchemyModelTestsSQLite(OSMAlchemyModelTests, unittest.TestCase):
    """ Tests run with SQLite """

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.base = declarative_base(bind=self.engine)
        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.osmalchemy = OSMAlchemy((self.engine, self.base, self.session))
        self.base.metadata.create_all()
        OSMAlchemyModelTests.setUp(self)

    def tearDown(self):
        self.session.remove()
        self.engine.dispose()
        OSMAlchemyModelTests.tearDown(self)

class OSMAlchemyModelTestsPostgres(OSMAlchemyModelTests, unittest.TestCase):
    """ Tests run with PostgreSQL """

    def setUp(self):
        self.postgresql = Postgresql()
        self.engine = create_engine(self.postgresql.url())
        self.base = declarative_base(bind=self.engine)
        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.osmalchemy = OSMAlchemy((self.engine, self.base, self.session))
        self.base.metadata.create_all()
        OSMAlchemyModelTests.setUp(self)

    def tearDown(self):
        self.session.remove()
        self.engine.dispose()
        self.postgresql.stop()
        OSMAlchemyModelTests.tearDown(self)

class OSMAlchemyModelTestsMySQL(OSMAlchemyModelTests, unittest.TestCase):
    """ Tests run with MySQL """

    def setUp(self):
        self.mysql = Mysqld()
        self.engine = create_engine(self.mysql.url() + "?charset=utf8mb4")
        self.base = declarative_base(bind=self.engine)
        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.osmalchemy = OSMAlchemy((self.engine, self.base, self.session))
        self.base.metadata.create_all()
        OSMAlchemyModelTests.setUp(self)

    def tearDown(self):
        self.session.remove()
        self.engine.dispose()
        self.mysql.stop()
        OSMAlchemyModelTests.tearDown(self)

class OSMAlchemyModelTestsFlaskSQLAlchemy(OSMAlchemyModelTests, unittest.TestCase):
    """ Tests run with SQLite """

    def setUp(self):
        app = Flask("test")
        db = FlaskSQLAlchemy(app)
        self.session = db.session
        self.osmalchemy = OSMAlchemy(db)
        db.create_all()
        OSMAlchemyModelTests.setUp(self)

    def tearDown(self):
        self.session.remove()
        OSMAlchemyModelTests.tearDown(self)

# Make runnable as standalone script
if __name__ == "__main__":
    unittest.main()
