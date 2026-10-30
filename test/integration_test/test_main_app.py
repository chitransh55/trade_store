from fastapi.testclient import TestClient

from app.api.trade_app import app

client = TestClient(app)



def test_endpoint():
    response = client.get("/")
    assert response.status_code == 200


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
