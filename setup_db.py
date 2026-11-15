import os, sys
from dotenv import load_dotenv
import mysql.connector

load_dotenv()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "gatepass_db")

def run_sql(cur, path):
    print(f"Executing {path}...")
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    stmt = []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("--"):
            continue
        stmt.append(line)
        if s.endswith(";"):
            sql = "".join(stmt).strip()
            stmt = []
            if sql:
                try:
                    cur.execute(sql)
                except mysql.connector.Error as err:
                    if "already exists" not in str(err).lower():
                        print(f"Notice: {err.msg}")

def main():
    print(f"Connecting to MySQL ({DB_HOST}:{DB_PORT}) as {DB_USER}...")
    try:
        conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, autocommit=True)
    except mysql.connector.Error as err:
        print(f"[ERROR] Failed to connect: {err.msg}"); sys.exit(1)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4;")
    cur.execute(f"USE `{DB_NAME}`;")
    for f in ["database/schema.sql", "database/seed.sql"]:
        if os.path.exists(f): run_sql(cur, f)
    cur.close(); conn.close()
    print("\n[SUCCESS] GatePass database initialization completed!")

if __name__ == "__main__":
    main()
