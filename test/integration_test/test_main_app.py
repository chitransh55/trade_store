import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.trade_app import app

client = TestClient(app)

@pytest.fixture(scope="session",autouse=True)
def cleanup_database():
    yield
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    DB_PATH = PROJECT_ROOT / "data" / "dws.db"
    path = Path(DB_PATH)
    conn = sqlite3.connect(str(path))
    try:
        conn.execute("DROP TABLE trader_trans;")
        conn.commit()
    finally:
        conn.close()

def test_missing_trade_id():
    data = {
        "trade_id": "",
        "version": 1,
        "counter_party_id": "ABC Bank",
        "portfolio_id": "I1",
        "maturity_date": "27/02/2027",
    }
    expected_output = "trade_id has not defined in the request, Kindly provide trade_id."
    response = client.post("/api/trade", json=data)
    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert response.json()["message"] == expected_output

def test_missing_version():
    data = {
        "trade_id": "I1",
        "counter_party_id": "ABC Bank",
        "portfolio_id": "I1",
        "maturity_date": "27/02/2027",
    }
    expected_output = "Version has not defined for I1, kindly provide version in the request."
    response = client.post("/api/trade", json=data)
    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert response.json()["message"] == expected_output

def test_missing_counter_party():
    data = {
        "trade_id": "I1",
        "version": 1,
        "portfolio_id": "I1",
        "maturity_date": "27/02/2027",
    }
    expected_output = "counter_party_id has not defined for I1, kindly provide counter_party_id in the request."
    response = client.post("/api/trade", json=data)
    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert response.json()["message"] == expected_output

def test_missing_portfolio_id():
    data = {
        "trade_id": "I1",
        "version": 1,
        "counter_party_id": "ABC Bank",
        "maturity_date": "27/02/2027",
    }
    expected_output = "portfolio_id has not defined for I1, kindly provide portfolio_id in the request."
    response = client.post("/api/trade", json=data)
    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert response.json()["message"] == expected_output

def test_missing_maturity_date():
    data = {
        "trade_id": "I1",
        "version": 1,
        "portfolio_id": "I1",
        "counter_party_id": "ABC Bank",
    }
    expected_output = "maturity_date has not defined for I1, kindly provide maturity_date in the request."
    response = client.post("/api/trade", json=data)
    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert response.json()["message"] == expected_output

def test_integration_insertion_of_data():
    data = {
        "trade_id": "I1",
        "version": 1,
        "counter_party_id": "ABC Bank",
        "portfolio_id": "IB1",
        "maturity_date": "27/02/2027",
    }
    response = client.post("/api/trade", json=data)
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Trade added successfully"

def test_intigration_if_record_expired():
    data = {
        "trade_id": "IE1",
        "version": 1,
        "counter_party_id": "XBC Bank",
        "portfolio_id": "IB4",
        "maturity_date": "27/02/2026",
    }

    response = client.post("/api/trade", json=data)
    assert response.json()["message"] == "Record maturity date already expired"

def test_data_intigration_lower_version():
    data = {
        "trade_id": "IL4",
        "version": 4,
        "counter_party_id": "XBC Bank",
        "portfolio_id": "IB4",
        "maturity_date": "27/12/2027",
    }
    response = client.post("/api/trade", json=data)
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Trade added successfully"

    lower_v_data = {
        "trade_id": "IL4",
        "version": 2,
        "counter_party_id": "ABC Bank",
        "portfolio_id": "IB4",
        "maturity_date": "27/12/2027",
    }
    response = client.post("/api/trade", json=lower_v_data)
    expected_output = "Record already persist with higher version of transaction so will discard IL4 with version 2 record."
    assert response.json()["message"] == expected_output

def test_search():
    data = {
        "trade_id": "IL4",
        "version": 4,
    }
    response = client.post("/api/search", json=data)
    output = response.json()
    assert output[0].get("version") == 4
    assert output[0].get("trade_id") == "IL4"
    assert output[0].get("counter_party_id") == "XBC Bank"

def test_search_without_version():
    data = {
        "trade_id": "IL4"
    }
    response = client.post("/api/search", json=data)
    output = response.json()
    assert output[0].get("version") == 4
    assert output[0].get("trade_id") == "IL4"
    assert output[0].get("counter_party_id") == "XBC Bank"

def test_search_without_trade_id():
    data = {
        "trade_id": ""
    }
    response = client.post("/api/search", json=data)
    expected_output = "trade_id has not defined in the request, Kindly provide trade_id."
    assert response.json()["message"] == expected_output

def test_expiry_job():
    data = {
        "trade_id": "EXP1",
        "version": 1,
        "counter_party_id": "XBC Bank",
        "portfolio_id": "EX11",
        "maturity_date": "27/12/2027",
    }
    client.post("/api/trade", json=data)
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    DB_PATH = PROJECT_ROOT / "data" / "dws.db"
    path = Path(DB_PATH)
    conn = sqlite3.connect(str(path))
    try:
        conn.execute(""" UPDATE trader_trans SET maturity_date = '27/02/2026' WHERE trade_id = 'EXP1'""")
        conn.commit()
    finally:
        conn.close()
    response = client.post("/api/run_expiry")
    assert response.json()["status"] == "job has successfully updated the expiry."