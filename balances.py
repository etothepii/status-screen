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
    return load_sheet(gc.open("Bank Balances").worksheet('Latest'))


def load_balances():
    balances = load_sheet(gc.open("Bank Balances").worksheet('Balances'))
    for column in balances.columns:
        if column == 'Date':
            continue
        balances[column] = pd.to_numeric(
            balances[column].str.replace(',', '').str.replace('$', '').str.replace('£', ''), errors='coerce')
    return balances.fillna(method='ffill').fillna(value=0)

