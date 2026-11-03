#!/usr/bin/env python3
"""Audit DOCX package relationships, content types, and referenced resources.

This is a structural check. It does not inspect pixels or verify layout.
"""
import argparse
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import sys
from urllib.parse import unquote
import xml.etree.ElementTree as E
from zipfile import BadZipFile, ZipFile

REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def read_package(path):
    with ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or archive.testzip() is not None:
            raise ValueError('Duplicate members or CRC error')
        parts = {}
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = info.filename
            relative = PurePosixPath(name)
            if relative.is_absolute() or '..' in relative.parts or '\\' in name or relative.as_posix() != name:
                raise ValueError('Invalid package path')
            if ((info.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError('Package symlinks are unsupported')
            parts[name] = archive.read(info)
    return parts


def rels_name(owner):
    if not owner:
        return '_rels/.rels'
    directory, name = posixpath.split(owner)
    return posixpath.join(directory, '_rels', name + '.rels')


def rels_owner(name):
    if name == '_rels/.rels':
        return ''
    directory, basename = posixpath.split(name)
    if posixpath.basename(directory) != '_rels' or not basename.endswith('.rels'):
        raise ValueError('Invalid relationships part name')
    return posixpath.join(posixpath.dirname(directory), basename[:-5])


def target_part(owner, target):
    target = unquote(target.split('#', 1)[0])
    value = posixpath.normpath(target.lstrip('/') if target.startswith('/') else posixpath.join(posixpath.dirname(owner), target))
    if value in ['', '.', '..'] or value.startswith('../') or '\\' in value:
        raise ValueError('Relationship target escapes the package')
    return value


def edges(parts, owner):
    name = rels_name(owner)
    if name not in parts:
        return []
    result = []
    seen = set()
    for node in E.fromstring(parts[name]):
        if node.tag != '{' + REL + '}Relationship':
            raise ValueError('Unexpected relationship element')
        rid = node.get('Id')
        if not rid or rid in seen or not node.get('Type') or not node.get('Target'):
            raise ValueError('Incomplete or duplicate relationship')
        seen.add(rid)
        external = node.get('TargetMode') == 'External'
        result.append({'id': rid, 'type': node.get('Type'), 'target': node.get('Target'),
                       'external': external, 'part': None if external else target_part(owner, node.get('Target'))})
    return result


def reachable(parts):
    keep = {'[Content_Types].xml'}
    pending = ['']
    visited = set()
    while pending:
        owner = pending.pop()
        if owner in visited:
            continue
        visited.add(owner)
        if owner:
            keep.add(owner)
        name = rels_name(owner)
        if name in parts:
            keep.add(name)
        for edge in edges(parts, owner):
            if not edge['external']:
                if edge['part'] not in parts:
                    raise ValueError('Missing relationship target: ' + edge['part'])
                pending.append(edge['part'])
    return keep


def audit(parts, public_preset=False):
    errors = []
    required = ['[Content_Types].xml', '_rels/.rels', 'word/document.xml']
    for name in required:
        if name not in parts:
            errors.append('Missing required part: ' + name)
    if errors:
        return {'pass': False, 'errors': errors, 'parts': len(parts)}
    types = E.fromstring(parts['[Content_Types].xml'])
    overrides = {n.get('PartName', '').lstrip('/'): n.get('ContentType') for n in types if n.tag == '{' + CT + '}Override'}
    defaults = {n.get('Extension'): n.get('ContentType') for n in types if n.tag == '{' + CT + '}Default'}
    for name in overrides:
        if name not in parts:
            errors.append('Dangling content type: ' + name)
    external = []
    for name, raw in parts.items():
        if name != '[Content_Types].xml' and name not in overrides and name.rsplit('.', 1)[-1] not in defaults:
            errors.append('Missing content type: ' + name)
        if name.endswith('.rels'):
            owner = rels_owner(name)
            if owner and owner not in parts:
                errors.append('Relationships owner missing: ' + name)
            for edge in edges(parts, owner):
                if edge['external']:
                    external.append({'owner': owner, 'id': edge['id'], 'type': edge['type']})
                elif edge['part'] not in parts:
                    errors.append('Dangling relationship: ' + name + '#' + edge['id'])
        elif name.endswith('.xml'):
            xml = E.fromstring(raw)
            ids = {e['id'] for e in edges(parts, name)}
            for node in xml.iter():
                for key, value in node.attrib.items():
                    if key.startswith('{' + R + '}') and value not in ids:
                        errors.append('Unknown relationship reference: ' + name + '#' + value)
    try:
        used = reachable(parts)
    except ValueError as exc:
        errors.append(str(exc)); used = set(parts)
    orphaned = sorted(set(parts) - used)
    if public_preset:
        if orphaned:
            errors.append('Public base preset has orphaned parts')
        for name in parts:
            if name.startswith(('customXml/', 'word/embeddings/')) or re.search(r'(?:comments|people|core0|custom\.xml|thumbnail)', name, re.I):
                errors.append('Unexpected provenance/embedded part: ' + name)
        if external:
            errors.append('Public base preset has external relationships')
        for name in [n for n in parts if n.endswith('.xml')]:
            xml = E.fromstring(parts[name])
            if any(node.tag in {'{' + W + '}' + tag for tag in ['ins', 'del', 'moveFrom', 'moveTo', 'altChunk']} for node in xml.iter()):
                errors.append('Tracked/embedded content in public preset: ' + name)
    return {'pass': not errors, 'errors': errors, 'parts': len(parts), 'orphaned_parts': orphaned,
            'external_relationships': external, 'media': sorted(n for n in parts if n.startswith('word/media/')),
            'checks_layout': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('docx', type=Path)
    p.add_argument('--public-preset', action='store_true')
    args = p.parse_args()
    try:
        result = audit(read_package(args.docx), args.public_preset)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['pass'] else 1
    except (ValueError, OSError, E.ParseError, BadZipFile) as exc:
        print(json.dumps({'error': str(exc)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
