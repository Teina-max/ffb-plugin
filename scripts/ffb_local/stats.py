"""Monthly request statistics (backlog B4), derived from the B3 tracking CSV."""
import csv
import datetime
import io
import re

from . import paths, tracking

MONTH = re.compile(r'(\d{4})-(0[1-9]|1[0-2])')
HEADER = ['Catégorie', 'Valeur', 'Demandes']
# Excel in a French locale may resave the ISO dates as dd/mm/yyyy.
DATE_FORMATS = ('%Y-%m-%d', '%d/%m/%Y')


def month_of(value):
    for pattern in DATE_FORMATS:
        try:
            return datetime.datetime.strptime(value.strip(), pattern).strftime('%Y-%m')
        except ValueError:
            pass
    return None


def plain(value):
    # Undo the formula guard of tracking.cell so the guard is applied once on output.
    value = value.strip()
    return value[1:] if value[:1] == "'" and value[1:2] in ('=', '+', '-', '@') else value


def count(values):
    labels, totals = {}, {}
    for value in values:
        key = value.casefold()
        labels.setdefault(key, value)
        totals[key] = totals.get(key, 0) + 1
    ranked = sorted(totals, key=lambda key: (-totals[key], labels[key].casefold()))
    return {labels[key]: totals[key] for key in ranked}


def existing_table(root_fd, name):
    try:
        data = paths.read_bytes(root_fd, name)
    except FileNotFoundError:
        return
    rows = list(csv.reader(io.StringIO(data.decode('utf-8-sig')), delimiter=';'))
    if not rows or rows[0] != HEADER:
        raise ValueError(name + ' existe avec un autre en-tête : fichier laissé intact')


def compute(root, month):
    if not isinstance(month, str) or not MONTH.fullmatch(month):
        raise ValueError('month : format AAAA-MM')
    name = 'stats-demandes-' + month + '.csv'
    with paths.managed_root(root) as (root_fd, _):
        rows = tracking.read_rows(root_fd, required=True)
        # A row Excel truncated or emptied cannot be attributed to a month: reported, not counted.
        months = [month_of(row[0]) if len(row) >= 6 else None for row in rows]
        selected = [row for row, row_month in zip(rows, months) if row_month == month]
        result = {
            'month': month,
            'total': len(selected),
            'byService': count(plain(row[4]) for row in selected),
            'byChannel': count(plain(row[5]) for row in selected),
            'byTheme': count(plain(row[3]) for row in selected),
            'ignored': months.count(None),
        }
        existing_table(root_fd, name)
        paths.replace_file(root_fd, name, render(result))
    return {**result, 'statsPath': root.rstrip('/') + '/' + name}


def render(result):
    lines = [HEADER, ['Total', '', str(result['total'])]]
    for category, key in (('Service', 'byService'), ('Canal', 'byChannel'), ('Thème', 'byTheme')):
        lines += [[category, tracking.cell(label), str(total)] for label, total in result[key].items()]
    buffer = io.StringIO()
    csv.writer(buffer, delimiter=';', lineterminator='\r\n').writerows(lines)
    return ('﻿' + buffer.getvalue()).encode('utf-8')
