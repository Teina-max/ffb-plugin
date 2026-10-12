"""Verbatim-copy check for drafts written from source documents (backlog D2)."""
import re

WINDOW = 12  # consecutive words shared with a source = a copied passage
QUOTED = re.compile(r'«[^»]*»|"[^"]*"|“[^”]*”')


def words(text):
    return re.findall(r'\w+', text.lower())


def check(payload):
    if not isinstance(payload, dict) or set(payload) != {'draft', 'sources'}:
        raise ValueError('copy-check attend exactement draft et sources')
    draft, sources = payload['draft'], payload['sources']
    if not isinstance(draft, str) or not draft.strip():
        raise ValueError('draft doit être un texte non vide')
    if not isinstance(sources, list) or not sources or any(not isinstance(s, str) for s in sources):
        raise ValueError('sources doit être une liste non vide de textes')
    grams = set()
    for source in sources:
        tokens = words(source)
        grams.update(tuple(tokens[i:i + WINDOW]) for i in range(len(tokens) - WINDOW + 1))
    # Quoted statements are attributed citations, not copy-paste.
    tokens = words(QUOTED.sub(' ', draft))
    passages, start, end = [], None, None
    for i in range(len(tokens) - WINDOW + 1):
        if tuple(tokens[i:i + WINDOW]) in grams:
            if start is None or i > end:
                if start is not None:
                    passages.append(' '.join(tokens[start:end]))
                start = i
            end = i + WINDOW
    if start is not None:
        passages.append(' '.join(tokens[start:end]))
    return {'status': 'copied' if passages else 'ok', 'copiedPassages': passages}
