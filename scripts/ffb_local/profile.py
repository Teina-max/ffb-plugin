"""Versioned preferences. The explicit CLI root is the only destination authority."""
import re

from . import paths

UUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z')


def validate(profile):
    if not isinstance(profile, dict):
        raise ValueError('Le profil doit être un objet JSON')
    if type(profile.get('schemaVersion')) is not int or profile['schemaVersion'] != 1:
        raise ValueError('schemaVersion doit être le nombre entier 1')
    if not isinstance(profile.get('displayName'), str) or not profile['displayName'].strip():
        raise ValueError('displayName doit être un texte non vide')
    departments = profile.get('departments')
    supported = {'hr', 'legal', 'communication', 'management', 'meetings'}
    if not isinstance(departments, list) or not departments:
        raise ValueError('departments doit contenir au moins un pôle')
    if any(not isinstance(item, str) or item not in supported for item in departments):
        raise ValueError('departments contient un pôle inconnu')
    if len(set(departments)) != len(departments):
        raise ValueError('departments contient un doublon')
    tasks = profile.get('frequentTasks')
    if not isinstance(tasks, list) or any(not isinstance(item, str) or not item.strip() for item in tasks):
        raise ValueError('frequentTasks doit être une liste de textes non vides')
    if profile.get('outputDetail') not in ('short', 'standard', 'detailed'):
        raise ValueError('outputDetail doit être short, standard ou detailed')
    # Shared FFB workspace on the connector: an identifier, not an access right (checked server-side).
    if 'sharedTenantId' in profile:
        tenant = profile['sharedTenantId']
        if not isinstance(tenant, str) or not UUID.fullmatch(tenant.lower()):
            raise ValueError('sharedTenantId doit être un identifiant UUID')
        profile = {**profile, 'sharedTenantId': tenant.lower()}
    return profile


def read(root):
    with paths.managed(root) as state:
        if state is None:
            return {'status': 'absent'}
        try:
            profile = validate(paths.decode_json(paths.read_bytes(state, 'profile.json')))
        except FileNotFoundError:
            return {'status': 'absent'}
        return {'status': 'available', 'profile': profile}


def save(root, update):
    if not isinstance(update, dict):
        raise ValueError('La mise à jour du profil doit être un objet JSON')
    with paths.managed(root, create=True) as state:
        try:
            existing = validate(paths.decode_json(paths.read_bytes(state, 'profile.json')))
        except FileNotFoundError:
            existing = {}
        profile = validate({**existing, **update})
        paths.atomic_profile(state, paths.encode_json(profile))
        return {'status': 'saved', 'profilePath': root.rstrip('/') + '/.ffb/profile.json'}
