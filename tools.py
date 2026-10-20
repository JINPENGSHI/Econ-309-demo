import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).parent / 'data' / 'unemployment.csv'

def get_unemployment_data(start: str, end: str):
    """Return monthly unemployment observations within an inclusive YYYY-MM range."""
    for date in (start, end):
        if len(date) != 7 or date[4] != '-' or not (date[:4] + date[5:]).isdigit() or not 1 <= int(date[5:]) <= 12:
            raise ValueError('Dates must use YYYY-MM, e.g. 2007-01')
    if start > end:
        raise ValueError('Start date must be before end date')
    data = pd.read_csv(DATA_PATH)
    rows = data[(data['date'] >= start) & (data['date'] <= end)].copy()
    if rows.empty:
        raise ValueError('No observations for this date range')
    return rows

def calculate_change(first: float, last: float):
    return round(float(last) - float(first), 2)

def summarize_period(rows):
    first, last = rows.iloc[0], rows.iloc[-1]
    peak = rows.loc[rows['unemployment_rate'].idxmax()]
    return {'start': str(first['date']), 'end': str(last['date']),
            'first': float(first['unemployment_rate']), 'last': float(last['unemployment_rate']),
            'change_pp': calculate_change(first['unemployment_rate'], last['unemployment_rate']),
            'peak': float(peak['unemployment_rate']), 'peak_date': str(peak['date']),
            'observations': len(rows)}
