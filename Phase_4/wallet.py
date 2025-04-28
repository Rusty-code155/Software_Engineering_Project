#Code Written By: Turner Miles Peeples

import json
import os
import logging

# Setup logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WalletManager:
    def __init__(self):
        self.cards = []
        self.load_cards()

    def get_cards(self):
        return self.cards

    def save_cards(self):
        try:
            with open('wallet.json', 'w') as f:
                json.dump(self.cards, f, indent=4)
            logger.debug("Saved cards to file")
        except Exception as e:
            logger.error(f"Error saving cards: {e}")
            raise

    def load_cards(self):
        try:
            if os.path.exists('wallet.json'):
                with open('wallet.json', 'r') as f:
                    self.cards = json.load(f)
                logger.debug("Loaded cards from file")
            else:
                self.cards = []
                logger.debug("No wallet file found, starting with empty list")
        except Exception as e:
            logger.error(f"Error loading cards: {e}")
            self.cards = []