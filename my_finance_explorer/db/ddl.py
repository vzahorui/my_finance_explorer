import sqlite3


CREATE_TABLE_ACCOUNTS = """
CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    currency TEXT,
    type TEXT,
    balance REAL NOT NULL,
    yield_percent REAL,
    yield_period TEXT,
    is_taxable BOOLEAN,
    expiration_date TEXT
);
"""

CREATE_TABLE_TRANSACTIONS = """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY,
    account_id INTEGER,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts (account_id)
);
"""

with sqlite3.connect('finance_db.db') as conn:
    conn.execute('''DROP TABLE IF EXISTS accounts;''')
    conn.execute(CREATE_TABLE_ACCOUNTS)
    conn.execute('''DROP TABLE IF EXISTS transactions;''')
    conn.execute(CREATE_TABLE_TRANSACTIONS)
