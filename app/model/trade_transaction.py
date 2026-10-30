from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


def initialize_expired(maturity_date: str):
    today = date.today()
    if maturity_date is not None:
        if datetime.strptime(maturity_date, "%d/%m/%Y").date() > today:
            return "N"
        else:
            return "Y"

class TradeTransaction(BaseModel):
    trade_id: str =  None
    version: int = None
    counter_party_id: str = None
    portfolio_id: str =  None
    maturity_date: str = None
    created_date: date | None = Field(
        default_factory=lambda: datetime.now().strftime("%d/%m/%Y")
    )
    expired: str | None = None

    @model_validator(mode="after")
    def set_expired(self):
        self.expired = initialize_expired(self.maturity_date)
        return self