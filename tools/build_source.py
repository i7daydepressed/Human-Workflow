#!/usr/bin/env python3
"""Build a deterministic source checkpoint from an explicit file allowlist."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {'.git', '.DS_Store', '__MACOSX', '__pycache__', 'private', 'originals', 'maintenance', 'arhive'}


def allowed_files(root):
    allowlist = root / 'packaging/source-allowlist.json'
    if allowlist.is_symlink():
        raise ValueError('Allowlist must not be a symlink')
    names = json.loads(allowlist.read_text(encoding='utf-8'))
    if not isinstance(names, list) or not all(isinstance(n, str) for n in names) or len(set(names)) != len(names):
        raise ValueError('Allowlist must contain unique file paths')
    files = {}
    for name in sorted(names):
        rel = PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or '\\' in name or rel.as_posix() != name or any(p in FORBIDDEN or p.startswith('._') for p in rel.parts):
            raise ValueError('Invalid or forbidden source path')
        path = root.joinpath(*rel.parts)
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError(f'Allowed file missing or outside source: {name}')
        if any(p.is_symlink() for p in [path, *path.parents] if p != root and p.is_relative_to(root)):
            raise ValueError(f'Allowed file traverses a symlink: {name}')
        files[name] = path.read_bytes()
    return files


def build(root, output):
    root = root.expanduser().resolve()
    raw = output.expanduser().absolute()
    if any(p.is_symlink() for p in [raw, *raw.parents]):
        raise ValueError('Archive destination must not traverse a symlink')
    output = raw.resolve()
    if output.is_relative_to(root):
        raise ValueError('Write source archives outside the source directory')
    files = allowed_files(root)
    stage = json.loads(files['packaging/release-status.json'])['stage']
    manifest = {'kind': 'source_checkpoint', 'stage': stage, 'installable_plugin': False,
                'files_sha256': {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}}
    files['SOURCE-MANIFEST.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.source-', suffix='.zip', dir=output.parent)
    os.close(fd)
    try:
        with ZipFile(temporary, 'w', compression=ZIP_DEFLATED, compresslevel=9) as z:
            for name, data in sorted(files.items()):
                info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = ZIP_DEFLATED
                z.writestr(info, data, compress_type=ZIP_DEFLATED, compresslevel=9)
        with ZipFile(temporary) as z:
            if z.testzip() is not None or set(z.namelist()) != set(files):
                raise ValueError('Archive integrity or file set mismatch')
            if any(z.read(name) != data for name, data in files.items()):
                raise ValueError('Archive byte mismatch')
        os.replace(temporary, output)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {'archive': str(output), 'files': len(files), 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'kind': 'source_checkpoint', 'installable_plugin': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.root, args.out), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
