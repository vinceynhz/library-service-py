"""
 :author: vic on 2021-04-17
"""
import unittest
from typing import Type

from dbschema import ContributionType
from dbschema.base import BaseEnum
from dbschema.book import BookFormat


class TestEnums(unittest.TestCase):
    def test_parse(self):
        self._parse_enum_members(BookFormat)
        self._parse_enum_members(ContributionType)

    def test_failed_parse(self):
        self._failed_parse(BookFormat)
        self._failed_parse(ContributionType)

    def _parse_enum_members(self, enum_name: Type[BaseEnum]):
        test_data = {name: member for name, member in enum_name.__members__.items()}
        for k, v in test_data.items():
            result = enum_name.parse(k)
            self.assertEqual(result, v)
            result = enum_name.parse(k.lower())
            self.assertEqual(result, v)
            result = enum_name.parse(k.title())
            self.assertEqual(result, v)

    def _failed_parse(self, enum_name: Type[BaseEnum]):
        try:
            enum_name.parse("UNKNOWN")
            self.fail('Reached unreachable point')
        except NameError as e:
            self.assertTrue(f"No {enum_name.__name__} with value: UNKNOWN" in str(e))
