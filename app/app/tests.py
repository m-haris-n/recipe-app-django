"""
Sample Tests
"""

from django.test import SimpleTestCase

from app import calc


class CalcTests(SimpleTestCase):
    """TEst Calc Module"""

    def test_add_numbers(self):
        """test Adding numbers together"""
        res = calc.add(5, 6)

        self.assertEqual(res, 11)

    def test_subtract_numbers(self):
        """Test subtraction"""

        res = calc.subtract(10, 15)
        self.assertEqual(res, -5)
