import os, glob, py_compile
from dotenv import load_dotenv

load_dotenv()

def print_check(msg, ok):
    print(f"  [{'✓' if ok else '✗'}] {msg}")

def main():
    print("\n--- GatePass Health Check ---")
    for name, mod in [("FastAPI", "fastapi"), ("MySQL Connector", "mysql.connector"), ("Pwdlib", "pwdlib")]:
        try:
            __import__(mod); print_check(name, True)
        except ImportError as e:
            print_check(name, False)

    for f in glob.glob("app/**/*.py", recursive=True) + ["setup_db.py"]:
        try:
            py_compile.compile(f, doraise=True); print_check(f, True)
        except Exception:
            print_check(f, False)

    try:
        import jinja2
        env = jinja2.Environment(loader=jinja2.FileSystemLoader("app/templates"))
        for t in ["base.html", "login.html", "dashboard.html", "visitors_new.html", "visitors_list.html",
                  "residents.html", "staff.html", "approvals.html", "gate.html", "deliveries.html",
                  "history.html", "reports.html", "error.html"]:
            env.get_template(t); print_check(f"app/templates/{t}", True)
    except Exception as e:
        print_check("Templates", False)

    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"), port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"), password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "gatepass_db"), connection_timeout=3
        )
        print_check("MySQL Database Connection", True)
        cur = conn.cursor()
        cur.execute("SHOW TABLES")
        tables = [r[0] for r in cur.fetchall()]
        print_check(f"Database Tables ({len(tables)} detected)", len(tables) >= 7)
        cur.close(); conn.close()
    except Exception as err:
        print_check("MySQL Connection", False)

    print("\nHealth check completed!\n")

if __name__ == "__main__":
    main()
