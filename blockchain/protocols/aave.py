"""Aave protocol connector."""

import logging

logger = logging.getLogger(__name__)


class AaveConnector:
    """Connector for Aave lending protocol."""

    def __init__(self, arc_client):
        """Initialize Aave connector."""
        self.arc_client = arc_client

    def deposit(self, token: str, amount: float) -> bool:
        """Deposit into Aave."""
        try:
            logger.info(f"Depositing {amount} {token} to Aave")
            return True
        except Exception as e:
            logger.error(f"Error depositing to Aave: {e}")
            return False

    def withdraw(self, token: str, amount: float) -> bool:
        """Withdraw from Aave."""
        try:
            logger.info(f"Withdrawing {amount} {token} from Aave")
            return True
        except Exception as e:
            logger.error(f"Error withdrawing from Aave: {e}")
            return False

    def get_apy(self, token: str) -> float:
        """Get APY for token."""
        try:
            logger.info(f"Getting Aave APY for {token}")
            return 0.0
        except Exception as e:
            logger.error(f"Error getting Aave APY: {e}")
            return 0.0
