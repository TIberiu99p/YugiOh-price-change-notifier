import configparser
import time
import requests
import json

class YGOPricesAPI():

    def __init__(self):
        self.url = "http://yugiohprices.com/api"
        # create config parser
        self.config = configparser.ConfigParser()
        # read config file
        self.config.read('config.ini')
        # check if 'card_prices' section exists, create it if it doesn't
        if not self.config.has_section('card_prices'):
            self.config.add_section('card_prices')
        # check if 'card_searches' section exists, create it if it doesn't
        if not self.config.has_section('card_searches'):
            self.config.add_section('card_searches')
        # check if 'cache' section exists, create it if it doesn't
        if not self.config.has_section('cache'):
            self.config.add_section('cache')

    def __make_request(self, url):
        """Request a resource from api"""
        try:
            request = requests.get(url)
            request.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f'Error: {err}')
            return None
        except Exception as err:
            print(f'Error: {err}')
            return None
        
        try:
            return request.json()
        except ValueError:
            print('Error: Could not parse JSON response')
            return None

    def search_card(self, search_terms, search_types):
        """Searches for a card by multiple criteria (name, set, attribute) and returns the search results"""
        # create empty list to store search results
        search_results = []
        for i in range(len(search_terms)):
            search_term = search_terms[i]
            search_type = search_types[i]
            if search_type == 'name':
                # search for cards by name
                result = self.__search_by_name(search_term)
            elif search_type == 'set':
                # search for cards by set
                result = self.__search_by_set(search_term)
            elif search_type == 'attribute':
                # search for cards by attribute
                result = self.__search_by_attribute(search_term)
            else:
                raise ValueError("Invalid search type. Choose 'name', 'set', or 'attribute'.")
            search_results += result
        # store the search results in the config file
        self.config.set('card_searches', search_terms, search_results)
        # write the updated config file
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        # return the search results
        return search_results

    def __search_by_name(self, name):
        """Searches for a card by name and returns a list of matching cards"""
        # check if the card is in the cache
        if self.config.has_option('cache', name):
            # get the cached data for the card
            cached_data = self.config.get('cache', name)
            # check if the cached data is stale
            if self.__is_cache_stale(cached_data):
                # get the current price data for the card
                price_data = self.get_price_by_name(name)
                # update the cache with the current data
                self.config.set('cache', name, price_data)
                # write the updated config file
                with open('config.ini', 'w') as configfile:
                    self.config.write(configfile)
            else:
                # use the cached data
                price_data = json.loads(cached_data)
        else:
            # get the current price data for the card
            price_data = self.get_price_by_name(name)
            # store the data in the cache
            self.config.set('cache', name, price_data)
            # write the updated config file
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
        # store the price data in the config file
        self.config.set('card_prices', name, price_data)
        # write the updated config file
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        # return the price data as a list
        return [price_data]

    def __search_by_set(self, set_name):
        """Searches for cards in a set and returns a list of matching cards"""
        # get set data for the set
        set_data = self.get_set_data(set_name)
        # create a list of cards in the set
        cards = []
        for card in set_data:
            # get the price data for each card in the set
            price_data = self.__search_by_name(card['name'])[0]
            # add the price data to the list of cards
            cards.append(price_data)
        # return the list of cards
        return cards

    def check_price_changes(self, name):
        """Checks if the price of a card has changed and returns the updated price data if it has"""
        # get the stored price data for the card
        stored_price_data = json.loads(self.config.get('card_prices', name))
        # get the current price data for the card
        current_price_data = self.__search_by_name(name)[0]
        # check if the prices have changed
        if current_price_data['prices']['low'] != stored_price_data['prices']['low'] or current_price_data['prices']['average'] != stored_price_data['prices']['average'] or current_price_data['prices']['high'] != stored_price_data['prices']['high']:
            # update the stored price data
            self.config.set('card_prices', name, current_price_data)
            # write the updated config file
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
            # return the updated price data
            return current_price_data
        # return None if the prices have not changed
        return None

    def __is_cache_stale(self, cached_data):
        """Checks if the cached data is older than the specified number of days"""
        # get the current timestamp
        current_timestamp = int(time.time())
        # get the timestamp of the cached data
        cached_timestamp = json.loads(cached_data)['timestamp']
        # check if the difference between the timestamps is greater than the specified number of days
        if (current_timestamp - cached_timestamp) / 86400 > self.cache_expiry:
            return True
        return False

    def get_price_by_name(self, name):
        """Gets the price data for a card by name"""
        url = f'{self.url}/price_for_card/{name}'
        data = self.__make_request(url)
        if data is None:
            return None
        # add a timestamp to the data
        data['timestamp'] = int(time.time())
        return data

    def get_set_data(self, set_name):
        """Gets the data for a set of cards"""
        url = f'{self.url}/set_data/{set_name}'
        data = self.__make_request(url)
        if data is None:
            return None
        return data

    