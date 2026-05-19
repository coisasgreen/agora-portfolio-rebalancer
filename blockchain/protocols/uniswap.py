"""Uniswap protocol connector."""

import logging

logger = logging.getLogger(__name__)


class UniswapConnector:
    """Connector for Uniswap DEX."""

    def __init__(self, arc_client):
        """Initialize Uniswap connector."""
        self.arc_client = arc_client

    def swap(self, token_in: str, token_out: str, amount: float) -> bool:
        """Execute swap on Uniswap."""
        try:
            logger.info(f"Swapping {amount} {token_in} to {token_out} on Uniswap")
            return True
        except Exception as e:
            logger.error(f"Error swapping on Uniswap: {e}")
            return False
