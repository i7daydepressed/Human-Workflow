#!/usr/bin/env python3
"""Apply an explicitly selected DOCX cover while preserving the layout body.

Word mode only: requires lxml. Supports paragraph/table/picture covers with a
single cover section. It is not a general document compositor or renderer.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import posixpath
import re
import sys
from zipfile import BadZipFile, ZipFile, ZipInfo, ZIP_DEFLATED

from lxml import etree as E

from docx_package import read_package, audit, edges, rels_name, R, REL, CT, W
from safe_paths import destination

WN = '{' + W + '}'
RN = '{' + R + '}'
SHARED = Path(__file__).resolve().parents[1]
NS = {'w': W, 'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}

# Property children have defined sequences. Keep inserted properties in the
# corresponding order rather than relying on a tolerant renderer to repair it.
PROPERTY_ORDER = {
    'pPr': 'pStyle keepNext keepLines pageBreakBefore framePr widowControl numPr suppressLineNumbers pBdr shd tabs suppressAutoHyphens kinsoku wordWrap overflowPunct topLinePunct autoSpaceDE autoSpaceDN bidi adjustRightInd snapToGrid spacing ind contextualSpacing mirrorIndents suppressOverlap jc textDirection textAlignment textboxTightWrap outlineLvl divId cnfStyle rPr sectPr pPrChange',
    'rPr': 'rStyle rFonts b bCs i iCs caps smallCaps strike dstrike outline shadow emboss imprint noProof snapToGrid vanish webHidden color spacing w kern position sz szCs highlight u effect bdr shd fitText vertAlign rtl cs em lang eastAsianLayout specVanish oMath rPrChange',
    'sectPr': 'headerReference footerReference footnotePr endnotePr type pgSz pgMar paperSrc pgBorders lnNumType pgNumType cols formProt vAlign noEndnote titlePg textDirection bidi rtlGutter docGrid printerSettings sectPrChange',
    'lvl': 'start numFmt lvlRestart pStyle isLgl suff lvlText lvlPicBulletId legacy lvlJc pPr rPr',
}


def order_properties(tree):
    for node in tree.iter():
        order = PROPERTY_ORDER.get(E.QName(node).localname) if node.tag.startswith(WN) else None
        if order:
            sequence = {WN + tag: index for index, tag in enumerate(order.split())}
            node[:] = sorted(node, key=lambda item: sequence.get(item.tag, len(sequence)))


def xml(raw):
    return E.fromstring(raw, parser=E.XMLParser(resolve_entities=False, no_network=True))


def raw(node):
    return E.tostring(node, encoding='UTF-8', xml_declaration=True, standalone=True)


def child(parent, tag):
    value = parent.find(WN + tag)
    if value is None:
        value = E.Element(WN + tag)
        if tag == 'pPr' and parent.tag == WN + 'p':
            parent.insert(0, value)
        else:
            parent.append(value)
    return value


def first_section(body):
    for index, block in enumerate(body):
        found = block.find('w:pPr/w:sectPr', NS) if block.tag == WN + 'p' else None
        if found is not None:
            return index, found
    return None, None


def covered_blocks(document, mode):
    body = document.find(WN + 'body')
    boundary, section = first_section(body)
    if boundary is not None:
        if mode == 'uploaded':
            raise ValueError('Uploaded cover has multiple sections; explicitly select from_sample for its first section')
        return deepcopy(list(body)[:boundary + 1])
    section = body.find(WN + 'sectPr')
    if section is None:
        raise ValueError('Cover section properties are missing')
    blocks = deepcopy([b for b in body if b.tag != WN + 'sectPr'])
    if not blocks:
        raise ValueError('Cover is empty')
    if blocks[-1].tag != WN + 'p':
        blocks.append(E.Element(WN + 'p'))
    child(blocks[-1], 'pPr').append(deepcopy(section))
    return blocks


def section_boundary_spacing(paragraph, styles):
    """Resolve only trailing spacing at the layout's cover/body boundary."""
    properties = paragraph.find(WN + 'pPr')
    selected = properties.find(WN + 'pStyle') if properties is not None else None
    lookup = {s.get(WN + 'styleId'): s for s in styles.findall(WN + 'style')}
    sid = selected.get(WN + 'val') if selected is not None else next(
        (s.get(WN + 'styleId') for s in lookup.values() if s.get(WN + 'type') == 'paragraph' and s.get(WN + 'default') == '1'), None)
    chain, seen = [], set()
    while sid:
        if sid in seen or sid not in lookup:
            raise ValueError('Invalid layout paragraph style inheritance')
        seen.add(sid); style = lookup[sid]; chain.insert(0, style.find(WN + 'pPr'))
        parent = style.find(WN + 'basedOn'); sid = parent.get(WN + 'val') if parent is not None else None
    areas = [styles.find('w:docDefaults/w:pPrDefault/w:pPr', NS), *chain, properties]
    values = {WN + 'after': '0'}
    for area in areas:
        spacing = area.find(WN + 'spacing') if area is not None else None
        if spacing is not None:
            values.update({k: v for k, v in spacing.attrib.items() if k in {WN + t for t in ['after', 'afterLines', 'afterAutospacing']}})
    return values


def validate_cover(blocks, parts):
    excluded = {'object', 'pict', 'txbxContent', 'altChunk', 'ins', 'del', 'moveFrom', 'moveTo',
                'commentRangeStart', 'commentRangeEnd', 'commentReference', 'footnoteReference', 'endnoteReference'}
    codes = []
    for block in blocks:
        for node in block.iter():
            if E.QName(node).localname in excluded:
                raise ValueError('Cover contains unsupported embedded, review, textbox, or note content')
            if node.tag == WN + 'instrText':
                codes.append(node.text or '')
            if node.tag == WN + 'fldSimple':
                codes.append(' ' + node.get(WN + 'instr', '') + ' ')
            if E.QName(node).localname == 'graphicData' and node.get('uri') != 'http://schemas.openxmlformats.org/drawingml/2006/picture':
                raise ValueError('Only simple embedded pictures are supported in a cover')
    if re.search(r'\b(?:TOC|PAGEREF|REF)\b', ''.join(codes), re.I):
        raise ValueError('Cross-reference fields in a cover require a document-specific merge')
    font_table = xml(parts['word/fontTable.xml']) if 'word/fontTable.xml' in parts else None
    if font_table is not None and any(E.QName(n).localname.startswith('embed') for n in font_table.iter()):
        raise ValueError('Embedded cover fonts require a document-specific merge')
    numbering = xml(parts['word/numbering.xml']) if 'word/numbering.xml' in parts else None
    if numbering is not None and numbering.find(WN + 'numPicBullet') is not None:
        raise ValueError('Picture bullets in a cover require a document-specific merge')


def apply(layout_path, cover_path, output, mode):
    layout = read_package(layout_path); cover = read_package(cover_path)
    for package in [layout, cover]:
        checked = audit(package)
        if not checked['pass']:
            raise ValueError('Invalid DOCX package: ' + '; '.join(checked['errors']))
    document = xml(layout['word/document.xml']); body = document.find(WN + 'body')
    boundary, previous_section = first_section(body)
    if boundary is None:
        raise ValueError('Layout needs an explicit cover section before its body')
    rest = deepcopy(list(body)[boundary + 1:])
    if not rest:
        raise ValueError('Layout body is empty')
    blocks = covered_blocks(xml(cover['word/document.xml']), mode)
    validate_cover(blocks, cover)
    # The final cover paragraph also carries the section break. Its trailing
    # spacing participates in the first body paragraph's spacing in Writer.
    # Retain the layout's boundary value, without changing visible cover text.
    boundary_spacing = section_boundary_spacing(body[boundary], xml(layout['word/styles.xml']))
    final_spacing = child(child(blocks[-1], 'pPr'), 'spacing')
    for key in ['after', 'afterLines', 'afterAutospacing']:
        final_spacing.attrib.pop(WN + key, None)
    final_spacing.attrib.update(boundary_spacing)
    # Materialize inherited layout header/footer relationships at its first body
    # section, so the new cover cannot replace the body's page-number footer.
    first_body_section = next((s for b in rest for s in b.iter(WN + 'sectPr')), None)
    if first_body_section is None:
        raise ValueError('Layout body section is missing')
    for kind in ['headerReference', 'footerReference']:
        present = {n.get(WN + 'type') for n in first_body_section.findall(WN + kind)}
        for reference in previous_section.findall(WN + kind):
            if reference.get(WN + 'type') not in present:
                first_body_section.insert(0, deepcopy(reference))
                present.add(reference.get(WN + 'type'))
        # An absent original reference means a blank header/footer, not an
        # invitation to inherit one from the newly imported cover.
        incoming = {n.get(WN + 'type') for b in blocks for s in b.iter(WN + 'sectPr')
                    for n in s.findall(WN + kind)}
        for reference_type in sorted(incoming - present):
            area = 'header' if kind == 'headerReference' else 'footer'
            part = 'word/cover-blank-' + area + '-' + reference_type + '.xml'
            while part in layout:
                part = part[:-4] + '_.xml'
            blank = E.Element(WN + ('hdr' if area == 'header' else 'ftr'), nsmap={'w': W})
            E.SubElement(blank, WN + 'p'); layout[part] = raw(blank)
            types = xml(layout['[Content_Types].xml'])
            types.append(E.Element('{' + CT + '}Override', PartName='/' + part,
                         ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.' + area + '+xml'))
            layout['[Content_Types].xml'] = raw(types)
            relationships = xml(layout['word/_rels/document.xml.rels'])
            rid = 'rIdCoverBlank' + area + reference_type
            while any(n.get('Id') == rid for n in relationships):
                rid += '_'
            relationships.append(E.Element('{' + REL + '}Relationship', Id=rid,
                                 Type=R + '/' + area, Target=part[5:]))
            layout['word/_rels/document.xml.rels'] = raw(relationships)
            first_body_section.insert(0, E.Element(WN + kind, {WN + 'type': reference_type, RN + 'id': rid}))

    styles = xml(layout['word/styles.xml']); own_styles = xml(cover['word/styles.xml'])
    default_style = next((s.get(WN + 'styleId') for s in own_styles.findall(WN + 'style')
                          if s.get(WN + 'type') == 'paragraph' and s.get(WN + 'default') == '1'), None)
    if default_style is None:
        raise ValueError('Cover has no default paragraph style')
    own_numbering = xml(cover['word/numbering.xml']) if 'word/numbering.xml' in cover else E.Element(WN + 'numbering')
    style_lookup = {s.get(WN + 'styleId'): s for s in own_styles.findall(WN + 'style')}
    number_lookup = {n.get(WN + 'numId'): n for n in own_numbering.findall(WN + 'num')}
    abstract_lookup = {n.get(WN + 'abstractNumId'): n for n in own_numbering.findall(WN + 'abstractNum')}
    required_styles, required_numbers, required_abstracts = {default_style}, set(), set()
    def collect(tree):
        for item in tree.iter():
            if item.tag in {WN + n for n in ['pStyle', 'rStyle', 'tblStyle', 'basedOn', 'next', 'link', 'styleLink', 'numStyleLink']}:
                required_styles.add(item.get(WN + 'val'))
            elif item.tag == WN + 'numId' and item.get(WN + 'val') != '0':
                required_numbers.add(item.get(WN + 'val'))
    for block in blocks:
        collect(block)
    for name in cover:
        if name.startswith(('word/header', 'word/footer')) and name.endswith('.xml'):
            collect(xml(cover[name]))
    previous = None
    while previous != (frozenset(required_styles), frozenset(required_numbers), frozenset(required_abstracts)):
        previous = (frozenset(required_styles), frozenset(required_numbers), frozenset(required_abstracts))
        for sid in list(required_styles):
            if sid not in style_lookup:
                raise ValueError('Cover style reference is missing')
            collect(style_lookup[sid])
        for num_id in list(required_numbers):
            if num_id not in number_lookup:
                raise ValueError('Cover numbering reference is missing')
            abstract = number_lookup[num_id].find(WN + 'abstractNumId').get(WN + 'val')
            if abstract not in abstract_lookup:
                raise ValueError('Cover abstract numbering is missing')
            required_abstracts.add(abstract); collect(abstract_lookup[abstract])
    used_styles = {s.get(WN + 'styleId') for s in styles.findall(WN + 'style')}
    style_map = {}
    for source in own_styles.findall(WN + 'style'):
        old = source.get(WN + 'styleId'); candidate = 'Cover_' + old
        if old not in required_styles:
            continue
        while candidate in used_styles:
            candidate += '_'
        used_styles.add(candidate); style_map[old] = candidate
    numbering = xml(layout['word/numbering.xml']) if 'word/numbering.xml' in layout else E.Element(WN + 'numbering', nsmap={'w': W})
    abstract_map, number_map = {}, {}
    for tag, key, mapping in [('abstractNum', 'abstractNumId', abstract_map), ('num', 'numId', number_map)]:
        next_id = max([int(n.get(WN + key)) for n in numbering.findall(WN + tag)] + [0]) + 1
        for source in own_numbering.findall(WN + tag):
            if source.get(WN + key) not in (required_abstracts if tag == 'abstractNum' else required_numbers):
                continue
            mapping[source.get(WN + key)] = str(next_id); next_id += 1

    theme = xml(cover['word/theme/theme1.xml']) if 'word/theme/theme1.xml' in cover else None
    def resolve_font(value):
        if theme is None:
            raise ValueError('Cover theme font has no theme part')
        family = 'majorFont' if value.lower().startswith('major') else 'minorFont'
        font = theme.find('.//a:fontScheme/a:' + family + '/a:latin', NS)
        if font is None or not font.get('typeface'):
            raise ValueError('Cover theme font cannot be resolved')
        return font.get('typeface')

    drawing_next = max([int(n.get('id')) for name, data in layout.items() if name.endswith('.xml')
                        for n in xml(data).iter() if E.QName(n).localname == 'docPr' and n.get('id', '').isdigit()] + [0]) + 1
    def remap(tree, paragraphs=False):
        nonlocal drawing_next
        for node in tree.iter():
            if node.tag in {WN + n for n in ['pStyle', 'rStyle', 'tblStyle', 'basedOn', 'next', 'link', 'styleLink', 'numStyleLink']}:
                old = node.get(WN + 'val')
                if old in style_map:
                    node.set(WN + 'val', style_map[old])
            elif node.tag == WN + 'numId' and node.get(WN + 'val') != '0':
                old = node.get(WN + 'val')
                if old not in number_map:
                    raise ValueError('Cover numbering reference is missing')
                node.set(WN + 'val', number_map[old])
            elif node.tag == WN + 'abstractNumId':
                node.set(WN + 'val', abstract_map[node.get(WN + 'val')])
            elif node.tag == WN + 'rFonts':
                for key in ['ascii', 'hAnsi', 'eastAsia', 'cs']:
                    attr = next((k for k in node.attrib if E.QName(k).localname.lower() == (key + 'Theme').lower()), None)
                    if attr is not None:
                        node.set(WN + key, resolve_font(node.attrib.pop(attr)))
            elif node.tag == WN + 'color' and node.get(WN + 'themeColor'):
                name = node.get(WN + 'themeColor')
                # Detach the stored explicit RGB from the layout's different
                # theme. A renderer must verify covers whose theme cache differs.
                value = node.get(WN + 'val', '')
                if not re.fullmatch('[0-9A-Fa-f]{6}', value):
                    if node.get(WN + 'themeTint') or node.get(WN + 'themeShade'):
                        raise ValueError('Tinted theme color without stored RGB requires a document-specific merge')
                    aliases = {'dark1': 'dk1', 'light1': 'lt1', 'dark2': 'dk2', 'light2': 'lt2', 'hyperlink': 'hlink', 'followedHyperlink': 'folHlink'}
                    color = theme.find('.//a:clrScheme/a:' + aliases.get(name, name), NS) if theme is not None else None
                    if color is None or not len(color):
                        raise ValueError('Cover theme color cannot be resolved')
                    value = color[0].get('val') if E.QName(color[0]).localname == 'srgbClr' else color[0].get('lastClr')
                    node.set(WN + 'val', value)
                for key in ['themeColor', 'themeTint', 'themeShade']:
                    node.attrib.pop(WN + key, None)
            elif E.QName(node).localname in ['docPr', 'cNvPr'] and node.get('id') is not None:
                node.set('id', str(drawing_next)); drawing_next += 1
        if paragraphs:
            for paragraph in tree.iter(WN + 'p'):
                props = child(paragraph, 'pPr')
                if props.find(WN + 'pStyle') is None:
                    style = E.Element(WN + 'pStyle', {WN + 'val': style_map[default_style]}); props.insert(0, style)

    for source in own_styles.findall(WN + 'style'):
        value = deepcopy(source); old_id = value.get(WN + 'styleId')
        if old_id not in required_styles:
            continue
        value.set(WN + 'styleId', style_map[old_id]); value.attrib.pop(WN + 'default', None)
        name = value.find(WN + 'name')
        if name is not None:
            name.set(WN + 'val', 'Cover ' + name.get(WN + 'val', old_id))
        if old_id == default_style:
            for area, lookup in [('rPr', 'rPrDefault/rPr'), ('pPr', 'pPrDefault/pPr')]:
                defaults = own_styles.find('w:docDefaults/' + '/'.join('w:' + p for p in lookup.split('/')), NS)
                if defaults is not None:
                    current = child(value, area)
                    for prop in defaults:
                        if current.find(prop.tag) is None:
                            current.append(deepcopy(prop))
        remap(value); order_properties(value); styles.append(value)
    for source in own_numbering:
        local = E.QName(source).localname
        if local not in ['abstractNum', 'num']:
            continue
        value = deepcopy(source)
        key = 'abstractNumId' if local == 'abstractNum' else 'numId'
        mapping = abstract_map if local == 'abstractNum' else number_map
        if source.get(WN + key) not in mapping:
            continue
        value.set(WN + key, mapping[source.get(WN + key)]); remap(value)
        order_properties(value); numbering.append(value)
    # Keep the OOXML abstract definitions before concrete numbering instances.
    numbering[:] = sorted(numbering, key=lambda n: 0 if n.tag == WN + 'abstractNum' else 1)
    layout['word/styles.xml'] = raw(styles); layout['word/numbering.xml'] = raw(numbering)

    content_types = xml(layout['[Content_Types].xml']); own_types = xml(cover['[Content_Types].xml'])
    overrides = {n.get('PartName', '').lstrip('/'): n.get('ContentType') for n in own_types if E.QName(n).localname == 'Override'}
    defaults = {n.get('Extension'): n.get('ContentType') for n in own_types if E.QName(n).localname == 'Default'}
    if 'word/numbering.xml' not in read_package(layout_path):
        E.SubElement(content_types, '{' + CT + '}Override', PartName='/word/numbering.xml', ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml')
    copied = {}; relationship_counter = 1
    def add_relationship(owner, source_owner, rid):
        nonlocal relationship_counter
        selected = next((e for e in edges(cover, source_owner) if e['id'] == rid), None)
        if selected is None:
            raise ValueError('Cover relationship is missing')
        if selected['external'] and selected['type'].endswith('/image'):
            raise ValueError('Cover pictures must be embedded')
        relation_part = rels_name(owner)
        relations = xml(layout[relation_part]) if relation_part in layout else E.Element('{' + REL + '}Relationships', nsmap={None: REL})
        used = {r.get('Id') for r in relations}
        new_id = 'rIdCover' + str(relationship_counter); relationship_counter += 1
        while new_id in used:
            new_id += '_'
        target = selected['target'] if selected['external'] else posixpath.relpath(copy_part(selected['part']), posixpath.dirname(owner))
        attributes = {'Id': new_id, 'Type': selected['type'], 'Target': target}
        if selected['external']:
            attributes['TargetMode'] = 'External'
        relations.append(E.Element('{' + REL + '}Relationship', attributes))
        layout[relation_part] = raw(relations)
        return new_id

    def copy_part(name):
        if name in copied:
            return copied[name]
        extension = name.rsplit('.', 1)[-1]
        target = ('word/media/cover-' if not name.endswith('.xml') else 'word/cover_parts/part-') + str(len(copied) + 1) + '.' + extension
        while target in layout:
            target = target.rsplit('.', 1)[0] + '_.' + extension
        copied[name] = target
        data = cover[name]
        if name.endswith('.xml'):
            tree = xml(data); validate_cover([tree], cover)
            if any(n.tag in {WN + 'bookmarkStart', WN + 'bookmarkEnd'} for n in tree.iter()):
                raise ValueError('Bookmarks in cover header/footer parts require a document-specific merge')
            remap(tree, paragraphs=True); remap_relationships(tree, name, target); order_properties(tree)
            data = raw(tree)
        layout[target] = data
        ctype = overrides.get(name) or defaults.get(extension)
        if not ctype:
            raise ValueError('Cover part content type missing')
        content_types.append(E.Element('{' + CT + '}Override', PartName='/' + target, ContentType=ctype))
        return target

    def remap_relationships(tree, source_owner, owner):
        for element in tree.iter():
            for key in list(element.attrib):
                if key.startswith(RN):
                    element.set(key, add_relationship(owner, source_owner, element.get(key)))

    existing_bookmarks = {n.get(WN + 'name') for b in rest for n in b.iter(WN + 'bookmarkStart')}
    next_bookmark = max([int(n.get(WN + 'id')) for b in rest for n in b.iter(WN + 'bookmarkStart')] + [0]) + 1
    ids, names = {}, {}
    for block in blocks:
        remap(block, paragraphs=True); remap_relationships(block, 'word/document.xml', 'word/document.xml')
        for start in block.iter(WN + 'bookmarkStart'):
            old = start.get(WN + 'id'); ids[old] = str(next_bookmark); next_bookmark += 1
            old_name = start.get(WN + 'name'); new_name = 'Cover_' + old_name
            while new_name in existing_bookmarks:
                new_name += '_'
            existing_bookmarks.add(new_name); names[old_name] = new_name
            start.set(WN + 'id', ids[old]); start.set(WN + 'name', new_name)
    for block in blocks:
        for end in block.iter(WN + 'bookmarkEnd'):
            if end.get(WN + 'id') not in ids:
                raise ValueError('Cover bookmark is not self-contained')
            end.set(WN + 'id', ids[end.get(WN + 'id')])
        for link in block.iter(WN + 'hyperlink'):
            anchor = link.get(WN + 'anchor')
            if anchor:
                if anchor not in names:
                    raise ValueError('Cover hyperlink refers outside the selected cover')
                link.set(WN + 'anchor', names[anchor])
    for block in list(body):
        body.remove(block)
    body.extend(blocks); body.extend(rest)
    for block in blocks:
        order_properties(block)
    order_properties(first_body_section)
    layout['word/document.xml'] = raw(document)
    layout['[Content_Types].xml'] = raw(content_types)
    checked = audit(layout)
    if not checked['pass']:
        raise ValueError('Merged DOCX failed package validation: ' + '; '.join(checked['errors']))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as file:
        with ZipFile(file, 'w', compression=ZIP_DEFLATED) as archive:
            for name, data in sorted(layout.items()):
                info = ZipInfo(name, (1980, 1, 1, 0, 0, 0)); info.create_system = 3; info.external_attr = 0o100644 << 16
                archive.writestr(info, data, compress_type=ZIP_DEFLATED)
    return {'result': str(output), 'cover_source': mode, 'cover_blocks': len(blocks),
            'layout_sha256': hashlib.sha256(layout_path.read_bytes()).hexdigest(),
            'cover_sha256': hashlib.sha256(cover_path.read_bytes()).hexdigest(),
            'result_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'boundary_spacing_after': {E.QName(k).localname: v for k, v in boundary_spacing.items()},
            'requires_field_refresh': True, 'visual_review_required': True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--layout', type=Path, default=SHARED / 'assets/word/base.docx')
    p.add_argument('--cover-source', choices=['builtin', 'uploaded', 'from_sample'], required=True)
    p.add_argument('--cover', type=Path)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    try:
        if (args.cover_source == 'builtin') == (args.cover is not None):
            raise ValueError('Select builtin alone, or uploaded/from_sample with an explicit cover file')
        raw_out = args.out.expanduser().absolute()
        if any(p.is_symlink() for p in [raw_out, *raw_out.parents]):
            raise ValueError('Output must not traverse a symlink')
        output = destination(raw_out.parent.resolve(), raw_out.name)
        if output.exists():
            raise ValueError('Output already exists; preserve it and select a new result path')
        if output.is_relative_to(SHARED.parent):
            raise ValueError('Task output must be outside the product installation/source')
        cover = args.cover or SHARED / 'assets/word/cover.docx'
        result = apply(args.layout.expanduser().resolve(), cover.expanduser().resolve(), output, args.cover_source)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, E.XMLSyntaxError, BadZipFile) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
