#!/usr/bin/env python3
"""Compare chosen preservation invariants of two DOCX files; no rendering."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, BadZipFile
import xml.etree.ElementTree as E
import sys
import re

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
W = '{' + NS['w'] + '}'


def field_codes(document):
    fields, stack, orphan = [], [], []
    for node in document.iter():
        if node.tag == W + 'p' and orphan:
            fields.append(''.join(orphan)); orphan = []
        elif node.tag == W + 'fldSimple':
            fields.append(node.get(W + 'instr', ''))
        elif node.tag == W + 'fldChar':
            kind = node.get(W + 'fldCharType')
            if kind == 'begin':
                stack.append([])
            elif kind == 'end' and stack:
                fields.append(''.join(stack.pop()))
        elif node.tag == W + 'instrText':
            (stack[-1] if stack else orphan).append(node.text or '')
    if orphan:
        fields.append(''.join(orphan))
    return fields


def read(path):
    with ZipFile(path) as z:
        doc = E.fromstring(z.read('word/document.xml'))
        body = doc.find('w:body', NS)
        media = {name: hashlib.sha256(z.read(name)).hexdigest()
                 for name in z.namelist() if name.startswith('word/media/')}
        table_content = []
        for table in doc.findall('.//w:tbl', NS):
            rows = []
            for row in table.findall('w:tr', NS):
                rows.append([''.join(t.text or '' for t in cell.findall('.//w:t', NS)) for cell in row.findall('w:tc', NS)])
            table_content.append(rows)
        geometry = [dict(node.attrib) for node in doc.findall('.//wp:extent', NS)]
        fields = field_codes(doc)
        return {'blocks': list(body), 'tables': table_content, 'media': media,
                'geometry': geometry,
                'toc_field_present': any(re.match(r'^\s*TOC(?:\s|$)', field, re.IGNORECASE) for field in fields)}


def block_bytes(block):
    return E.canonicalize(E.tostring(block, encoding='unicode'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('baseline', type=Path); p.add_argument('result', type=Path)
    p.add_argument('--cover-before', type=int)
    p.add_argument('--tables', action='store_true'); p.add_argument('--media', action='store_true')
    p.add_argument('--geometry', action='store_true')
    p.add_argument('--require-toc', action='store_true', help='Fail if the result has no TOC field; does not check cached pages')
    args = p.parse_args()
    if args.cover_before is None and not any([args.tables, args.media, args.geometry, args.require_toc]):
        p.error('Выбрать хотя бы один инвариант')
    try:
        old, new = read(args.baseline), read(args.result)
        checks = {}
        if args.cover_before is not None:
            n = args.cover_before
            if n <= 0 or n > len(old['blocks']) or n > len(new['blocks']):
                raise ValueError('cover-before должен задавать непустой префикс существующих body-блоков')
            checks['cover_blocks_equal'] = all(block_bytes(a) == block_bytes(b) for a, b in zip(old['blocks'][:n], new['blocks'][:n]))
        for enabled, key in [(args.tables, 'tables'), (args.media, 'media'), (args.geometry, 'geometry')]:
            if enabled:
                checks[key + '_equal'] = old[key] == new[key]
        if args.require_toc:
            checks['toc_required_present'] = new['toc_field_present']
        result = {'checks': checks, 'pass': all(checks.values()),
                  'toc_field_present': new['toc_field_present'],
                  'note': 'Проверены только выбранные инварианты; визуальная верстка и страницы TOC не проверялись'}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['pass'] else 1
    except (ValueError, OSError, E.ParseError, BadZipFile, KeyError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False)); return 2


if __name__ == '__main__':
    sys.exit(main())
