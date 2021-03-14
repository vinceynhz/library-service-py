"""
 :author: vic on 2021-03-14
"""
import unittest
import dbschema

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestDbSchema(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:', echo=True)
        dbschema.SessionMaker = sessionmaker(bind=self.engine)

    def test_base(self):
        with dbschema.CloseableSession() as session:
            self.assertEqual({}, session.info)
