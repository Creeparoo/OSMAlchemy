#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~

# Standard unit testing framework
import unittest

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

def tearDownModule():
    """ Global test suite tear down code """

    # Purge caches of database engines
    Postgresql.clear_cache()
    Mysqld.clear_cache()

class OSMAlchemyModelTests(object):
    """ Incomplete base class for common test routines.

    Subclassed in engine-dependent test classes.
    """

    def setUp(self):
        self.base = declarative_base(bind=self.engine)
        self.osmalchemy = OSMAlchemy(self.base)
        self.base.metadata.create_all()
        self.session = sessionmaker(bind=self.engine)()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

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
        node.tags = [self.osmalchemy.Tag("name", "test"),
                     self.osmalchemy.Tag("foo", "bar")]

        # Store everything
        self.session.add(node)
        self.session.commit()

        # Query for node and check
        node = self.session.query(self.osmalchemy.Node).filter_by(latitude=51.0).first()
        self.assertEqual(node.latitude, 51.0)
        self.assertEqual(node.longitude, 7.0)
        self.assertEqual(len(node.tags), 2)
        self.assertEqual((node.tags[0].key, node.tags[0].value), ("name", "test"))
        self.assertEqual((node.tags[1].key, node.tags[1].value), ("foo", "bar"))

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
        way.tags = [self.osmalchemy.Tag("name", "Testway"),
                    self.osmalchemy.Tag("foo", "bar")]

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
        self.assertEqual((way.tags[0].key, way.tags[0].value), ("name", "Testway"))
        self.assertEqual((way.tags[1].key, way.tags[1].value), ("foo", "bar"))

    def test_create_way_with_nodes_and_tags_and_tags_on_node(self):
        # Create way and nodes
        way = self.osmalchemy.Way()
        way.nodes = [self.osmalchemy.Node(51.0, 7.0),
                     self.osmalchemy.Node(51.1, 7.1),
                     self.osmalchemy.Node(51.2, 7.2),
                     self.osmalchemy.Node(51.3, 7.3),
                     self.osmalchemy.Node(51.4, 7.4)]
        way.tags = [self.osmalchemy.Tag("name", "Testway"),
                    self.osmalchemy.Tag("foo", "bar")]
        way.nodes[2].tags = [self.osmalchemy.Tag("name", "Testampel"),
                             self.osmalchemy.Tag("foo", "bar")]

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
        self.assertEqual((way.tags[0].key, way.tags[0].value), ("name", "Testway"))
        self.assertEqual((way.tags[1].key, way.tags[1].value), ("foo", "bar"))
        self.assertEqual(len(way.nodes[2].tags), 2)
        self.assertEqual((way.nodes[2].tags[0].key, way.nodes[2].tags[0].value), ("name", "Testampel"))
        self.assertEqual((way.nodes[2].tags[1].key, way.nodes[2].tags[1].value), ("foo", "bar"))
        self.assertIsNot(way.tags[1], way.nodes[2].tags[1])

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
