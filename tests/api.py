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

""" Tests concerning the OSMAlchemy object. """

# Standard unit testing framework
import unittest

# Module to be tested
from osmalchemy import OSMAlchemy

# SQLAlchemy for working with model and data
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Flask for testing integration with Flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy as FlaskSQLAlchemy

class OSMAlchemyAPITests(unittest.TestCase):
    def test_instantiate_with_engine(self):
        engine = create_engine("sqlite:///:memory:")
        osmalchemy = OSMAlchemy(engine)
        self.assertIsInstance(osmalchemy, OSMAlchemy)
        self.assertIs(osmalchemy._engine, engine)
        engine.dispose()

    def test_instantiate_with_engine_and_base(self):
        engine = create_engine("sqlite:///:memory:")
        base = declarative_base(bind=engine)
        osmalchemy = OSMAlchemy((engine, base))
        self.assertIsInstance(osmalchemy, OSMAlchemy)
        self.assertIs(osmalchemy._engine, engine)
        self.assertIs(osmalchemy._base, base)
        engine.dispose()

    def test_instantiate_with_engine_and_base_and_session(self):
        engine = create_engine("sqlite:///:memory:")
        base = declarative_base(bind=engine)
        session = scoped_session(sessionmaker(bind=engine))
        osmalchemy = OSMAlchemy((engine, base, session))
        self.assertIsInstance(osmalchemy, OSMAlchemy)
        self.assertIs(osmalchemy._engine, engine)
        self.assertIs(osmalchemy._base, base)
        self.assertIs(osmalchemy._session, session)
        engine.dispose()

    def test_instantiate_with_flask_sqlalchemy(self):
        app = Flask("test")
        db = FlaskSQLAlchemy(app)
        osmalchemy = OSMAlchemy(db)
        self.assertIsInstance(osmalchemy, OSMAlchemy)
        self.assertIs(osmalchemy._engine, db.engine)
        self.assertIs(osmalchemy._base, db.Model)
        self.assertIs(osmalchemy._session, db.session)

# Make runnable as standalone script
if __name__ == "__main__":
    unittest.main()
