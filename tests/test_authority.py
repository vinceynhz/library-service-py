"""
 :author: vic on 2021-03-13
"""
import authority
import json
import unittest


class TestAuthorityMethods(unittest.TestCase):
    def setUp(self):
        with open('tests/contributor_data.json', 'r') as infile:
            self.contributor_data = json.load(infile)

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

    def test_sha256(self):
        for tc in self.contributor_data:
            self.assertEqual(tc['sha256'], authority.sha56(tc['input']))

    def test_cataloguing(self):
        for tc in self.contributor_data:
            self.assertEqual(tc['cataloguing'], authority.ordering_name(tc['input']))


if __name__ == '__main__':
    unittest.main()
