from pathlib import Path

import pytest

from app.database.db_service import DBService
from app.model.trade_transaction import TradeTransaction


@pytest.fixture(scope="session")
def database():
    TEST_DATABASE_PATH = Path("./test_db/default.db").resolve()
    db = DBService(TEST_DATABASE_PATH, "trader_trans", 10)
    return db

@pytest.fixture(scope="session",autouse=True)
def cleanup_database(database):
    yield
    conn = database._connect()
    try:
        database.execute("DROP TABLE trader_trans;")
        conn.commit()
    finally:
        conn.close()

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
        "trade_id": "TI1",
        "version": 1,
        "counter_party_id": "ABC Bank",
        "portfolio_id": "B1",
        "maturity_date": "27/02/2027",
    }
    trade_data = TradeTransaction.model_validate(data)
    rowid = database.save(trade_data)
    assert rowid is not None

def test_invalid_trade_id(database):
    output = database.search("QTEST2", None)
    assert not output

def test_search_with_trade_id(database):
    data ={
        "trade_id": "Q1",
        "version": 1,
        "counter_party_id": "ABC Bank",
        "portfolio_id": "B1",
        "maturity_date": "27/02/2027",
    }
    trade_data = TradeTransaction.model_validate(data)
    rowid = database.save(trade_data)
    assert rowid is not None

    output = database.search("Q1", None)
    assert output is not None
    assert output[0].get("version") == 1
    assert output[0].get("trade_id") == "Q1"
    assert output[0].get("counter_party_id") == "ABC Bank"
    assert output[0].get("portfolio_id") == "B1"
    assert output[0].get("maturity_date") == "27/02/2027"

def test_search_with_trade_id_and_version(database):
    data ={
        "trade_id": "Q2",
        "version": 2,
        "counter_party_id": "XBC Bank",
        "portfolio_id": "B2",
        "maturity_date": "27/02/2027",
    }
    trade_data = TradeTransaction.model_validate(data)
    rowid = database.save(trade_data)
    assert rowid is not None

    output = database.search("Q2", 2)
    assert output is not None
    assert output[0].get("version") == 2
    assert output[0].get("trade_id") == "Q2"
    assert output[0].get("counter_party_id") == "XBC Bank"
    assert output[0].get("portfolio_id") == "B2"
    assert output[0].get("maturity_date") == "27/02/2027"

def test_expiry_run(database):
    data ={
        "trade_id": "EXQ1",
        "version": 1,
        "counter_party_id": "ABC Bank",
        "portfolio_id": "B1",
        "maturity_date": "27/02/2026",
    }
    trade_data = TradeTransaction.model_validate(data)
    rowid = database.save(trade_data)
    assert rowid is not None

    database.run_expired("N")
    output = database.search("EXQ1", 1)
    assert output[0].get("version") == 1
    assert output[0].get("trade_id") == "EXQ1"
    assert output[0].get("expired") == "N"
