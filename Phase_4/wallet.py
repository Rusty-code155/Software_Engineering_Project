import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('debug.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class WalletManager:
    def __init__(self):
        self.cards = []
        logger.debug("WalletManager initialized")

    def add_card(self, number, card_type, image_path=""):
        try:
            card = {
                "Number": number,
                "Type": card_type,
                "ImagePath": image_path
            }
            self.cards.append(card)
            logger.info(f"Added card: {card_type} ending in {number[-4:]}")
        except Exception as e:
            logger.error(f"Error adding card: {e}")
            raise

    def get_cards(self):
        logger.debug("Retrieved cards")
        return self.cards