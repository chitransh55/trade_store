from pathlib import Path

import pytest

from app.common.exception import LowerVersionError
from app.model.trade_transaction import TradeTransaction
from app.service.trade import Trade


@pytest.fixture(scope="session")
def trade():
    TEST_DATABASE_PATH = Path("./test_db/default.db").resolve()
    TABLE_NAME = "trader_trans"

    trade = Trade(TEST_DATABASE_PATH, TABLE_NAME, 10)
    return trade

def test_multiple_insertion(trade):
    records = [
        {
            "trade_id": "TRADE1",
            "version": 1,
            "counter_party_id": "ABC Bank",
            "portfolio_id": "B1",
            "maturity_date": "27/02/2027",
        },
        {
            "trade_id": "TRADE1",
            "version": 2,
            "counter_party_id": "ABC Bank",
            "portfolio_id": "B2",
            "maturity_date": "27/02/2027",
        },
        {
            "trade_id": "TRADE1",
            "version": 3,
            "counter_party_id": "ABC Bank",
            "portfolio_id": "B3",
            "maturity_date": "27/12/2026",
        }
    ]

    for data in records:
        trade_data = TradeTransaction.model_validate(data)
        rowid = trade.save_trade(trade_data)
        assert rowid is not None

def test_get_latest_version(trade):
    version = trade._get_latest_version("TRADE1")
    assert 3 == version[0][0]

def test_lower_version_insertion(trade):
    data = {
            "trade_id": "TRADE1",
            "version": 5,
            "counter_party_id": "XBC Bank",
            "portfolio_id": "B5",
            "maturity_date": "27/12/2026",
        }

    trade_data = TradeTransaction.model_validate(data)
    rowid = trade.save_trade(trade_data)
    assert rowid is not None

    lovwer_version_data = {
        "trade_id": "TRADE1",
        "version": 4,
        "counter_party_id": "XBC Bank",
        "portfolio_id": "B4",
        "maturity_date": "27/12/2026",
    }

    expected_output = "Record already persist with higher version of transaction so will discard TRADE1 with version 4 record."
    older_version_data = TradeTransaction.model_validate(lovwer_version_data)
    with pytest.raises(LowerVersionError) as err:
        trade.save_trade(older_version_data)

    assert str(err.value) == expected_output

