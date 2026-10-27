#!/usr/bin/env python3
"""Create an identity-bearing per-run Markdown journal; append observations."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import uuid
from safe_paths import directory as checked_directory, destination

IDENTITY_KEYS = ['agent', 'agent_id', 'id_source', 'model', 'model_source',
                 'user', 'task', 'skill_version', 'timezone']
ENTRY_KEYS = ['goal', 'actions', 'files', 'checks', 'result', 'user_decision', 'next_step']


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def read_object(path):
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError('Ожидается JSON-объект')
    return value


def checked_dir(root):
    directory = checked_directory(root, 'agent-logs')
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def start(root, identity_file, language='ru'):
    data = read_object(identity_file)
    for key in IDENTITY_KEYS:
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f'Нужно непустое поле {key}; неизвестное обозначить явно')
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:12]
    directory = checked_dir(root)
    metadata = directory / f'{run_id}.identity.json'
    journal = directory / f'{run_id}.md'
    metadata.write_text(json.dumps({**data, 'run_id': run_id, 'started_utc': utc()}, ensure_ascii=False, indent=2), encoding='utf-8')
    with journal.open('x', encoding='utf-8') as f:
        heading = 'Work log' if language == 'en' else 'Рабочий лог'
        f.write(f'# {heading} {run_id}\n\n')
        for key in IDENTITY_KEYS:
            f.write(f'- {key}: {data[key]}\n')
        f.write(f'- started_utc: {utc()}\n\n')
    return {'run_id': run_id, 'journal': str(journal), 'identity': str(metadata), 'cloud_synced': False}


def append(root, run_id, entry_file):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', run_id):
        raise ValueError('Недопустимый run-id')
    directory = checked_dir(root)
    journal = directory / f'{run_id}.md'
    identity = directory / f'{run_id}.identity.json'
    if journal.is_symlink() or identity.is_symlink() or not journal.is_file() or not identity.is_file():
        raise ValueError('Не найден собственный лог с identity; сначала выполнить start')
    data = read_object(entry_file)
    if not isinstance(data.get('goal'), str) or not data['goal'].strip():
        raise ValueError('Нужно непустое поле goal')
    if not isinstance(data.get('result'), str) or not data['result'].strip():
        raise ValueError('Нужно непустое поле result')
    parts = [f'\n## {utc()}\n']
    for key in ENTRY_KEYS:
        value = data.get(key)
        if value is None:
            continue
        if isinstance(value, list) and all(isinstance(v, str) for v in value):
            parts += [f'\n**{key}**\n', *(f'- {v}\n' for v in value)]
        elif isinstance(value, str):
            parts += [f'\n**{key}:** {value}\n']
        else:
            raise ValueError(f'{key}: ожидается строка или массив строк')
    raw = ''.join(parts).encode('utf-8')
    # один владелец run-id; O_APPEND сохраняет предыдущие записи
    fd = os.open(journal, os.O_WRONLY | os.O_APPEND)
    try:
        count = os.write(fd, raw)
        if count != len(raw):
            raise OSError('Неполная запись лога; проверить файл перед повтором')
        os.fsync(fd)
    finally:
        os.close(fd)
    return {'journal': str(journal), 'appended_bytes': count, 'cloud_synced': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('start'); a.add_argument('root', type=Path); a.add_argument('--identity', type=Path, required=True); a.add_argument('--language', choices=['ru', 'en'], default='ru')
    a = sub.add_parser('append'); a.add_argument('root', type=Path); a.add_argument('--run-id', required=True); a.add_argument('--entry', type=Path, required=True)
    args = p.parse_args()
    try:
        root = args.root.expanduser().resolve()
        result = start(root, args.identity, args.language) if args.command == 'start' else append(root, args.run_id, args.entry)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False)); return 2


if __name__ == '__main__':
    sys.exit(main())
