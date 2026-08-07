import unittest
from price_fetcher import fetch_fallback_prices, fetch_live_prices

class TestPriceFetcher(unittest.TestCase):
    def test_fallback_prices(self):
        prices = fetch_fallback_prices()
        self.assertEqual(prices['mannco_usd'], 1.73)
        self.assertEqual(prices['dmarket_usd'], 1.63)
        self.assertEqual(prices['steam_uah'], 99.0)

    def test_fetch_live_prices_returns_valid_structure(self):
        prices = fetch_live_prices()
        self.assertIn('mannco_usd', prices)
        self.assertIn('dmarket_usd', prices)
        self.assertIn('steam_uah', prices)
        self.assertIsInstance(prices['mannco_usd'], float)
        self.assertIsInstance(prices['dmarket_usd'], float)
        self.assertIsInstance(prices['steam_uah'], float)
        self.assertGreaterThan(prices['mannco_usd'], 0)
        self.assertGreaterThan(prices['dmarket_usd'], 0)
        self.assertGreaterThan(prices['steam_uah'], 0)

    def assertGreaterThan(self, val, target):
        self.assertTrue(val > target, f"{val} is not greater than {target}")

if __name__ == "__main__":
    unittest.main()
