import unittest
from Classes import get_rank_file


class MyTestCase(unittest.TestCase):
    def test_get_rank_file(self):
        result = get_rank_file(0, 0)
        self.assertEqual(result, "a8")  # add assertion here

        result = get_rank_file(1, 0)
        self.assertEqual(result, "a7")


if __name__ == '__main__':
    unittest.main()
