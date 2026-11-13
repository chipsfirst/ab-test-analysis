"""Скачивание датасета Marketing A/B Testing с Kaggle.

Датасет: faviovaz/marketing-ab-testing, лицензия CC0 1.0 (public domain).
Источник: https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing
Файл: marketing_AB.csv, 588 101 строка.

Скрипт не требует авторизации: Kaggle отдаёт публичные датасеты по прямой ссылке.
"""

import hashlib
import os
import urllib.request
import zipfile

URL = 'https://www.kaggle.com/api/v1/datasets/download/faviovaz/marketing-ab-testing'
ZIP_SHA256 = '669e02e4c032d8378f59b73a1dbc52e5d0c396286d787de62570cda0b1d977f0'
CSV_NAME = 'marketing_AB.csv'

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    os.makedirs(DATA, exist_ok=True)
    zip_path = os.path.join(DATA, 'marketing-ab.zip')
    csv_path = os.path.join(DATA, CSV_NAME)

    if os.path.exists(csv_path):
        print(f'{csv_path} уже есть')
        return

    if not os.path.exists(zip_path):
        print(f'скачиваю {URL}')
        urllib.request.urlretrieve(URL, zip_path)

    actual = sha256(zip_path)
    if actual != ZIP_SHA256:
        raise SystemExit(f'контрольная сумма не совпала: {actual}')

    with zipfile.ZipFile(zip_path) as archive:
        archive.extract(CSV_NAME, DATA)
    print(f'{csv_path}: {os.path.getsize(csv_path) / 1024 / 1024:.0f} МБ')


if __name__ == '__main__':
    main()
