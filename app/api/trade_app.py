from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from app.service.trade import Trade
from app.model.trade_transaction import TradeTransaction
from app.common.exception import MissingValueError, InvalidMaturityDateError, LowerVersionError, TradeStoreError
from app.common.Config import Config

service = Trade(
    Config.DATABASE_PATH,
    Config.TABLE_NAME,
    Config.DB_TIMEOUT
)

app = FastAPI(
    title="Trade Store API",
    version="1.0",
    description="Trade API is used to save the transaction data into SQLite"
)

"""
 Create FastAPI to to receive posted JSON data.
 
"""
@app.exception_handler(MissingValueError)
async def missing_value_exception_handler(
    request: Request,
    exc: MissingValueError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "error",
            "message": str(exc)
        }
    )

def exception_builder_msg(exc: TradeStoreError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
                    "status": "error",
                    "message": str(exc)
                }
    )


@app.post("/api/trade", status_code=status.HTTP_201_CREATED)
async def trade(data: TradeTransaction):
    if data.trade_id is None or data.trade_id == "":
        raise MissingValueError("trade_id has not defined in the request, Kindly provide trade_id.")

    if data.version is None or data.version < 1:
        raise MissingValueError(f"Version has not defined for {data.trade_id}, kindly provide version in the request.")

    if data.counter_party_id is None or data.counter_party_id == "":
        raise MissingValueError(f"counter_party_id has not defined for {data.trade_id}, kindly provide counter_party_id in the request.")

    if data.portfolio_id is None or data.portfolio_id == "":
        raise MissingValueError(f"portfolio_id has not defined for {data.trade_id}, kindly provide portfolio_id in the request.")

    if data.maturity_date is None:
        raise MissingValueError(f"maturity_date has not defined for {data.trade_id}, kindly provide maturity_date in the request.")
    try :
        rowid = service.save_trade(data)
        return {
            "status": "success",
            "message": "Trade added successfully",
            "rowid": rowid
        }
    except InvalidMaturityDateError as e:
        return exception_builder_msg(e)
    except LowerVersionError as ex:
        return exception_builder_msg(ex)

@app.get("/")
def home():
    return {"message": "Trade Store API is running"}
