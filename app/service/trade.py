
from app.common.exception import InvalidMaturityDateError, LowerVersionError
from app.database.db_service import DBService
from app.model.trade_search import TradeSearch
from app.model.trade_transaction import TradeTransaction


class Trade:

    def __init__(self, database_path, table_name, timeout):
        self.database = DBService(database_path,table_name, timeout)

    """
    If higher version already saved then throw HigherVersion exception and discard the transaction.
    If trade_id and version already saved then update records.
    """

    def _get_latest_version(self, trade_id: str):
        query = f""" SELECT version FROM trader_trans WHERE trade_id = '{trade_id}' ORDER BY version DESC LIMIT 1;"""
        result = self.database.execute(query, None)
        return result


    def save_trade(self, trade_transaction: TradeTransaction):

        if trade_transaction.expired == "Y":
            raise InvalidMaturityDateError("Record maturity date already expired")

        result = self._get_latest_version(trade_transaction.trade_id)
        if result is not None and trade_transaction.version < result[0][0]:
            raise LowerVersionError(f"Record already persist with higher version of transaction so will"
                                        f" discard {trade_transaction.trade_id} with version {trade_transaction.version} record.")

        return (self.database.save(trade_transaction))



    def mark_expiry(self, query: str):
        pass

    """
    Query data from database. As of now It's support query on trade_id and version.
    Parameters: 
        query = {
            "trade_id": "<trade_id>",
            "version": "<version>",
        }
    trade_id is mandatory
    Return : Rows (List of Tuples).
    """
    def qsearch(self, trade_search: TradeSearch):
        return self.database.search(trade_search.trade_id, trade_search.version)

    def run_expired_query(self, updated_value: str):
        self.database.run_expired(updated_value)
        return "job has successfully updated the expiry."

