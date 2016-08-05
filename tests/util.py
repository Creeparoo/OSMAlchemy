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

""" Tests concerning OSMAlchemy utility code. """

# Standard unit testing framework
import unittest

# We want to profile test cases, and other imports
import time
import os

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
    print("Utility code test times")
    print("=======================")
    print("")
    for suite in profile:
        print("%8.3f s\t%s" % (sum([profile[suite][test] for test in profile[suite]]), suite))
        for test in profile[suite]:
            print("\t%8.3f s\t%s" % (profile[suite][test], test))

class OSMAlchemyUtilTests(object):
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

        self.datadir = os.path.join(os.path.dirname(__file__), "data")

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

        profile[self.__class__.__name__][self.id().split(".")[-1]] -= time.time()
        profile[self.__class__.__name__][self.id().split(".")[-1]] *= -1

    def test_import_osm_file(self):
        # Construct path to test data file
        path = os.path.join(self.datadir, "schwarzrheindorf.osm")

        # Import data into model
        self.osmalchemy.import_osm_file(path)

        # Check number of elements
        nodes = self.session.query(self.osmalchemy.Node).all()
        ways = self.session.query(self.osmalchemy.Way).all()
        relationss = self.session.query(self.osmalchemy.Relation).all()
        self.assertEqual(len(nodes), 7518)
        self.assertEqual(len(ways), 1559)
        self.assertEqual(len(relations), 33)

        # Try to retrieve some node and make checks on it
        haltestelle = self.session.query(self.osmalchemy.Node).filter_by(id=252714572).one()
        # Check metadata
        self.assertEqual(haltestelle.id, 252714572)
        self.assertEqual(haltestelle.latitude, 50.7509314)
        self.assertEqual(haltestelle.longitude, 7.1173853)
        # Check tags
        self.assertEqual(haltestelle.tags["VRS:gemeinde"], "BONN")
        self.assertEqual(haltestelle.tags["VRS:ref"], "65248")
        self.assertEqual(haltestelle.tags["name"], "Schwarzrheindorf Kirche")
        # Check node on a street
        wittestr = self.session.query(self.osmalchemy.Way).filter_by(id=23338279).one()
        self.assertIn(haltestelle, wittestr.nodes)

        # Try to retrieve some way and do checks on it
        doppelkirche = self.session.query(self.osmalchemy.Way).filter_by(id=83296962).one()
        # Verify metadata
        self.assertEqual(doppelkirche.id, 83296962)
        self.assertEqual(doppelkirche.visible, True)
        # Verify some tags
        self.assertEqual(doppelkirche.tags["name"], "St. Maria und St. Clemens Doppelkirche")
        self.assertEqual(doppelkirche.tags["historic"], "church")
        self.assertEqual(doppelkirche.tags["wheelchair"], "limited")
        self.assertEqual(doppelkirche.tags["addr:street"], "Dixstraße")
        # verify nodes on way
        nodes = (969195704, 969195706, 1751820961, 969195708, 969195710, 969195712,
                 969195714, 969195719, 969195720, 969195721, 969195722, 969218813,
                 969218815, 969218817, 969218819, 969218820, 969218821, 969218822,
                 969195740, 969195742, 969195745, 969195750, 969195751, 969195752,
                 969195753, 1751858766, 969195754, 969195759, 969218844, 969195704)
        for ref in nodes:
            nd = self.session.query(self.osmalchemy.Node).filter_by(id=ref).one()
            # Verify existence
            self.assertIn(nd, doppelkirche.nodes)
            # Verify ordering
            self.assertIs(doppelkirche.nodes[nodes.indexOf(ref)], nd)
        # Cross-check other nodes are not in way
        for ref in set(26853096, 26853100, 247056873):
            nd = self.session.query(self.osmalchemy.Node).filter_by(id=ref).one()
            self.assertNotIn(nd, doppelkieche.nodes)

    # Try to retrieve some relation and make checks on it
    buslinie = self.session.query(self.osmalchemy.Relation).filter_by(id=1823975).one()
    # Check metadata
    self.assertEqual(buslinie.id, 1823975)
    self.assertEqual(busline.changeset, 40638463)
    # Check tags
    self.assertEqual(busline.tags["name"], "VRS 640 Siegburg")
    self.assertEqual(busline.tags["ref"], "640")
    self.assertEqual(busline.tags["type"], "route")
    self.assertEqual(busline.tags["route"], "bus")
    # Check members
    self.assertIn((haltestelle, "stop"), buslinie.members)
    self.assertEqual(busline.members.indexOf((haltestelle, "stop")), 16)
    self.assertIn((wittestr, ""), buslinie.members)
    self.assertEqual(busline.members.indexOf((wittestr, "")), 109)

class OSMAlchemyUtilTestsSQLite(OSMAlchemyUtilTests, unittest.TestCase):
    """ Tests run with SQLite """

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", echo=True)
        OSMAlchemyUtilTests.setUp(self)

    def tearDown(self):
        OSMAlchemyUtilTests.tearDown(self)

class OSMAlchemyUtilTestsPostgres(OSMAlchemyUtilTests, unittest.TestCase):
    """ Tests run with PostgreSQL """

    def setUp(self):
        self.postgresql = Postgresql()
        self.engine = create_engine(self.postgresql.url(), echo=True)
        OSMAlchemyUtilTests.setUp(self)

    def tearDown(self):
        self.postgresql.stop()
        OSMAlchemyUtilTests.tearDown(self)

class OSMAlchemyUtilTestsMySQL(OSMAlchemyUtilTests, unittest.TestCase):
    """ Tests run with MySQL """

    def setUp(self):
        self.mysql = Mysqld()
        self.engine = create_engine(self.mysql.url(), echo=True)
        OSMAlchemyUtilTests.setUp(self)

    def tearDown(self):
        self.mysql.stop()
        OSMAlchemyUtilTests.tearDown(self)

# Make runnable as standalone script
if __name__ == "__main__":
    unittest.run()