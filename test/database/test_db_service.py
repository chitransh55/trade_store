import pytest
from app.database.db_service import DBService
from pathlib import Path
from app.model.trade_transaction import TradeTransaction

@pytest.fixture(scope="session")
def database():
    TEST_DATABASE_PATH = Path("./test_db/default.db").resolve()
    db = DBService(TEST_DATABASE_PATH, "trader_trans", 10)
    return db

def test_database(database):
    assert database is not None

def test_connection(database):
    conn = database._connect()
    assert conn is not None

def test_get_version(database):
    trade_id = "T1"
    query = f" SELECT version FROM trader_trans WHERE trade_id = '{trade_id}' ORDER BY version DESC LIMIT 1;"
    result = database.execute(query, None)
    assert result is None or len(result) <= 1


def test_insertion(database):
    data ={
        "trade_id": "T1",
        "version": 1,
        "counter_party_id": "ABC Bank",
        "portfolio_id": "B1",
        "maturity_date": "27/02/2026",
    }
    trade_data = TradeTransaction.model_validate(data)
    rowid = database.save(trade_data)
    assert rowid is not None




