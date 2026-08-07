import unittest
from Calc import calculate_mannco_price, calculate_dmmarket_price

class TestCalcFunctions(unittest.TestCase):
    def test_calculate_mannco_price_default(self):
        # Default: 1 key
        # key_price_usd = 1.73
        # fee_usd = round(0.06275 * 1 + 0.305, 2) = 0.37
        # total_usd = 1.73 + 0.37 = 2.10
        # total_sar = round(2.10 * 3.75, 2) = 7.88
        # total_uah = round(99 * 1 / 1.15, 2) = 86.09
        result = calculate_mannco_price(1)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, (7.88, 2.10, 86.09))

    def test_calculate_dmmarket_price_default(self):
        # Default: 1 key
        # key_price_usd = 1.63
        # fee_usd = round(2.35/100 * 1.63 + 0.25, 2) = 0.29
        # total_usd = 1.63 + 0.29 = 1.92
        # total_sar = round(1.92 * 3.75, 2) = 7.20
        # total_uah = round(99 * 1 / 1.15, 2) = 86.09
        result = calculate_dmmarket_price(1)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, (7.20, 1.92, 86.09))

if __name__ == "__main__":
    unittest.main()
