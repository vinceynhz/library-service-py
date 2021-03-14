"""
 :author: vic on 2021-03-14
"""
import dbschema
import json
import logging
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestDbSchema(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%dT%H:%M:%S')
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        dbschema.Base.metadata.create_all(self.engine)
        dbschema.SessionMaker = sessionmaker(bind=self.engine)

        with open('tests/contributor_data.json', 'r') as infile:
            self.contributor_data = json.load(infile)

    def tearDown(self):
        self.engine.dispose()

    def test_base(self):
        with dbschema.CloseableSession() as session:
            self.assertEqual({}, session.info)

    def test_add_contributors(self):
        # add all contributors from test data
        for tc in self.contributor_data:
            contributor = dbschema.Contributor.maker({'name': tc['input']})
            logging.info(repr(contributor))
            contributor = dbschema.add_contributor(contributor)
            self.assertTrue(contributor is not None)

        all_contributors = dbschema.contributors()
        self.assertTrue(len(self.contributor_data), len(all_contributors))
