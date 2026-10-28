"""One spreadsheet row per handled request (backlog B3), upserted by request id."""
import csv
import datetime
import io
import os

from . import paths, records

FILE = 'suivi-demandes.csv'
HEADER = ['Date', 'Identifiant', 'Adhérent', 'Thème', 'Service', 'Canal', 'Statut', 'Brouillon']
SERVICES = {'hr': 'RH', 'legal': 'Juridique / Général', 'communication': 'Communication',
            'sp': 'SP', 'ca': 'CA', 'internal': 'Vie interne', 'reception': 'Standard'}
CHANNELS = {'appel', 'rdv', 'mail'}


def text(payload, name):
    value = payload.get(name)
    if not isinstance(value, str) or not value.strip() or len(value) > 200 or any(ord(c) < 32 for c in value):
        raise ValueError(name + ' : texte non vide de 200 caractères au plus, sur une ligne')
    return value.strip()


def cell(value):
    # Spreadsheet formula injection: a leading =, +, -, @ is kept as plain text.
    return "'" + value if value[:1] in ('=', '+', '-', '@') else value


def latest_revision(state, request):
    if not isinstance(request, str) or not records.ID_PATTERN.fullmatch(request):
        raise ValueError('request-id invalide')
    try:
        requests = paths.directory(state, 'requests')
        try:
            request_fd = paths.directory(requests, request)
        finally:
            os.close(requests)
    except FileNotFoundError:
        raise ValueError('Aucun brouillon enregistré pour cette demande : enregistrer le brouillon avant le suivi')
    try:
        revisions = sorted(name for name in os.listdir(request_fd) if records.REVISION_PATTERN.fullmatch(name))
        if not revisions:
            raise ValueError('Aucun brouillon enregistré pour cette demande : enregistrer le brouillon avant le suivi')
        activity, _ = records.load_revision(request_fd, request, revisions[-1])
        return activity
    finally:
        os.close(request_fd)


def read_rows(root_fd, required=False):
    try:
        data = paths.read_bytes(root_fd, FILE)
    except FileNotFoundError:
        if required:
            raise ValueError(FILE + ' introuvable : aucune demande suivie dans ce dossier')
        return []
    rows = list(csv.reader(io.StringIO(data.decode('utf-8-sig')), delimiter=';'))
    if not rows or rows[0] != HEADER:
        raise ValueError(FILE + ' existe avec un autre en-tête : fichier laissé intact')
    return rows[1:]


def track(root, request, payload):
    if not isinstance(payload, dict) or set(payload) != {'adherent', 'theme', 'channel'}:
        raise ValueError('Le suivi contient exactement adherent, theme et channel')
    adherent, theme = text(payload, 'adherent'), text(payload, 'theme')
    if payload['channel'] not in CHANNELS:
        raise ValueError('channel : appel, rdv ou mail')
    with paths.managed_root(root) as (root_fd, state):
        if state is None:
            raise ValueError('Aucun brouillon enregistré pour cette demande : enregistrer le brouillon avant le suivi')
        activity = latest_revision(state, request)
        rows = read_rows(root_fd)
        previous = next((row for row in rows if len(row) > 1 and row[1] == request), None)
        date = previous[0] if previous else datetime.date.today().isoformat()
        row = [date, request, cell(adherent), cell(theme), SERVICES[activity['department']],
               payload['channel'], 'brouillon', activity['draftPath']]
        rows = [row if existing is previous else existing for existing in rows] if previous else rows + [row]
        buffer = io.StringIO()
        csv.writer(buffer, delimiter=';', lineterminator='\r\n').writerows([HEADER, *rows])
        paths.replace_file(root_fd, FILE, ('﻿' + buffer.getvalue()).encode('utf-8'))
    return {'status': 'tracked', 'trackingPath': root.rstrip('/') + '/' + FILE, 'requestId': request}
