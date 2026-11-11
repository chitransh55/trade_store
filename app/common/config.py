from pathlib import Path


class Config:
    DB_TIMEOUT = 10
    DATABASE_PATH = Path("./data/dws.db").resolve()
    TABLE_NAME = "trader_trans"

