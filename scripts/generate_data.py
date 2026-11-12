"""Генератор данных A/B-эксперимента.

Заложенный эффект (ground truth):
    конверсия control      8.0 %
    конверсия treatment    9.8 % на мобильных, 8.8 % на десктопе
    средний чек выросших   +4 %
    доля возвратов         2.0 % против 2.1 % (эффекта нет)

Чтобы данные точно соответствовали дизайну, число конверсий в каждой
ячейке (группа × устройство) фиксируется, а сами конверсии распределяются
случайно. Иначе случайный разброс может увести наблюдаемый эффект от
заложенного — и учебный кейс будет противоречить собственной легенде.

Данные детерминированы (seed=42), пишутся в data/experiment.csv.
Только стандартная библиотека Python.
"""

import csv
import math
import os
import random

SEED = 42
N_PER_GROUP = 12_300
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'experiment.csv')

BASE_CONVERSION = 0.08
MOBILE_SHARE = 0.62
MOBILE_LIFT = 0.018
DESKTOP_LIFT = 0.008
REVENUE_LIFT = 1.04
REFUND_CONTROL = 0.020
REFUND_TREATMENT = 0.021


def lognormal_revenue(rng, mean=1800.0, sigma=0.8):
    mu = math.log(mean) - sigma ** 2 / 2
    return round(rng.lognormvariate(mu, sigma), 2)


def main():
    rng = random.Random(SEED)

    users = []
    user_id = 0
    for group in ('control', 'treatment'):
        for _ in range(N_PER_GROUP):
            user_id += 1
            users.append({
                'user_id': f'u{user_id:06d}',
                'group': group,
                'device': 'mobile' if rng.random() < MOBILE_SHARE else 'desktop',
                'converted': 0,
                'revenue': 0.0,
                'refunded': 0,
            })

    cells = {}
    for user in users:
        cells.setdefault((user['group'], user['device']), []).append(user)

    for (group, device), cell in cells.items():
        conversion = BASE_CONVERSION
        if group == 'treatment':
            conversion += MOBILE_LIFT if device == 'mobile' else DESKTOP_LIFT
        converted_count = round(len(cell) * conversion)
        for index in rng.sample(range(len(cell)), converted_count):
            cell[index]['converted'] = 1

    for user in users:
        treatment = user['group'] == 'treatment'
        if user['converted']:
            revenue = lognormal_revenue(rng)
            user['revenue'] = round(revenue * (REVENUE_LIFT if treatment else 1.0), 2)
        refund_rate = REFUND_TREATMENT if treatment else REFUND_CONTROL
        user['refunded'] = 1 if rng.random() < refund_rate else 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['user_id', 'group', 'device', 'converted', 'revenue', 'refunded'])
        writer.writeheader()
        writer.writerows(users)
    print(f'{OUT}: {len(users):,} строк')


if __name__ == '__main__':
    main()
