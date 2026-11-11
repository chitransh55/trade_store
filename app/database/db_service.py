import sqlite3
from datetime import date

from app.common.exception import DatabaseServiceError
from app.model.trade_transaction import TradeTransaction

TRADE_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS trader_trans (
    trade_id         TEXT    NOT NULL,
    version          INTEGER NOT NULL,
    counter_party_id TEXT,
    portfolio_id     TEXT,
    maturity_date    TEXT    NOT NULL,
    created_date     TEXT DEFAULT (
        strftime('%d/%m/%Y', 'now', 'localtime')
    ),
    expired          TEXT    NOT NULL DEFAULT 'N' CHECK (expired IN ('Y', 'N')),
    PRIMARY KEY (trade_id, version)
)
"""


class DBService:

    def __init__(self, db_path, trader_table_name, db_timeout):
        self.DATABASE_PATH = db_path
        self.TRADER_TABLE_NAME = trader_table_name
        self.DB_TIMEOUT = db_timeout
        self._initialize()

    def _connect(self):
        # Create the database directory if it does not exist.
        self.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(
            str(self.DATABASE_PATH),
            timeout=self.DB_TIMEOUT
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 10000")
        return conn

    def _initialize(self):
        with self._connect() as conn:
            conn.execute(TRADE_TABLE_SCHEMA)

    def execute(self, query, params=None):
        with self._connect() as conn:
            cursor = conn.execute(query)
            row = cursor.fetchall()
            return row if row else None

    def save(self, transaction_data: TradeTransaction):
        try:
            with self._connect() as conn:
                cursor = conn.execute("""
                    INSERT INTO trader_trans (trade_id, version, counter_party_id, portfolio_id, maturity_date, created_date, expired)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(trade_id, version) DO UPDATE SET
                        counter_party_id = excluded.counter_party_id,
                        portfolio_id = excluded.portfolio_id,
                        maturity_date = excluded.maturity_date,
                        created_date = excluded.created_date,
                        expired = excluded.expired""",
                             (
                                 transaction_data.trade_id,
                                 transaction_data.version,
                                 transaction_data.counter_party_id,
                                 transaction_data.portfolio_id,
                                 transaction_data.maturity_date,
                                 transaction_data.created_date,
                                 transaction_data.expired
                             )
                )
                data = cursor.lastrowid
                return data
        except sqlite3.IntegrityError as e:
            raise DatabaseServiceError(f"Database operation failed: {e}") from e

        except sqlite3.OperationalError as e:
            raise DatabaseServiceError(f"Database operation failed: {e}") from e

        except sqlite3.Error as e:
            raise DatabaseServiceError(f"Database operation failed: {e}") from e

    def search(self, trade_id: str, version: int):
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            if version is not None:
                cursor = conn.execute("""Select *
                                         FROM trader_trans
                                         WHERE trade_id = ?
                                           AND version = ?""", (trade_id, version))
            else:
                cursor = conn.execute("""Select *
                                         FROM trader_trans
                                         WHERE trade_id = ?""", (trade_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def _get_expired_records(self):
        today = date.today().strftime("%Y-%m-%d")
        expired_data_query = """
                    SELECT *
                    FROM trader_trans
                    WHERE DATE(
                                SUBSTR(maturity_date, 7, 4) || '-' ||
                                SUBSTR(maturity_date, 4, 2) || '-' ||
                                SUBSTR(maturity_date, 1, 2)
                    ) < ?
        """

        with self._connect() as conn:
            cursor = conn.execute(expired_data_query, (today,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def run_expired(self, updated_value):
        expired_data = self._get_expired_records()
        if expired_data is not None and len(expired_data) >= 1:
            update_expired_flag_query = """
            UPDATE trader_trans
            SET expired = ?
            where trade_id = ? and version = ?
            """
            with self._connect() as conn:
                for tran in expired_data:
                    conn.execute(update_expired_flag_query, (updated_value, tran.get('trade_id'), tran.get('version')))
                    conn.commit()

