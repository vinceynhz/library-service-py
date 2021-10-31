"""
 :author: vic on 2021-03-13
"""
import authority
import json
import unittest


class TestAuthorityMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('tests/contributor_data.json', 'r') as infile:
            cls.contributor_data = json.load(infile)
        with open('tests/book_data.json', 'r') as infile:
            cls.book_data = json.load(infile)

    def test_isalphanum(self):
        for i in range(128):
            char = bytes.fromhex('%02x' % i).decode('utf-8')
            res = authority._isalphanum(char)
            if i == 32 or 48 <= i < 58 or 65 <= i < 91 or 97 <= i < 123:
                self.assertTrue(res, 'int: %d char: %s' % (i, char))
            else:
                self.assertFalse(res, 'int: %d char: %s' % (i, char))

    def test_normalize(self):
        self.assertEqual('clean', authority._normalize('clean'))
        self.assertEqual('', authority._normalize(''))
        self.assertEqual('clean words', authority._normalize('clean words'))
        self.assertEqual('clean words', authority._normalize('C!l@EA----N W^o%!@#R$%^D&s'))

    def test_name(self):
        for tc in self.contributor_data:
            self.assertEqual(tc['name'], authority.name(tc['input']))

    def test_title(self):
        for tc in self.book_data:
            self.assertEqual(tc['title']['expected'], authority.title(tc['title']['input']))

    def test_sha256(self):
        # test from test cases
        for tc in self.contributor_data:
            self.assertEqual(tc['sha256'], authority.sha56(tc['input']))

        # These two should also return the same SHA between them since the special characters do not count
        salems_lot_sha = "1C660F4FCD1746AC8C689C3142A3C79BE56077824BF11F434B6F150F78CFD236"

        self.assertEqual(salems_lot_sha, authority.sha56("'Salem's Lot"))
        self.assertEqual(salems_lot_sha, authority.sha56("Salems Lot"))

    def test_cataloguing(self):
        for tc in self.contributor_data:
            self.assertEqual(tc['cataloguing'], authority.ordering_name(tc['input']))
        for tc in self.book_data:
            self.assertEqual(tc['title']['cataloguing'], authority.ordering_title(tc['title']['input']))


if __name__ == '__main__':
    unittest.main()
