from contextlib import contextmanager
import mysql.connector
from mysql.connector import pooling
from app import config

_pool = None

def get_raw_connection():
    global _pool
    if _pool is None:
        try:
            _pool = pooling.MySQLConnectionPool(
                pool_name="gatepass_pool", pool_size=5, pool_reset_session=True,
                host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER,
                password=config.DB_PASSWORD, database=config.DB_NAME, connection_timeout=5
            )
        except Exception:
            _pool = False
    if _pool:
        try:
            return _pool.get_connection()
        except Exception:
            pass
    return mysql.connector.connect(
        host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER,
        password=config.DB_PASSWORD, database=config.DB_NAME, connection_timeout=5
    )

@contextmanager
def get_db_cursor(commit: bool = False, dictionary: bool = True):
    conn = get_raw_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor, conn
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass
