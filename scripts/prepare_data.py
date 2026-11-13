"""Подготовка Marketing A/B Testing к анализу.

Переименовывает колонки, приводит флаги к 0/1 и сохраняет компактный CSV:
user_id, group, converted, total_ads, day, hour.

Исходные поля: user id, test group (ad/psa), converted (True/False),
total ads, most ads day, most ads hour.
"""

import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
RAW = os.path.join(DATA, 'marketing_AB.csv')
OUT = os.path.join(DATA, 'experiment.csv')


def main():
    raw = pd.read_csv(RAW)
    frame = pd.DataFrame({
        'user_id': raw['user id'].astype('int64'),
        'group': raw['test group'].astype(str),
        'converted': raw['converted'].astype(bool).astype('int8'),
        'total_ads': raw['total ads'].astype('int32'),
        'day': raw['most ads day'].astype(str),
        'hour': raw['most ads hour'].astype('int8'),
    })
    frame.to_csv(OUT, index=False)

    print(f'строк: {len(frame):,}')
    print(f'группы: {frame["group"].value_counts().to_dict()}')
    print(f'конверсия: {frame.groupby("group")["converted"].mean().round(6).to_dict()}')
    print(f'{OUT}: {os.path.getsize(OUT) / 1024 / 1024:.1f} МБ')


if __name__ == '__main__':
    main()
