import streamlit as st


account_table_config = {
    'account_id': st.column_config.NumberColumn('Account Id', required=True),
    'name': st.column_config.TextColumn('Name', required=True),
    'currency': st.column_config.TextColumn('Currency', required=True),
    'type': st.column_config.TextColumn('Type', help='Could be "deposit", "obligation", "current account", etc.'),
    'balance': st.column_config.NumberColumn('Balance', default=0, format='%.2f'),
    'yield_percent': st.column_config.NumberColumn('Yield percent', format='%.2f%%'),
    'yield_period': st.column_config.TextColumn('Yield period', help='In which period the yield will capitalize'),
    'is_taxable': st.column_config.CheckboxColumn('Is taxable', default=False),
    'expiration_date': st.column_config.DateColumn('Expiration date')
}

transactions_table_config = {
    'account_id': st.column_config.NumberColumn('Account Id', required=True),
    'date': st.column_config.DateColumn('Date', required=True),
    'amount': st.column_config.NumberColumn('Amount', format='%.0f', required=True),
    'description': st.column_config.TextColumn('Description')
}