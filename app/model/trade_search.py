from pydantic import BaseModel


class TradeSearch(BaseModel):
    trade_id: str = None
    version: int = None
