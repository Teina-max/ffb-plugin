"""Descriptor-relative filesystem operations on an explicitly selected root."""
import contextlib
import json
import os
import pathlib
import stat
import uuid

try:
    import fcntl
except ImportError:
    fcntl = None

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parents[2]


def checkpoint(name):
    """No-op boundary; a test subprocess may replace this callable in memory."""


def directory(parent, name, create=False):
    if create:
        try:
            os.mkdir(name, 0o700, dir_fd=parent)
            os.fsync(parent)
        except FileExistsError:
            pass
    return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)


@contextlib.contextmanager
def root_handle(root):
    required = {os.open, os.mkdir, os.rename, os.unlink}
    if fcntl is None or not required.issubset(os.supports_dir_fd):
        raise ValueError('Ce système ne fournit pas les verrous et accès relatifs POSIX requis')
    if not hasattr(os, 'O_NOFOLLOW') or not hasattr(os, 'O_DIRECTORY'):
        raise ValueError('Ce système ne fournit pas les primitives sans suivi de liens requises')
    if not os.path.isabs(root) or '..' in root.split('/'):
        raise ValueError('Choisir un chemin absolu explicite sans traversée ..')
    plugin = os.stat(PLUGIN_ROOT)
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    chain = []
    try:
        for part in root.split('/'):
            if not part or part == '.':
                continue
            child = directory(fd, part)
            chain.append((fd, part, child))
            fd = child
            current = os.fstat(fd)
            if (current.st_dev, current.st_ino) == (plugin.st_dev, plugin.st_ino):
                raise ValueError('Le dossier de travail doit être situé hors du plugin')
        checkpoint('root-open')
        yield fd
        for parent, part, child in chain:
            verify_binding(parent, part, child)
    finally:
        os.close(fd)
        for parent, _, _ in reversed(chain):
            os.close(parent)


def verify_binding(parent, name, expected):
    current = directory(parent, name)
    try:
        left, right = os.fstat(current), os.fstat(expected)
        if (left.st_dev, left.st_ino) != (right.st_dev, right.st_ino):
            raise ValueError('Le dossier sélectionné a été remplacé pendant cette opération')
    finally:
        os.close(current)


def regular(parent, name, flags=os.O_RDONLY):
    fd = os.open(name, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=parent)
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        os.close(fd)
        raise ValueError('Fichier refusé : un fichier ordinaire sans lien supplémentaire est requis')
    return fd


def read_bytes(parent, name):
    with os.fdopen(regular(parent, name), 'rb') as stream:
        return stream.read()


def decode_json(data):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Clé JSON en doublon : ' + key)
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError('Constante JSON invalide : ' + value)

    return json.loads(data, object_pairs_hook=unique_pairs, parse_constant=invalid_constant)


def encode_json(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def write_new(parent, name, data):
    with os.fdopen(regular(parent, name, os.O_WRONLY | os.O_CREAT | os.O_EXCL), 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


@contextlib.contextmanager
def managed(root, create=False):
    with managed_root(root, create) as (_, state):
        yield state


@contextlib.contextmanager
def managed_root(root, create=False):
    """Locked .ffb state plus the selected root, for files the user opens directly."""
    with root_handle(root) as root_fd:
        try:
            state = directory(root_fd, '.ffb', create)
        except FileNotFoundError:
            yield root_fd, None
            return
        try:
            lock = regular(state, 'lock', os.O_RDWR | os.O_CREAT)
            try:
                fcntl.flock(lock, fcntl.LOCK_EX)
                checkpoint('locked')
                yield root_fd, state
                verify_binding(root_fd, '.ffb', state)
            finally:
                os.close(lock)
        finally:
            os.close(state)


def atomic_profile(state, data):
    temporary = '.profile-' + uuid.uuid4().hex
    try:
        write_new(state, temporary, data)
        checkpoint('profile-staged')
        os.replace(temporary, 'profile.json', src_dir_fd=state, dst_dir_fd=state)
        os.fsync(state)
    finally:
        try:
            os.unlink(temporary, dir_fd=state)
        except FileNotFoundError:
            pass
