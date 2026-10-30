class TradeStoreError(Exception):
    """Base exception for expected trade-store errors."""


class LowerVersionError(TradeStoreError):
    """Raised when an incoming trade has a lower version than the stored trade."""


class TradeNotFoundError(TradeStoreError):
    """Raised when a requested trade does not exist."""

class DatabaseServiceError(TradeStoreError):
    """Raised when an error is in DBService operations."""

class InvalidMaturityDateError(TradeStoreError):
    """Raised when a new or updated trade is already past maturity."""

class DataInsertionError(TradeStoreError):
    """ Raise when SQLITE insertion has failed """

class MissingValueError(TradeStoreError):
    """ Raise when required field was missed """