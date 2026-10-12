"""Immutable draft/activity pairs with request-to-source binding."""
import datetime
import os
import re
import uuid

from . import paths


ID_PATTERN = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z')
REVISION_PATTERN = re.compile(r'r[0-9]{6,}\Z')
# hr: member HR diagnostic; legal: member request reply (Juridique / Général);
# communication: content production (speeches and other drafts).
DEPARTMENTS = {'hr', 'legal', 'communication'}


def validate(request, source, payload):
    if not isinstance(request, str) or not ID_PATTERN.fullmatch(request):
        raise ValueError('request-id : 1 à 64 caractères ASCII, lettres, chiffres, _ ou -, début alphanumérique')
    if not isinstance(source, str) or not source.strip() or any(ord(c) < 32 or ord(c) == 127 for c in source):
        raise ValueError('source-ref doit être une référence explicite non vide, sans caractères de contrôle')
    if not isinstance(payload, dict) or set(payload) - {'draft', 'department', 'companyRef'}:
        raise ValueError('Le document doit contenir uniquement draft, department et éventuellement companyRef')
    if not isinstance(payload.get('draft'), str) or not payload['draft'].strip():
        raise ValueError('draft doit être un texte non vide')
    if payload.get('department') not in DEPARTMENTS:
        raise ValueError('department : parcours disponibles : ' + ', '.join(sorted(DEPARTMENTS)))
    company = payload.get('companyRef')
    if company is not None and (not isinstance(company, str) or not company.strip()):
        raise ValueError('companyRef doit être un texte non vide ou null')
    return {'draft': payload['draft'], 'department': payload['department'], 'companyRef': company}


def result(root, request, revision, reused):
    base = root.rstrip('/') + '/.ffb/requests/' + request + '/' + revision
    return {'status': 'draft', 'reused': reused, 'draftPath': base + '/draft.md',
            'activityPath': base + '/activity.json', 'revision': revision}


def load_revision(request_fd, request, revision):
    fd = paths.directory(request_fd, revision)
    try:
        if set(os.listdir(fd)) != {'draft.md', 'activity.json'}:
            raise ValueError('Révision existante incomplète ou contenant des fichiers inconnus')
        activity = paths.decode_json(paths.read_bytes(fd, 'activity.json'))
        draft = paths.read_bytes(fd, 'draft.md').decode('utf-8')
        expected = {'schemaVersion', 'requestId', 'sourceRef', 'department', 'companyRef',
                    'draftPath', 'createdAt', 'revision', 'status'}
        if not isinstance(activity, dict) or set(activity) != expected:
            raise ValueError('Métadonnées de révision invalides')
        if type(activity['schemaVersion']) is not int or activity['schemaVersion'] != 1:
            raise ValueError('schemaVersion de révision invalide')
        if activity['requestId'] != request or activity['revision'] != revision or activity['status'] != 'draft':
            raise ValueError('Identité, révision ou statut de révision invalide')
        if activity['draftPath'] != f'.ffb/requests/{request}/{revision}/draft.md':
            raise ValueError('draftPath de révision invalide')
        if not isinstance(activity['createdAt'], str):
            raise ValueError('createdAt de révision invalide')
        if datetime.datetime.fromisoformat(activity['createdAt']).tzinfo is None:
            raise ValueError('createdAt doit inclure le fuseau horaire')
        content = validate(request, activity['sourceRef'], {
            'draft': draft, 'department': activity['department'], 'companyRef': activity['companyRef'],
        })
        return activity, content
    finally:
        os.close(fd)


def publish(request_fd, request, source, revision, payload):
    stage = '.stage-' + uuid.uuid4().hex
    fd = paths.directory(request_fd, stage, create=True)
    try:
        paths.write_new(fd, 'draft.md', payload['draft'].encode('utf-8'))
        paths.checkpoint('draft-staged')
        activity = {
            'schemaVersion': 1, 'requestId': request, 'sourceRef': source,
            'department': payload['department'], 'companyRef': payload['companyRef'],
            'draftPath': f'.ffb/requests/{request}/{revision}/draft.md',
            'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'revision': revision, 'status': 'draft',
        }
        paths.write_new(fd, 'activity.json', paths.encode_json(activity))
        os.fsync(fd)
        paths.checkpoint('before-publication')
        paths.verify_binding(request_fd, stage, fd)
        os.rename(stage, revision, src_dir_fd=request_fd, dst_dir_fd=request_fd)
        os.fsync(request_fd)
        paths.checkpoint('after-publication')
        paths.verify_binding(request_fd, revision, fd)
    finally:
        os.close(fd)
    # Interrupted stages are deliberately retained and ignored, never promoted or repaired.


def save(root, request, source, payload):
    payload = validate(request, source, payload)
    with paths.managed(root, create=True) as state:
        requests = paths.directory(state, 'requests', create=True)
        try:
            request_fd = paths.directory(requests, request, create=True)
            try:
                names = os.listdir(request_fd)
                revisions = []
                for name in names:
                    if re.fullmatch(r'\.stage-[a-f0-9]{32}', name):
                        stage_fd = paths.directory(request_fd, name)
                        os.close(stage_fd)
                        continue
                    if not REVISION_PATTERN.fullmatch(name):
                        raise ValueError('Fichier inconnu dans le dossier de la demande : ' + name)
                    revisions.append(name)
                match = None
                for revision in sorted(revisions):
                    activity, content = load_revision(request_fd, request, revision)
                    if activity['sourceRef'] != source:
                        raise ValueError('Ce request-id est déjà lié à une autre source-ref')
                    if content == payload:
                        match = revision
                if match:
                    paths.verify_binding(state, 'requests', requests)
                    paths.verify_binding(requests, request, request_fd)
                    return result(root, request, match, True)
                number = max((int(name[1:]) for name in revisions), default=0) + 1
                revision = f'r{number:06d}'
                publish(request_fd, request, source, revision, payload)
                paths.verify_binding(state, 'requests', requests)
                paths.verify_binding(requests, request, request_fd)
                return result(root, request, revision, False)
            finally:
                os.close(request_fd)
        finally:
            os.close(requests)
