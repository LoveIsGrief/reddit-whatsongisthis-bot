import unittest

from src.title_parser import get_range_from_string


class TestRangeParser(unittest.TestCase):
    def test_start_and_end(self):
        string_no_hours = "prefix [01:00-02:00]"
        string_with_hours = "prefix [01:01:01-01:02:02] suffix"
        string_no_start_hour = "prefix [01:01-01:02:02] suffix"
        string_no_end_hour = "prefix [01:01:01-02:02] suffix"  # obviously doesn't make sense...

        self.assertEqual(get_range_from_string(string_no_hours), (60, 120))
        self.assertEqual(get_range_from_string(string_with_hours), (3661, 3722))
        self.assertEqual(get_range_from_string(string_no_start_hour), (61, 3722))
        self.assertEqual(get_range_from_string(string_no_end_hour), (3661, 122))


if __name__ == '__main__':
    unittest.main()
