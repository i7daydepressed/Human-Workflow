#!/usr/bin/env python3
"""Inspect DOCX blocks without modifying the sample. Standard library only."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E
from safe_paths import destination

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W = '{' + NS['w'] + '}'


def xml_properties(node):
    if node is None:
        return None
    return {'tag': node.tag.rsplit('}', 1)[-1],
            'attributes': {k.rsplit('}', 1)[-1]: v for k, v in node.attrib.items()},
            'children': [xml_properties(c) for c in node]}


def text(node):
    return ''.join(n.text or '' for n in node.iter(W + 't'))


def val(node, path):
    child = node.find(path, NS)
    return child.get(W + 'val') if child is not None else None


def inspect(path):
    with ZipFile(path) as z:
        document = E.fromstring(z.read('word/document.xml'))
        styles = E.fromstring(z.read('word/styles.xml'))
        numbering = E.fromstring(z.read('word/numbering.xml')) if 'word/numbering.xml' in z.namelist() else None
        body = document.find('w:body', NS)
        blocks = []
        for index, block in enumerate(body):
            record = {'body_index': index, 'kind': block.tag.rsplit('}', 1)[-1]}
            if block.tag == W + 'p':
                record.update(text=text(block), style=val(block, 'w:pPr/w:pStyle'),
                              outline=val(block, 'w:pPr/w:outlineLvl'),
                              num_id=val(block, 'w:pPr/w:numPr/w:numId'),
                              num_level=val(block, 'w:pPr/w:numPr/w:ilvl'),
                              pPr=xml_properties(block.find('w:pPr', NS)),
                              run_formats=[xml_properties(r.find('w:rPr', NS)) for r in block.findall('w:r', NS)],
                              images=len(block.findall('.//w:drawing', NS)),
                              formulas=len(block.findall('.//m:oMath', NS)))
            elif block.tag == W + 'tbl':
                record.update(rows=len(block.findall('w:tr', NS)),
                              text_preview=text(block)[:800],
                              tblPr=xml_properties(block.find('w:tblPr', NS)),
                              grid=xml_properties(block.find('w:tblGrid', NS)))
            else:
                record['text_preview'] = text(block)[:800]
            record['fields'] = [''.join(n.itertext()) for n in block.findall('.//w:instrText', NS)]
            record['simple_fields'] = [n.get(W + 'instr') for n in block.findall('.//w:fldSimple', NS)]
            blocks.append(record)
        style_map = {}
        for style in styles.findall('w:style', NS):
            style_map[style.get(W + 'styleId')] = {
                'type': style.get(W + 'type'), 'name': val(style, 'w:name'),
                'based_on': val(style, 'w:basedOn'), 'outline': val(style, 'w:pPr/w:outlineLvl'),
                'pPr': xml_properties(style.find('w:pPr', NS)),
                'rPr': xml_properties(style.find('w:rPr', NS)),
            }
        return {'source': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'blocks': blocks, 'styles': style_map,
                'numbering': xml_properties(numbering),
                'sections': [xml_properties(n) for n in document.findall('.//w:sectPr', NS)],
                'note': 'Индексы относятся только к этой копии. Выбирать образцы после визуального просмотра; стили могут наследоваться через based_on.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('docx', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = inspect(args.docx.resolve())
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        output = destination(args.out.expanduser().parent.resolve(), args.out.name)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding='utf-8')
        print(json.dumps({'inventory': str(args.out.resolve()), 'blocks': len(result['blocks']),
                          'styles': len(result['styles']), 'sha256': result['sha256']}, ensure_ascii=False))
    else:
        print(payload)


if __name__ == '__main__':
    main()
