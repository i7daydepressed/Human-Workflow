#!/usr/bin/env python3
"""Build a portable preview plugin and optional isolated repo marketplace; never install."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from build_source import ROOT, FORBIDDEN, allowed_files
from sync_skill_resources import require_current


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def safe_name(name):
    if not isinstance(name, str) or not name:
        raise ValueError('Package paths must be nonempty strings')
    rel = PurePosixPath(name)
    if (not rel.parts or rel.is_absolute() or rel.as_posix() != name or '..' in rel.parts
            or '\\' in name or any(p in FORBIDDEN or p.startswith('._') for p in rel.parts)):
        raise ValueError('Invalid package path')
    return name


def payload(root):
    require_current(root)
    source = allowed_files(root)
    mapping = json.loads(source['packaging/plugin-files.json'])
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError('Plugin file mapping must be a nonempty object')
    files = {}
    provenance = {}
    for target, origin in sorted(mapping.items()):
        safe_name(target)
        if not isinstance(origin, str) or origin not in source:
            raise ValueError('Plugin source must be explicitly source-allowlisted')
        if target == 'PACKAGE-MANIFEST.json':
            raise ValueError('Package manifest path is reserved')
        files[target] = source[origin]
        provenance[target] = {'source': origin, 'sha256': hashlib.sha256(source[origin]).hexdigest()}
    manifest = json.loads(files['plugin.json'])
    identity = manifest['name']
    if identity != 'workflow-tools-preview' or manifest['version'] != '0.0.0-i06':
        raise ValueError('I06 builder supports only the recorded preview identity')
    if manifest.get('$schema') != 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json':
        raise ValueError('Expected the portable Agent Plugins manifest')
    if set(manifest) != {'$schema', 'name', 'version', 'description', 'extensions', 'license'}:
        raise ValueError('Unexpected identity or service metadata in the preview manifest')
    if manifest['license'] != 'PolyForm-Noncommercial-1.0.0 OR LicenseRef-Workflow-Tools-Commercial':
        raise ValueError('Expected the owner-selected licensing alternatives')
    entries = sorted(n for n in files if n.startswith('skills/') and n.endswith('/SKILL.md'))
    if entries != ['skills/human-step/SKILL.md', 'skills/md-word/SKILL.md']:
        raise ValueError('Expected exactly two workflow entrypoints')
    files['PACKAGE-MANIFEST.json'] = encoded({
        'kind': 'portable_plugin_preview', 'stage': 'I06',
        'identity_status': 'Human Workflow display name; retained technical ID; preview version',
        'host_installation_verified': False, 'published': False,
        'files': provenance})
    return files, identity


def zip_bytes(files):
    stream = io.BytesIO()
    with ZipFile(stream, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=ZIP_DEFLATED, compresslevel=9)
    data = stream.getvalue()
    with ZipFile(io.BytesIO(data)) as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(files):
            raise ValueError('Archive integrity or file set mismatch')
        if any(archive.read(name) != content for name, content in files.items()):
            raise ValueError('Archive byte mismatch')
    return data


def output_path(value, root):
    raw = value.expanduser().absolute()
    if any(p.is_symlink() for p in [raw, *raw.parents]):
        raise ValueError('Archive destination must not traverse a symlink')
    path = raw.resolve()
    if path.is_relative_to(root):
        raise ValueError('Write preview artifacts outside the source tree')
    if path.exists():
        raise ValueError('Preview output already exists; choose a new path')
    return path


def save_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.plugin-', suffix='.zip', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        # Publish a complete file without replacing an existing destination.
        os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {'archive': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def build(root, output, marketplace_output=None):
    root = root.expanduser().resolve()
    outputs = [output_path(output, root)]
    if marketplace_output is not None:
        outputs.append(output_path(marketplace_output, root))
    if len(set(outputs)) != len(outputs):
        raise ValueError('Plugin and marketplace outputs must be different paths')
    files, identity = payload(root)
    artifacts = [(outputs[0], zip_bytes(files), 'portable_plugin_preview', len(files))]
    if marketplace_output is not None:
        source = allowed_files(root)
        catalog = json.loads(source['packaging/marketplace.json'])
        entry = catalog['plugins']
        if (len(entry) != 1 or entry[0]['name'] != identity
                or entry[0]['source'] != {'source': 'local', 'path': './plugins/' + identity}):
            raise ValueError('Marketplace must point to the isolated preview package')
        repo = {'plugins/' + identity + '/' + name: content for name, content in files.items()}
        repo['.agents/plugins/marketplace.json'] = source['packaging/marketplace.json']
        repo['README.md'] = source['packaging/marketplace-readme.ru.md']
        repo['README.en.md'] = source['packaging/marketplace-readme.en.md']
        repo['README.ru.md'] = source['packaging/marketplace-readme.ru.md']
        artifacts.append((outputs[1], zip_bytes(repo), 'isolated_repo_marketplace_preview', len(repo)))
    results = []
    for path, data, kind, count in artifacts:
        result = save_new(path, data)
        result.update({'kind': kind, 'files': count})
        results.append(result)
    return {'artifacts': results, 'installed': False, 'published': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--marketplace-out', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.root, args.out, args.marketplace_out), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
