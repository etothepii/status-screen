import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import re

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    f"{os.environ['HOME']}/.auth/google-balances.json", scope
)

gc = gspread.authorize(credentials)


def load_sheet(sheet):
    data = sheet.get_all_values()
    headers = [re.sub(r"\s+", ' ', _) for _ in data.pop(0)]
    return pd.DataFrame(data, columns=headers)


def load_latest():
    return load_sheet(gc.open("Bank Balances").worksheet('Latest')).set_index('Account')[['Currency', 'Debit/Credit']]


def load_balances():
    balances = load_sheet(gc.open("Bank Balances").worksheet('Balances'))
    value_columns = [_ for _ in balances.columns if _ != 'Date']
    for column in value_columns:
        balances[column] = pd.to_numeric(
            balances[column].str.replace(',', '').str.replace('$', '').str.replace('£', ''), errors='coerce')
    return balances.fillna(method='ffill').fillna(value=0).melt(id_vars=["Date"], value_vars=value_columns)


def load_data():
    return load_balances().join(load_latest(), on='variable', how='left')