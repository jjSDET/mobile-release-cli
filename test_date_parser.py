# File: test_date_parser.py
import unittest
from datetime import datetime
from date_parser import parse_date

class TestDateParser(unittest.TestCase):

    def test_single_date(self):
        self.assertEqual(parse_date('07/04', 2020), (datetime(2020, 7, 4), datetime(2020, 7, 4)))

    def test_date_range_same_year(self):
        self.assertEqual(parse_date('07/04-08/05', 2020), (datetime(2020, 7, 4), datetime(2020, 8, 5)))

    def test_date_range_cross_year(self):
        self.assertEqual(parse_date('11/30-01/15', 2020), (datetime(2020, 11, 30), datetime(2021, 1, 15)))

    def test_date_with_year(self):
        self.assertEqual(parse_date('07/04/2020', 2020), (datetime(2020, 7, 4), datetime(2020, 7, 4)))

    def test_date_range_with_year(self):
        self.assertEqual(parse_date('07/04/2020-08/05/2021', 2020), (datetime(2020, 7, 4), datetime(2021, 8, 5)))

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            parse_date('02/30/2020', 2020)

    def test_invalid_date_range(self):
        with self.assertRaises(ValueError):
            parse_date('07/04/2020-02/30/2020', 2020)

    def test_incomplete_date_range(self):
        with self.assertRaises(ValueError):
            parse_date('07/04-', 2020)

if __name__ == '__main__':
    unittest.main()
