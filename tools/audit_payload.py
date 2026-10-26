#!/usr/bin/env python3
"""Scan source/ZIP text and DOCX XML using externally supplied private markers.

No OCR, media inspection, or anonymity guarantee. Keep detailed reports private.
"""
import argparse
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys
import unicodedata
import xml.etree.ElementTree as E
from zipfile import ZipFile, BadZipFile

GENERIC = [r'https?://(?:drive|docs)\.google\.com/', r'libfile_[A-Za-z0-9_-]+',
           r'/(?:workspace|root|Users)/', r'com\.google\.drivefs\.item-id']
BAD_PARTS = {'.DS_Store', '__MACOSX', 'private', 'originals', 'maintenance', 'arhive'}


def normalized(value):
    return unicodedata.normalize('NFKC', value).casefold()


def archive_entries(raw, prefix=''):
    with ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:
            raise ValueError('Archive CRC check failed')
        if len(set(z.namelist())) != len(z.namelist()):
            raise ValueError('Duplicate archive names')
        for info in z.infolist():
            if info.is_dir():
                continue
            path = PurePosixPath(info.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in info.filename or (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Unsafe archive member')
            yield prefix + info.filename, z.read(info)


def scan(target, config):
    literals = config.get('literals', [])
    patterns = GENERIC + config.get('patterns', [])
    if not isinstance(literals, list) or not all(isinstance(v, str) and v for v in literals):
        raise ValueError('Private literals must be nonempty strings')
    regexes = [re.compile(p, re.IGNORECASE) for p in patterns]
    results = []
    if target.is_dir():
        entries = []
        for path in sorted(target.rglob('*')):
            name = path.relative_to(target).as_posix()
            if any(v in {'.git', '__pycache__'} for v in path.relative_to(target).parts):
                continue
            if path.is_symlink():
                results.append({'file': name, 'kind': 'symlink'})
            elif path.is_file():
                entries.append((name, path.read_bytes()))
    else:
        entries = list(archive_entries(target.read_bytes()))
    def inspect(name, raw):
        if any(part in BAD_PARTS or part.startswith('._') for part in PurePosixPath(name).parts):
            results.append({'file': name, 'kind': 'forbidden-path'})
        if name.lower().endswith('.docx'):
            for child, data in archive_entries(raw, prefix=name + '!/'):
                inspect(child, data)
            return
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            return
        if name.endswith(('.xml', '.rels')):
            root = E.fromstring(text)
            joined = ''.join(node.text or '' for node in root.iter() if node.tag.rsplit('}', 1)[-1] in {'t', 'instrText', 'delText'})
            text += '\n' + ''.join(root.itertext()) + '\n' + joined + '\n' + '\n'.join(value for node in root.iter() for value in node.attrib.values())
        value = normalized(text)
        for index, literal in enumerate(literals):
            if normalized(literal) in value:
                results.append({'file': name, 'kind': 'private-literal', 'marker_index': index})
        for index, regex in enumerate(regexes):
            if regex.search(text):
                results.append({'file': name, 'kind': 'pattern', 'pattern_index': index})
    for name, raw in entries:
        inspect(name, raw)
    return {'files': len(entries), 'findings': results, 'checks_media': False, 'checks_host_installation': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('target', type=Path)
    p.add_argument('--markers', type=Path, required=True, help='Private JSON config outside the product')
    p.add_argument('--report', type=Path, help='Optional private detailed report; marker text is not printed')
    args = p.parse_args()
    try:
        target = args.target.resolve()
        if target.is_dir() and args.markers.resolve().is_relative_to(target):
            raise ValueError('Private markers must stay outside the audited tree')
        result = scan(target, json.loads(args.markers.read_text(encoding='utf-8')))
        if args.report:
            if args.report.is_symlink() or (target.is_dir() and args.report.resolve().is_relative_to(target)):
                raise ValueError('Detailed report must stay outside the audited tree and not be a symlink')
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'files': result['files'], 'findings': len(result['findings']), 'checks_media': False}))
        return 1 if result['findings'] else 0
    except (ValueError, OSError, TypeError, E.ParseError, BadZipFile, re.error) as exc:
        print(json.dumps({'error': str(exc)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
