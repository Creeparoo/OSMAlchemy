import unittest

from osmalchemy import OSMAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class OSMAlchemyModelTests(unittest.TestCase):
    """ Test cases for the data model, without any OSM API
    integration.
    """

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", echo=True)
        self.base = declarative_base(bind=self.engine)
        self.osmalchemy = OSMAlchemy(self.base)
        self.base.metadata.create_all()
        self.session = sessionmaker(bind=self.engine)()

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
