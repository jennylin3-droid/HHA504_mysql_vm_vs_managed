# managed_demo.py — Linear, step-by-step demo for managed MySQL (Azure/GCP/OCI)
# Run this file top-to-bottom OR run it cell-by-cell in VS Code.
# Prereqs:
#   pip install sqlalchemy pymysql pandas python-dotenv
#
# Env vars (populate a local .env):
#   MAN_DB_HOST, MAN_DB_PORT, MAN_DB_USER, MAN_DB_PASS, MAN_DB_NAME

import os, time
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv


def get_env():
    # Always load the .env from the project root and from the managed folder
    load_dotenv("c:/Users/jenny/Desktop/HHA504_mysql_vm_vs_managed/HHA504_mysql_vm_vs_managed/.env")
    load_dotenv("c:/Users/jenny/Desktop/HHA504_mysql_vm_vs_managed/assignment_4/.env")
    load_dotenv()

    host = os.getenv("MAN_DB_HOST")
    port = os.getenv("MAN_DB_PORT", "3306")
    user = os.getenv("MAN_DB_USER")
    password = os.getenv("MAN_DB_PASS")
    db_name = os.getenv("MAN_DB_NAME")

    print("[ENV] MAN_DB_HOST:", host)
    print("[ENV] MAN_DB_PORT:", port)
    print("[ENV] MAN_DB_USER:", user)
    print("[ENV] MAN_DB_NAME:", db_name)

    if not all([host, port, user, password, db_name]):
        raise RuntimeError("One or more MAN_DB_* env vars are missing. Check your .env file.")

    return host, port, user, password, db_name


def main():
    start = datetime.utcnow()
    host, port, user, password, db_name = get_env()

    # --- 1) Ensure the database exists (connect without DB first) ---
    server_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/"
    print(f"[STEP 1] Connecting to managed MySQL server (no DB): mysql+pymysql://{user}:*****@{host}:{port}/")

    # Disable SSL to avoid Windows cert-store hangs for this homework demo
    engine_server = create_engine(
        server_url,
        connect_args={"ssl": {"ssl_disabled": True}},
        pool_pre_ping=True,
        future=True,
    )

    try:
        with engine_server.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}`"))
            conn.commit()
            print(f"[OK] Ensured database `{db_name}` exists on managed MySQL.")
    except SQLAlchemyError as e:
        print("[ERROR] While creating/ensuring DB:", e)
        print("Check networking, authorized IPs in Cloud SQL, and your MAN_DB_* credentials.")
        raise

    # --- 2) Connect to that specific database ---
    db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    print(f"[STEP 2] Connecting to managed DB: mysql+pymysql://{user}:*****@{host}:{port}/{db_name}")

    engine = create_engine(
        db_url,
        connect_args={"ssl": {"ssl_disabled": True}},
        pool_pre_ping=True,
        future=True,
    )

    # --- 3) Create a DataFrame and write it to a table ---
    table_name = "visits"

    df = pd.DataFrame([
        {"visit_id": 1, "patient_id": 101, "visit_date": "2025-09-01", "clinic": "primary", "minutes": 15},
        {"visit_id": 2, "patient_id": 102, "visit_date": "2025-09-02", "clinic": "urgent", "minutes": 30},
        {"visit_id": 3, "patient_id": 103, "visit_date": "2025-09-03", "clinic": "primary", "minutes": 20},
        {"visit_id": 4, "patient_id": 104, "visit_date": "2025-09-04", "clinic": "urgent", "minutes": 25},
        {"visit_id": 5, "patient_id": 105, "visit_date": "2025-09-05", "clinic": "primary", "minutes": 10}
    ])

    # Write the DataFrame to the MySQL table
    try:
        with engine.connect() as conn:
            df.to_sql(
                name=table_name,
                con=conn,
                if_exists="replace",  # Options: 'fail', 'replace', 'append'
                index=False,
                method="multi",  # Insert multiple rows at once
            )
            print(f"[OK] Wrote DataFrame to table `{table_name}` in managed MySQL.")
    except SQLAlchemyError as e:
        print("[ERROR] While writing DataFrame to table:", e)
        raise

    # --- 4) Read back the data from the table ---
    try:
        with engine.connect() as conn:
            result_df = pd.read_sql_table(table_name, con=conn)
            print(f"[OK] Read back {len(result_df)} rows from table `{table_name}`.")
            print(result_df)  # Print the actual rows
    except SQLAlchemyError as e:
        print("[ERROR] While reading table data:", e)
        raise
    duration = datetime.utcnow() - start
    print("[DONE]", duration)

    print("Script completed.")
    # --- 4) Write the DataFrame to MySQL as table `visits` ---
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)
    print(f"[STEP 3] Wrote {len(df)} rows into table `{table_name}` on managed MySQL.")

    # --- 5) Read it back and print row count ---
    df_back = pd.read_sql(f"SELECT * FROM {table_name}", con=engine)
    print("[STEP 4] Reading back row count ...")
    print(" n_rows =", len(df_back))
    print(df_back)

    # optional timing
    duration = datetime.utcnow() - start
    print(f"[DONE] Managed path completed in {duration.total_seconds():.1f}s at {datetime.utcnow().isoformat()}Z")
