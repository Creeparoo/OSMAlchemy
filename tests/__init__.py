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
        self.session = sessionmaker(bind=self.engine)

    def test_create_node(self):
        node = self.osmalchemy.Node()
        node.latitude = 51.0
        node.longitude = 7.0
        self.session.add(node)
        self.session.commit()
