"""Reproduce descriptive analysis from a third-party educational launch dataset."""
from pathlib import Path
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

URL = 'https://raw.githubusercontent.com/Abhigyan-RA/SpaceX-capstone/main/dataset_part_2.csv'
OUT = Path('outputs')
OUT.mkdir(exist_ok=True)

def main():
    df = pd.read_csv(URL)
    required = {'FlightNumber','Date','LaunchSite','Orbit','Class','PayloadMass'}
    if not required.issubset(df.columns):
        raise ValueError('Missing required fields: ' + str(required - set(df.columns)))
    if df.FlightNumber.duplicated().any():
        raise ValueError('Duplicate flight numbers detected')
    if not df['Class'].isin([0,1]).all():
        raise ValueError('Class must be a binary landing outcome')
    df['Date'] = pd.to_datetime(df['Date'], errors='raise')
    print('Launches:', len(df), 'Successes:', int(df['Class'].sum()))
    for name in ('LaunchSite','Orbit'):
        tab = df.groupby(name)['Class'].agg(['count','sum','mean'])
        tab['success_pct'] = 100 * tab['mean']
        print('\n', name, '\n', tab)
        tab.to_csv(OUT / f'{name}_summary.csv')
        ax = tab['success_pct'].sort_values().plot.bar(figsize=(10,4))
        ax.set(xlabel=name, ylabel='Landing success (%)', ylim=(0,105))
        plt.tight_layout()
        plt.savefig(OUT / f'{name}_success.png', dpi=160)
        plt.close()
    year = df.groupby(df['Date'].dt.year)['Class'].agg(['count','sum','mean'])
    year['success_pct'] = year['mean'] * 100
    year.to_csv(OUT/'year_summary.csv')
    ax = year['success_pct'].plot(marker='o', figsize=(10,4))
    ax.set(xlabel='Year', ylabel='Landing success (%)', ylim=(0,105))
    plt.tight_layout()
    plt.savefig(OUT/'year_success.png', dpi=160)
    plt.close()
    copy = df.copy()
    copy['Date'] = copy['Date'].dt.strftime('%Y-%m-%d')
    with sqlite3.connect(OUT/'launches.sqlite') as conn:
        copy.to_sql('launches', conn, if_exists='replace', index=False)
    print('Saved tables, plots and SQLite database to outputs/')

if __name__ == '__main__':
    main()
