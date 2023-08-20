import sqlite3
import pathlib
from datetime import date

import streamlit as st
import pandas as pd

from helpers.config import account_table_config, transactions_table_config


def read_accounts_data() -> pd.DataFrame:
    with sqlite3.connect(pathlib.Path('db') / 'finance_db.db') as conn:
        cur = conn.execute('''SELECT * FROM accounts''')
        pandas_df = pd.DataFrame(cur.fetchall(), columns=account_table_config.keys())
        pandas_df['expiration_date'] = pd.to_datetime(pandas_df['expiration_date'])
        return pandas_df


def update_data(accounts_table_state: dict, accounts: pd.DataFrame):
    """Change values in the database based on the edits to the accounts data."""
    if not accounts_table_state:  # if no change was applied
        return
    with sqlite3.connect(pathlib.Path('db') / 'finance_db.db') as conn:
        # Check new rows
        if accounts_table_state['added_rows']:
            for r in accounts_table_state['added_rows']:
                # Prepare a query and run INSERT statement into accounts table
                used_columns = ', '.join(r.keys())
                placeholders_for_used_columns = ':' + ', :'.join(r.keys())
                query = f'''INSERT INTO accounts ({used_columns}) 
                VALUES ({placeholders_for_used_columns})'''
                conn.execute(query, r)

                # Add corresponding transactions into transactions table
                query = f'''INSERT INTO transactions 
                            (account_id, date, amount, description) 
                            VALUES (?, ?, ?, ?)'''
                affected_account = r['account_id']
                transaction_date = date.today().isoformat()
                transaction_amount = r['balance']
                transaction_description = 'Initializing'
                conn.execute(
                    query,
                    (affected_account, transaction_date, transaction_amount, transaction_description)
                )
        # Check modified rows
        if accounts_table_state['edited_rows']:
            for r in accounts_table_state['edited_rows']:
                # Prepare and run an UPDATE statement over accounts table
                formatted_pairs = [f"{key} = :{key}" for key in accounts_table_state['edited_rows'][r].keys()]
                # produce something like "SET col1 = :col1, col2 = :col2"
                set_string = "SET " + ", ".join(formatted_pairs)
                affected_account = int(accounts.loc[r, 'account_id'])  # convert from numpy.int64
                query = f'''UPDATE accounts 
                {set_string} WHERE account_id = :account_id'''
                params = accounts_table_state['edited_rows'][r].copy()
                params['account_id'] = affected_account
                conn.execute(query, params)

                if 'balance' in params:
                    # Add corresponding transactions into transactions table
                    previous_balance = float(accounts.loc[r, 'balance'])
                    transaction_amount = params['balance'] - previous_balance
                    transaction_description = 'Adjustment'
                    transaction_date = date.today().isoformat()
                    query = f'''INSERT INTO transactions
                    (account_id, date, amount, description)
                    VALUES (?, ?, ?, ?)'''
                    conn.execute(
                       query,
                       (affected_account, transaction_date, transaction_amount, transaction_description)
                    )
        # Check deleted rows
        if accounts_table_state['deleted_rows']:
            for r in accounts_table_state['deleted_rows']:
                # Prepare a query and run DELETE statement over accounts table
                affected_account = int(accounts.loc[r, 'account_id'])
                query = f'''DELETE FROM accounts WHERE account_id = ?'''
                conn.execute(query, (affected_account,))

                # Add corresponding transactions into transactions table
                query = f'''INSERT INTO transactions 
                        (account_id, date, amount, description) 
                        VALUES (?, ?, ?, ?)'''
                transaction_date = date.today().isoformat()
                transaction_amount = -float(accounts.loc[r, 'balance'])
                transaction_description = 'Account liquidation'
                conn.execute(
                    query,
                    (affected_account, transaction_date, transaction_amount, transaction_description)
                )
        conn.commit()
        return


def run_transactions(transactions_table_state: dict, accounts: pd.DataFrame):
    """Change the values in the database based on the transactions input."""
    if not transactions_table_state:  # if no change was applied
        return

    with sqlite3.connect(pathlib.Path('db') / 'finance_db.db') as conn:
        for r in transactions_table_state['added_rows']:
            affected_account = r['account_id']
            transaction_amount = r['amount']
            transaction_date = r['date']
            transaction_description = r.get('description', 'Absent')

            filtered_accounts_table = accounts.loc[accounts['account_id'] == affected_account]
            if filtered_accounts_table.empty:
                st.warning(f'The specified account Id {affected_account} does not exist.')
                continue

            affected_account_balance = filtered_accounts_table['balance'].iloc[0]
            new_balance = affected_account_balance + transaction_amount
            # Run UPDATE statement over accounts table
            query = f'''UPDATE accounts 
            SET balance = :new_balance WHERE account_id = :account_id'''
            params = {'new_balance': new_balance, 'account_id': affected_account}
            conn.execute(query, params)
            # Run INSERT statement into transactions table
            query = f'''INSERT INTO transactions 
            (account_id, date, amount, description) 
            VALUES (?, ?, ?, ?)'''
            conn.execute(
                query,
                (affected_account, transaction_date, transaction_amount, transaction_description)
            )
        conn.commit()


accounts_from_db = read_accounts_data()
transactions_placeholder = pd.DataFrame(columns=['account_id', 'date', 'amount', 'description'])

# Make the layout
st.title('My finances')
st.data_editor(accounts_from_db, key='accounts_table',
               num_rows='dynamic', column_config=account_table_config)
st.button(
    'Update accounts', on_click=update_data,
    args=(st.session_state['accounts_table'], accounts_from_db)
)

st.divider()

st.header('Transactions input')
st.data_editor(transactions_placeholder, key='transactions_table',
               num_rows='dynamic', column_config=transactions_table_config)

# st.write(st.session_state['accounts_table'])  # view the edited data

st.button(
    'Submit transactions', on_click=run_transactions,
    args=(st.session_state['transactions_table'], accounts_from_db)
)

# st.write(st.session_state['transactions_table'])  # view the edited data
