import unittest
import sys
sys.path.append('..')
from mal.enums import Field, AnimeStatus


class TestEnums(unittest.TestCase):

    def test_contains(self):
        # can use strings instead of the enum
        # just test a few randmly because it's all inherited beaviour
        # from the BaseEnum
        self.assertIn('id', Field)
        self.assertNotIn('not_a_field', Field)

    def test_equality(self):
        self.assertEqual('statistics', Field.statistics)
        self.assertEqual('currently_airing', AnimeStatus.airing)
