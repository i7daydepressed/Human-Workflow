#!/usr/bin/env python3
"""Manage an explicit private local profile. Never discover or contact a service."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import uuid

from safe_paths import destination, installation_root

SCHEMA = 1
CODE_ROOT = installation_root(__file__)
TOP_KEYS = {'schema_version', 'profile_id', 'instruction_language', 'output_language',
            'log_language', 'workspace', 'word', 'style', 'rating_scales', 'history_ref'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def private_root(path):
    path = path.expanduser().resolve()
    if path == CODE_ROOT or path.is_relative_to(CODE_ROOT):
        raise ValueError('Profile must be outside the product source/installation')
    if path.exists() and not path.is_dir():
        raise ValueError('Profile root must be a directory')
    return path


def new_root(path):
    raw = path.expanduser().absolute()
    if any(part.is_symlink() for part in [raw, *raw.parents]):
        raise ValueError('New transfer destination must not traverse a symlink')
    return private_root(raw)


def reference(value, root):
    if not isinstance(value, dict) or set(value) != {'path', 'sha256'}:
        raise ValueError('File resource must contain only path and sha256')
    if not isinstance(value['path'], str) or not value['path']:
        raise ValueError('Resource path must be a nonempty relative string')
    path = destination(root, value['path'])
    if not isinstance(value['sha256'], str) or not re.fullmatch('[a-f0-9]{64}', value['sha256']):
        raise ValueError('Resource SHA-256 is required')
    if not path.is_file() or digest(path) != value['sha256']:
        raise ValueError(f'Resource missing or hash mismatch: {value["path"]}')
    return path


def validate(data, root):
    if not isinstance(data, dict) or set(data) - TOP_KEYS:
        raise ValueError('Profile must be an object containing known fields only')
    required = {'schema_version', 'profile_id', 'instruction_language', 'output_language', 'log_language', 'word'}
    if not required.issubset(data):
        raise ValueError('Profile is missing required fields')
    if type(data.get('schema_version')) is not int or data['schema_version'] != SCHEMA:
        raise ValueError('Unsupported schema_version; existing profile is not rewritten')
    if not isinstance(data.get('profile_id'), str) or not re.fullmatch('[A-Za-z0-9_-]{1,80}', data['profile_id']):
        raise ValueError('profile_id must be a stable local identifier')
    if data.get('instruction_language') not in ['en', 'ru']:
        raise ValueError('instruction_language must be en or ru')
    for key in ['output_language', 'log_language']:
        if data.get(key) is not None and (not isinstance(data[key], str) or not re.fullmatch('[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*', data[key])):
            raise ValueError(f'{key} must be a language tag or null')
    if data.get('workspace') is not None:
        value = data['workspace']
        if not isinstance(value, dict) or set(value) != {'kind', 'locator'} or value['kind'] not in ['local', 'provider'] or not isinstance(value['locator'], str) or not value['locator']:
            raise ValueError('workspace requires kind=local/provider and a nonempty locator')
    word = data.get('word')
    if not isinstance(word, dict) or set(word) != {'layout', 'cover'}:
        raise ValueError('word requires separate layout and cover choices')
    for area, choices in [('layout', ['unselected', 'builtin', 'file']), ('cover', ['unselected', 'builtin', 'uploaded', 'from_sample'])]:
        choice = word[area]
        if not isinstance(choice, dict) or choice.get('source') not in choices:
            raise ValueError(f'Invalid word.{area} choice')
        source = choice['source']
        expected = {'source'} if source == 'unselected' else ({'source', 'preset_id'} if source == 'builtin' else {'source', 'resource'})
        if set(choice) != expected:
            raise ValueError(f'Unexpected or missing word.{area} fields')
        if source == 'builtin':
            if not isinstance(choice['preset_id'], str) or not choice['preset_id']:
                raise ValueError('builtin choice requires preset_id')
        elif source != 'unselected':
            reference(choice['resource'], root)
    for key in ['style', 'rating_scales']:
        if key in data and not isinstance(data[key], dict):
            raise ValueError(f'{key} must be an object of explicit user preferences')
    if data.get('history_ref') is not None and not isinstance(data['history_ref'], str):
        raise ValueError('history_ref must be a locator string or null; it is not auto-loaded')
    return data


def load(root):
    path = destination(root, 'profile.json')
    return validate(json.loads(path.read_text(encoding='utf-8')), root)


def write_new(path, data):
    # No overwrite, no metadata copy; a profile is user data, never product output.
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def setup(root, instruction_language='en', output_language=None, log_language=None):
    path = destination(root, 'profile.json')
    if path.exists():
        data = load(root)
        return {'created': False, 'profile_id': data['profile_id'], 'profile': str(path), 'unchanged': True}
    data = {'schema_version': SCHEMA, 'profile_id': 'profile-' + uuid.uuid4().hex,
            'instruction_language': instruction_language, 'output_language': output_language,
            'log_language': log_language, 'workspace': None,
            'word': {'layout': {'source': 'unselected'}, 'cover': {'source': 'unselected'}},
            'style': {}, 'rating_scales': {}, 'history_ref': None}
    validate(data, root)
    root.mkdir(parents=True, exist_ok=True)
    write_new(path, data)
    return {'created': True, 'profile_id': data['profile_id'], 'profile': str(path)}


def selected_files(data, root):
    files = {'profile.json': destination(root, 'profile.json')}
    for choice in data['word'].values():
        if choice.get('resource'):
            resource = choice['resource']
            path = reference(resource, root)
            if resource['path'] == 'manifest.json':
                raise ValueError('manifest.json is reserved for transfer metadata')
            files[resource['path']] = path
    return files


def export_profile(root, target):
    data = load(root)
    target = new_root(target)
    if target.exists():
        raise ValueError('Export destination must not already exist')
    if target.is_relative_to(root) or root.is_relative_to(target):
        raise ValueError('Export and profile roots must be disjoint')
    files = selected_files(data, root)
    # Local workspace paths are machine-specific; do not silently reuse them on import.
    exported = deepcopy(data)
    workspace = exported.get('workspace')
    if workspace and workspace['kind'] == 'local':
        exported['workspace'] = None
    exported['history_ref'] = None
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.profile-export-', dir=target.parent) as temporary:
        staging = Path(temporary) / 'profile'
        staging.mkdir()
        write_new(staging / 'profile.json', exported)
        for relative, source in files.items():
            if relative == 'profile.json':
                continue
            out = destination(staging, relative)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(source.read_bytes())
        manifest = {'schema_version': 1, 'profile_id': data['profile_id'],
                    'files_sha256': {name: digest(staging / name) for name in files},
                    'excluded': ['history bytes', 'unselected resources', 'local workspace locator']}
        write_new(staging / 'manifest.json', manifest)
        staging.rename(target)
    return {'export': str(target), 'files': len(files), 'private': True, 'cloud_synced': False}


def import_profile(source, target):
    source = private_root(source)
    target = new_root(target)
    if target.exists():
        raise ValueError('Import destination exists; profile identity conflict requires a separate decision')
    if target.is_relative_to(source) or source.is_relative_to(target):
        raise ValueError('Import and export roots must be disjoint')
    data = load(source)
    manifest = json.loads(destination(source, 'manifest.json').read_text(encoding='utf-8'))
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1 or manifest.get('profile_id') != data['profile_id']:
        raise ValueError('Invalid transfer manifest')
    files = selected_files(data, source)
    if manifest.get('files_sha256') != {name: digest(path) for name, path in files.items()}:
        raise ValueError('Transfer hashes or allowed file set do not match')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.profile-import-', dir=target.parent) as temporary:
        staging = Path(temporary) / 'profile'
        staging.mkdir()
        for relative, path in files.items():
            out = destination(staging, relative)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(path.read_bytes())
        validate(data, staging)
        staging.rename(target)
    return {'import': str(target), 'profile_id': data['profile_id'], 'provider_access_checked': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('init'); a.add_argument('root', type=Path)
    a.add_argument('--instruction-language', choices=['en', 'ru'], default='en')
    a.add_argument('--output-language'); a.add_argument('--log-language')
    a = sub.add_parser('validate'); a.add_argument('root', type=Path)
    a = sub.add_parser('export'); a.add_argument('root', type=Path); a.add_argument('target', type=Path)
    a = sub.add_parser('import'); a.add_argument('source', type=Path); a.add_argument('root', type=Path)
    args = p.parse_args()
    try:
        root = new_root(args.root) if args.command == 'import' else private_root(args.root)
        if args.command == 'init':
            result = setup(root, args.instruction_language, args.output_language, args.log_language)
        elif args.command == 'validate':
            result = {'valid': True, 'profile_id': load(root)['profile_id'], 'schema_version': SCHEMA}
        elif args.command == 'export':
            result = export_profile(root, args.target)
        else:
            result = import_profile(args.source, root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
