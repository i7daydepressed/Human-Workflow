#!/usr/bin/env python3
"""Generate skill-local resources from canonical allowlisted sources."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ('human-step', 'md-word')
REGISTRY = 'packaging/skill-resources.json'


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def safe_path(root, name):
    rel = PurePosixPath(name)
    if (not rel.parts or rel.is_absolute() or '..' in rel.parts
            or rel.as_posix() != name or '\\' in name):
        raise ValueError('Invalid resource path')
    path = root.joinpath(*rel.parts)
    if any(p.is_symlink() for p in [path, *path.parents] if p.is_relative_to(root)):
        raise ValueError('Resource path traverses a symlink: ' + name)
    if not path.resolve().is_relative_to(root):
        raise ValueError('Resource path escapes the source tree')
    return path


def generated_name(name):
    return any(name.startswith('skills/' + skill + '/resources/') for skill in SKILLS)


def make_plan(root):
    allow_path = safe_path(root, 'packaging/source-allowlist.json')
    names = json.loads(allow_path.read_text(encoding='utf-8'))
    if not isinstance(names, list) or not all(isinstance(n, str) for n in names) or len(names) != len(set(names)):
        raise ValueError('Expected a unique source allowlist')
    canonical = sorted(n for n in names if not generated_name(n) and n != REGISTRY)
    files = {}
    mapping = {}
    for skill in SKILLS:
        prefix = 'skills/' + skill + '/resources/'
        provenance = {}
        for name in canonical:
            own_locale = any(name.startswith('locales/' + language + '/' + skill + '/')
                             for language in ('en', 'ru'))
            shared = name.startswith('shared/') and (skill == 'md-word' or not name.startswith('shared/examples/'))
            if not (own_locale or shared or name.startswith('docs/')
                    or name in ('LICENSE', 'COMMERCIAL-LICENSE.md', 'COMMERCIAL-LICENSE.ru.md')):
                continue
            source = safe_path(root, name)
            if not source.is_file():
                raise ValueError('Canonical resource missing: ' + name)
            data = source.read_bytes()
            target = prefix + name
            files[target] = data
            info = {'source': name, 'sha256': hashlib.sha256(data).hexdigest()}
            mapping[target] = info
            provenance[name] = info
        files[prefix + 'resource-manifest.json'] = encoded({
            'schema_version': 1, 'kind': 'workflow_skill_resources',
            'skill': skill, 'generated': True, 'files': provenance})
    files[REGISTRY] = encoded({
        'schema_version': 1,
        'canonical_roots': ['locales/', 'shared/', 'docs/'],
        'policy': 'Edit canonical sources; regenerate skill-local copies. No private profiles or task files.',
        'files': mapping})
    expected_allowlist = sorted(set(canonical) | set(files))
    files['packaging/source-allowlist.json'] = encoded(expected_allowlist)
    package_path = safe_path(root, 'packaging/plugin-files.json')
    package = json.loads(package_path.read_text(encoding='utf-8'))
    package = {target: origin for target, origin in package.items()
               if not generated_name(target) and not generated_name(origin)}
    for name in files:
        if generated_name(name):
            package[name] = name
    files['packaging/plugin-files.json'] = encoded(dict(sorted(package.items())))
    # Validate every destination before writing any part of the generated tree.
    for name in files:
        safe_path(root, name)
    return files


def inspect(root):
    expected = make_plan(root)
    stale = [name for name, data in expected.items()
             if not safe_path(root, name).is_file() or safe_path(root, name).read_bytes() != data]
    extras = []
    for skill in SKILLS:
        folder = safe_path(root, 'skills/' + skill + '/resources')
        if folder.is_dir():
            for path in folder.rglob('*'):
                relative = path.relative_to(root).as_posix()
                if path.is_symlink():
                    raise ValueError('Generated resource must not be a symlink: ' + relative)
                if path.is_file() and '__pycache__' not in path.parts and relative not in expected:
                    extras.append(relative)
    return expected, sorted(stale), sorted(extras)


def require_current(root):
    _, stale, extras = inspect(root)
    if stale or extras:
        raise ValueError('Skill resources are stale or contain unmanaged files; run tools/sync_skill_resources.py')


def sync(root, check=False):
    expected, stale, extras = inspect(root)
    if check:
        return {'current': not stale and not extras, 'stale': stale, 'unmanaged': extras}
    if extras:
        raise ValueError('Unmanaged files in a generated resource directory; preserve and inspect them before syncing')
    for name, data in sorted(expected.items()):
        path = safe_path(root, name)
        if not path.is_file() or path.read_bytes() != data:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    return {'current': True, 'updated': len(stale),
            'resource_files': sum(generated_name(n) for n in expected), 'skills': list(SKILLS)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        result = sync(args.root.expanduser().resolve(), args.check)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['current'] else 1
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
