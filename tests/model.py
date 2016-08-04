#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

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
from sqlalchemy.orm import sessionmaker

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

        self.base = declarative_base(bind=self.engine)
        self.osmalchemy = OSMAlchemy(self.base)
        self.base.metadata.create_all()
        self.session = sessionmaker(bind=self.engine)()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

        profile[self.__class__.__name__][self.id().split(".")[-1]] -= time.time()
        profile[self.__class__.__name__][self.id().split(".")[-1]] *= -1

    def test_create_node(self):
        # Create node
        node = self.osmalchemy.Node()
        node.latitude = 51.0
        node.longitude = 7.0

        # Store node
        self.session.add(node)
        self.session.commit()

        # Query for node and check
        node = self.session.query(self.osmalchemy.Node).filter_by(latitude=51.0).first()
        self.assertEqual(node.latitude, 51.0)
        self.assertEqual(node.longitude, 7.0)
        self.assertEqual(len(node.tags), 0)

    def test_create_node_with_tags(self):
        # Create node and tags
        node = self.osmalchemy.Node(51.0, 7.0)
        node.tags = {"name": "test", "foo": "bar"}

        # Store everything
        self.session.add(node)
        self.session.commit()

        # Query for node and check
        node = self.session.query(self.osmalchemy.Node).filter_by(latitude=51.0).first()
        self.assertEqual(node.latitude, 51.0)
        self.assertEqual(node.longitude, 7.0)
        self.assertEqual(len(node.tags), 2)
        self.assertEqual(node.tags["name"], "test")
        self.assertEqual(node.tags["foo"], "bar")

    def test_create_way_with_nodes(self):
        # Create way and nodes
        way = self.osmalchemy.Way()
        way.nodes = [self.osmalchemy.Node(51.0, 7.0),
                     self.osmalchemy.Node(51.1, 7.1),
                     self.osmalchemy.Node(51.2, 7.2),
                     self.osmalchemy.Node(51.3, 7.3),
                     self.osmalchemy.Node(51.4, 7.4)]

        # Store everything
        self.session.add(way)
        self.session.commit()

        # Query for way and check
        way = self.session.query(self.osmalchemy.Way).first()
        self.assertEqual(len(way.nodes), 5)
        self.assertEqual((way.nodes[0].latitude, way.nodes[0].longitude), (51.0, 7.0))
        self.assertEqual((way.nodes[1].latitude, way.nodes[1].longitude), (51.1, 7.1))
        self.assertEqual((way.nodes[2].latitude, way.nodes[2].longitude), (51.2, 7.2))
        self.assertEqual((way.nodes[3].latitude, way.nodes[3].longitude), (51.3, 7.3))
        self.assertEqual((way.nodes[4].latitude, way.nodes[4].longitude), (51.4, 7.4))

    def test_create_way_with_nodes_and_tags(self):
        # Create way and nodes
        way = self.osmalchemy.Way()
        way.nodes = [self.osmalchemy.Node(51.0, 7.0),
                     self.osmalchemy.Node(51.1, 7.1),
                     self.osmalchemy.Node(51.2, 7.2),
                     self.osmalchemy.Node(51.3, 7.3),
                     self.osmalchemy.Node(51.4, 7.4)]
        way.tags = {"name": "Testway", "foo": "bar"}

        # Store everything
        self.session.add(way)
        self.session.commit()

        # Query for way and check
        way = self.session.query(self.osmalchemy.Way).first()
        self.assertEqual(len(way.nodes), 5)
        self.assertEqual((way.nodes[0].latitude, way.nodes[0].longitude), (51.0, 7.0))
        self.assertEqual((way.nodes[1].latitude, way.nodes[1].longitude), (51.1, 7.1))
        self.assertEqual((way.nodes[2].latitude, way.nodes[2].longitude), (51.2, 7.2))
        self.assertEqual((way.nodes[3].latitude, way.nodes[3].longitude), (51.3, 7.3))
        self.assertEqual((way.nodes[4].latitude, way.nodes[4].longitude), (51.4, 7.4))
        self.assertEqual(len(way.tags), 2)
        self.assertEqual(way.tags["name"], "Testway")
        self.assertEqual(way.tags["foo"], "bar")

    def test_create_way_with_nodes_and_tags_and_tags_on_node(self):
        # Create way and nodes
        way = self.osmalchemy.Way()
        way.nodes = [self.osmalchemy.Node(51.0, 7.0),
                     self.osmalchemy.Node(51.1, 7.1),
                     self.osmalchemy.Node(51.2, 7.2),
                     self.osmalchemy.Node(51.3, 7.3),
                     self.osmalchemy.Node(51.4, 7.4)]
        way.tags = {"name": "Testway", "foo": "bar"}
        way.nodes[2].tags = {"name": "Testampel", "foo": "bar"}

        # Store everything
        self.session.add(way)
        self.session.commit()

        # Query for way and check
        way = self.session.query(self.osmalchemy.Way).first()
        self.assertEqual(len(way.nodes), 5)
        self.assertEqual((way.nodes[0].latitude, way.nodes[0].longitude), (51.0, 7.0))
        self.assertEqual((way.nodes[1].latitude, way.nodes[1].longitude), (51.1, 7.1))
        self.assertEqual((way.nodes[2].latitude, way.nodes[2].longitude), (51.2, 7.2))
        self.assertEqual((way.nodes[3].latitude, way.nodes[3].longitude), (51.3, 7.3))
        self.assertEqual((way.nodes[4].latitude, way.nodes[4].longitude), (51.4, 7.4))
        self.assertEqual(len(way.tags), 2)
        self.assertEqual(way.tags["name"], "Testway")
        self.assertEqual(way.tags["foo"], "bar")
        self.assertEqual(len(way.nodes[2].tags), 2)
        self.assertEqual(way.nodes[2].tags["name"], "Testampel")
        self.assertEqual(way.nodes[2].tags["foo"], "bar")

    def test_create_relation_with_nodes(self):
        # Create way and add nodes
        relation = self.osmalchemy.Relation()
        relation.members = [self.osmalchemy.Node(51.0, 7.0),
                            self.osmalchemy.Node(51.1, 7.1),
                            self.osmalchemy.Node(51.2, 7.2),
                            self.osmalchemy.Node(51.3, 7.3),
                            self.osmalchemy.Node(51.4, 7.4)]

        # Store everything
        self.session.add(relation)
        self.session.commit()

        # Query for way and check
        relation = self.session.query(self.osmalchemy.Relation).first()
        self.assertEqual((relation.members[0].latitude, relation.members[0].longitude),
                         (51.0, 7.0))
        self.assertEqual((relation.members[1].latitude, relation.members[1].longitude),
                         (51.1, 7.1))
        self.assertEqual((relation.members[2].latitude, relation.members[2].longitude),
                         (51.2, 7.2))
        self.assertEqual((relation.members[3].latitude, relation.members[3].longitude),
                         (51.3, 7.3))
        self.assertEqual((relation.members[4].latitude, relation.members[4].longitude),
                         (51.4, 7.4))

    def test_create_relation_with_nodes_and_ways(self):
        # Create way and add nodes and ways
        relation = self.osmalchemy.Relation()
        relation.members = [self.osmalchemy.Node(51.0, 7.0),
                            self.osmalchemy.Way(),
                            self.osmalchemy.Node(51.1, 7.1),
                            self.osmalchemy.Way(),
                            self.osmalchemy.Node(51.2, 7.2),
                            self.osmalchemy.Way(),
                            self.osmalchemy.Node(51.3, 7.3),
                            self.osmalchemy.Way(),
                            self.osmalchemy.Node(51.4, 7.4)]
        relation.members[3].nodes.append(relation.members[8])

        # Store everything
        self.session.add(relation)
        self.session.commit()

        # Query for way and check
        relation = self.session.query(self.osmalchemy.Relation).first()
        self.assertEqual((relation.members[0].latitude, relation.members[0].longitude),
                         (51.0, 7.0))
        self.assertEqual((relation.members[2].latitude, relation.members[2].longitude),
                         (51.1, 7.1))
        self.assertEqual((relation.members[4].latitude, relation.members[4].longitude),
                         (51.2, 7.2))
        self.assertEqual((relation.members[6].latitude, relation.members[6].longitude),
                         (51.3, 7.3))
        self.assertEqual((relation.members[8].latitude, relation.members[8].longitude),
                         (51.4, 7.4))
        self.assertIs(relation.members[3].nodes[0], relation.members[8])

    def test_create_relation_with_nodes_and_ways_and_tags_everywhere(self):
        # Create way and add nodes and ways
        relation = self.osmalchemy.Relation()
        relation.members = [self.osmalchemy.Node(51.0, 7.0),
                            self.osmalchemy.Way(),
                            self.osmalchemy.Node(51.1, 7.1),
                            self.osmalchemy.Way(),
                            self.osmalchemy.Node(51.2, 7.2),
                            self.osmalchemy.Way(),
                            self.osmalchemy.Node(51.3, 7.3),
                            self.osmalchemy.Way(),
                            self.osmalchemy.Node(51.4, 7.4)]
        relation.tags = {"name": "weirdest roads in Paris"}
        relation.members[3].nodes.append(relation.members[8])
        relation.members[7].tags = {"foo": "bar", "bang": "baz"}
        relation.members[8].tags = {"name": "Doppelknoten"}

        # Store everything
        self.session.add(relation)
        self.session.commit()

        # Query for way and check
        relation = self.session.query(self.osmalchemy.Relation).first()
        self.assertEqual((relation.members[0].latitude, relation.members[0].longitude),
                         (51.0, 7.0))
        self.assertEqual((relation.members[2].latitude, relation.members[2].longitude),
                         (51.1, 7.1))
        self.assertEqual((relation.members[4].latitude, relation.members[4].longitude),
                         (51.2, 7.2))
        self.assertEqual((relation.members[6].latitude, relation.members[6].longitude),
                         (51.3, 7.3))
        self.assertEqual((relation.members[8].latitude, relation.members[8].longitude),
                         (51.4, 7.4))
        self.assertIs(relation.members[3].nodes[0], relation.members[8])
        self.assertEqual(relation.tags["name"], "weirdest roads in Paris")
        self.assertEqual(relation.members[7].tags["foo"], "bar")
        self.assertEqual(relation.members[7].tags["bang"], "baz")
        self.assertEqual(relation.members[8].tags, relation.members[3].nodes[0].tags)

class OSMAlchemyModelTestsSQLite(OSMAlchemyModelTests, unittest.TestCase):
    """ Tests run with SQLite """

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", echo=True)
        OSMAlchemyModelTests.setUp(self)

    def tearDown(self):
        OSMAlchemyModelTests.tearDown(self)

class OSMAlchemyModelTestsPostgres(OSMAlchemyModelTests, unittest.TestCase):
    """ Tests run with PostgreSQL """

    def setUp(self):
        self.postgresql = Postgresql()
        self.engine = create_engine(self.postgresql.url(), echo=True)
        OSMAlchemyModelTests.setUp(self)

    def tearDown(self):
        self.postgresql.stop()
        OSMAlchemyModelTests.tearDown(self)

class OSMAlchemyModelTestsMySQL(OSMAlchemyModelTests, unittest.TestCase):
    """ Tests run with MySQL """

    def setUp(self):
        self.mysql = Mysqld()
        self.engine = create_engine(self.mysql.url(), echo=True)
        OSMAlchemyModelTests.setUp(self)

    def tearDown(self):
        self.mysql.stop()
        OSMAlchemyModelTests.tearDown(self)
