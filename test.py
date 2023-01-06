import unittest
from yugiohPrice import YGOPricesAPI

class TestYGOPricesAPI(unittest.TestCase):
    def setUp(self):
        # create an instance of the YGOPricesAPI class
        self.api = YGOPricesAPI()

    def test_search_card(self):
        # test searching for a card by name
        result = self.api.search_card(['Dark Magician'], ['name'])
        self.assertIsNotNone(result)
        # test searching for a card by set
        result = self.api.search_card(['Duelist Alliance'], ['set'])
        self.assertIsNotNone(result)
        # test searching for a card by attribute
        result = self.api.search_card(['LIGHT'], ['attribute'])
        self.assertIsNotNone(result)
        # test searching for a card with an invalid search type
        with self.assertRaises(ValueError):
            result = self.api.search_card(['Dark Magician'], ['invalid'])

    def test_get_price(self):
        # test getting the price for a card by name
        result = self.api.get_price_by_name('Dark Magician')
        self.assertIsNotNone(result)
        # test getting the price for a card by id
        result = self.api.get_price_by_id(1)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()