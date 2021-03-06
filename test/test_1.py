# import unittest
#
#
# class Summarizer:
#     def __init__(self, k):
#         self.k = k
#
#     def sum(self, i, j):
#         print('summ')
#         return i * j + self.k
#
#     def stop(self):
#         print('stop')
#
#
# class TestSummaeizer(unittest.TestCase):
#     def setUp(self):
#         print('setUp')
#         self.sut = Summarizer(5)
#
#     def tearDown(self) -> None:
#         print('tearDown')
#         self.sut.stop()
#
#     def test_sum_calc_positive(self):
#         self.assertEqual(self.sut.sum(3, 4), 17)
#
#     def test_sum_calc_negative(self):
#         self.assertEqual(self.sut.sum(-3, -4), 17)
#
#
# if __name__ == '__main__':
#     unittest.main()
