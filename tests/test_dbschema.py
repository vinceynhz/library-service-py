"""
 :author: vic on 2021-03-14
"""
from builtins import classmethod
from sqlalchemy.exc import IntegrityError

import dbschema
import json
import logging.config
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestDbSchema(unittest.TestCase):
    engine = None
    contributor_data = None
    book_data = None

    @classmethod
    def setUpClass(cls):
        logging.config.fileConfig("logging.conf")
        cls.engine = create_engine('sqlite:///:memory:', echo=False)
        dbschema.Base.metadata.create_all(cls.engine)
        dbschema.SessionMaker = sessionmaker(bind=cls.engine)

        with open('tests/contributor_data.json', 'r') as infile:
            cls.contributor_data = json.load(infile)

        with open('tests/book_data.json', 'r') as infile:
            cls.book_data = json.load(infile)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def test_base(self):
        with dbschema.CloseableSession() as session:
            self.assertEqual({}, session.info)

    def test_add_data(self):
        # add all contributors from test data
        for tc in self.contributor_data:
            contributor = dbschema.Contributor.maker({'name': tc['input']})
            self.assertIsNotNone(contributor)
            logging.info(repr(contributor))
            contributor_json = contributor.json()

            # attempt to add
            try:
                contributor_id = dbschema.add_contributor(contributor)
                self.assertIsNotNone(contributor_id)
                # we set the id we got from the DB
                contributor_json['id'] = int(contributor_id)
                # we pull that same id from the DB
                retrieved = dbschema.get_contributor(contributor_id)
                # and verify it's the same
                self.assertEqual(contributor_json, retrieved)
            except IntegrityError:
                self.assertTrue('duplicate' in tc and tc['duplicate'])

        all_contributors = dbschema.get_contributors()
        unique_contributors = [cont for cont in self.contributor_data if
                               'duplicate' not in cont or not cont['duplicate']]
        self.assertEqual(len(unique_contributors), len(all_contributors))

        # add all books from test data
        for tc in self.book_data:
            book = dbschema.Book.maker(
                {
                    "title": tc["title"]["input"],
                    "format": tc["format"]
                }
            )
            self.assertIsNotNone(book)
            logging.info(repr(book))
            book_json = book.json()
            book_json['sha256'] = tc['sha256']
            book_json['contributors'] = tc['contributors']

            book_contributors = {str(c["id"]): c["type"] for c in tc["contributors"]}

            # attempt to add
            try:
                book_id = dbschema.add_book(book, book_contributors)
                self.assertIsNotNone(book_id)
                # set the book id as the one we got back
                book_json["id"] = int(book_id)

                retrieved = dbschema.get_book(book_id)
                self.assertEqual(book_json, retrieved)
            except IntegrityError as exception:
                print(exception)
                self.fail("Reached unreachable point")

            # check if the book is part of the contributors


        all_books = dbschema.get_books()
        self.assertEqual(len(self.book_data), len(all_books))

