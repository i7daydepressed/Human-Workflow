"""Structural and cover-merge regressions; rendered pages are checked separately."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as X

SOURCE = Path(__file__).resolve().parents[1]
SCRIPTS = SOURCE / 'shared/scripts'
ASSETS = SOURCE / 'shared/assets/word'
sys.path.insert(0, str(SCRIPTS))
from docx_package import read_package, audit, W, R, REL, CT

try:
    from lxml import etree as E
    from word_cover import first_section
except ImportError:
    E = None

WN = '{' + W + '}'
NS = {'w': W}


def save(path, parts):
    with ZipFile(path, 'w', compression=ZIP_DEFLATED) as archive:
        for name, raw in parts.items():
            archive.writestr(name, raw)


class Preset(unittest.TestCase):
    def test_public_packages_have_no_orphans_external_links_or_provenance_parts(self):
        for name, count in [('base.docx', 3), ('cover.docx', 0)]:
            result = audit(read_package(ASSETS / name), public_preset=True)
            self.assertTrue(result['pass'], result)
            self.assertEqual(result['orphaned_parts'], [])
            self.assertEqual(result['external_relationships'], [])
            self.assertEqual(len(result['media']), count)

    def test_catalog_hashes_match_current_assets(self):
        catalog = json.loads((ASSETS / 'catalog.json').read_text())
        for role in ['layout', 'cover']:
            item = catalog[role]
            self.assertEqual(hashlib.sha256((ASSETS / item['file']).read_bytes()).hexdigest(), item['sha256'])
        self.assertEqual(catalog['layout']['classification'], 'neutral-derived-preset')

    def test_live_fields_multilevel_heading_and_layout_geometry(self):
        parts = read_package(ASSETS / 'base.docx')
        doc = X.fromstring(parts['word/document.xml'])
        codes = ''.join(n.text or '' for n in doc.iter(WN + 'instrText'))
        self.assertIn(' TOC ', codes)
        self.assertEqual(codes.count('PAGEREF '), 10)
        self.assertTrue(any(' PAGE ' in raw.decode() for name, raw in parts.items() if name.startswith('word/footer') and name.endswith('.xml')))
        nested = next(p for p in doc.findall('w:body/w:p', NS) if 'Вложенный подраздел' in ''.join(p.itertext()))
        self.assertEqual(nested.find('w:pPr/w:pStyle', NS).get(WN + 'val'), '3')
        self.assertEqual(nested.find('w:pPr/w:numPr/w:ilvl', NS).get(WN + 'val'), '2')
        self.assertEqual(nested.find('w:pPr/w:numPr/w:numId', NS).get(WN + 'val'), '11')
        for section in doc.iter(WN + 'sectPr'):
            self.assertEqual(section.find(WN + 'pgSz').get(WN + 'w'), '11906')
            self.assertEqual(section.find(WN + 'pgSz').get(WN + 'h'), '16838')
            margins = section.find(WN + 'pgMar')
            self.assertEqual([margins.get(WN + k) for k in ['top','bottom','left','right']], ['1134','1134','1701','851'])

    def test_neutral_pngs_contain_only_pixel_chunks(self):
        parts = read_package(ASSETS / 'base.docx')
        for name, raw in parts.items():
            if not name.startswith('word/media/'):
                continue
            self.assertEqual(raw[:8], b'\x89PNG\r\n\x1a\n')
            offset, chunks = 8, []
            while offset < len(raw):
                size = struct.unpack('>I', raw[offset:offset+4])[0]
                chunks.append(raw[offset+4:offset+8]); offset += 12 + size
            self.assertEqual(offset, len(raw))
            self.assertEqual(set(chunks), {b'IHDR', b'IDAT', b'IEND'})

    def test_dangling_resource_and_unknown_relationship_reference_fail(self):
        parts = read_package(ASSETS / 'base.docx')
        del parts['word/media/image1.png']
        self.assertFalse(audit(parts)['pass'])
        parts = read_package(ASSETS / 'base.docx')
        doc = X.fromstring(parts['word/document.xml'])
        doc.set('{' + R + '}id', 'rIdMissing')
        parts['word/document.xml'] = X.tostring(doc)
        self.assertFalse(audit(parts)['pass'])

    def test_orphan_and_dangling_content_type_fail_public_check(self):
        parts = read_package(ASSETS / 'base.docx')
        parts['word/unused.xml'] = b'<unused/>'
        self.assertFalse(audit(parts, public_preset=True)['pass'])
        parts = read_package(ASSETS / 'base.docx')
        types = X.fromstring(parts['[Content_Types].xml'])
        X.SubElement(types, '{' + CT + '}Override', PartName='/missing.xml', ContentType='application/xml')
        parts['[Content_Types].xml'] = X.tostring(types)
        self.assertFalse(audit(parts)['pass'])


@unittest.skipIf(E is None, 'Optional Word mode requires lxml')
class Covers(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.area = Path(self.temp.name)
        self.base = read_package(ASSETS / 'base.docx')

    def call(self, *args, code=0):
        result = subprocess.run([sys.executable, str(SCRIPTS / 'word_cover.py'), *map(str, args)], cwd='/', capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def merge(self, mode, cover=None):
        out = self.area / (mode + '.docx')
        args = ['--cover-source', mode, '--out', out]
        if cover is not None: args += ['--cover', cover]
        result = self.call(*args)
        self.assertTrue(result['requires_field_refresh'])
        return read_package(out)

    def custom(self):
        """Synthetic independent cover: another font, margins, logo and footer."""
        parts = dict(self.base); original = E.fromstring(parts['word/document.xml'])
        drawing = deepcopy(next(original.iter(WN + 'drawing')))
        doc = E.Element(WN + 'document', nsmap={'w': W, 'r': R}); body = E.SubElement(doc, WN + 'body')
        for text in ['Synthetic custom cover', 'Synthetic author']:
            paragraph = E.SubElement(body, WN + 'p'); props = E.SubElement(paragraph, WN + 'pPr')
            E.SubElement(props, WN + 'spacing', {WN + 'after': '560'})
            E.SubElement(E.SubElement(paragraph, WN + 'r'), WN + 't').text = text
        section = deepcopy(next(original.iter(WN + 'sectPr')))
        for ref in list(section):
            if ref.tag in {WN+'headerReference', WN+'footerReference', WN+'titlePg'}:section.remove(ref)
        section.find(WN + 'pgMar').set(WN + 'top', '1984')
        for kind, rid in [('header', 'rIdSyntheticHeader'), ('footer', 'rIdSyntheticFooter')]:
            section.insert(0, E.Element(WN + kind + 'Reference', {WN+'type':'default','{'+R+'}id':rid}))
            root = E.Element(WN + ('hdr' if kind == 'header' else 'ftr'), nsmap={'w':W,'r':R})
            paragraph = E.SubElement(root, WN + 'p')
            E.SubElement(E.SubElement(paragraph, WN + 'r'), WN + 't').text = 'Synthetic ' + kind
            if kind == 'header':E.SubElement(paragraph, WN + 'r').append(drawing)
            part = 'word/synthetic-' + kind + '.xml'; parts[part] = E.tostring(root)
            rels = E.fromstring(parts['word/_rels/document.xml.rels'])
            rels.append(E.Element('{'+REL+'}Relationship',Id=rid,Type=R+'/'+kind,Target=part[5:]))
            parts['word/_rels/document.xml.rels'] = E.tostring(rels)
            types = E.fromstring(parts['[Content_Types].xml'])
            types.append(E.Element('{'+CT+'}Override',PartName='/'+part,ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.'+kind+'+xml'))
            parts['[Content_Types].xml'] = E.tostring(types)
        # Reuse one embedded neutral picture, with a relationship owned by header.
        image_id = next(n for n in drawing.iter() if n.get('{'+R+'}embed')).get('{'+R+'}embed')
        relation = next(n for n in E.fromstring(parts['word/_rels/document.xml.rels']) if n.get('Id') == image_id)
        header_rels = E.Element('{'+REL+'}Relationships'); header_rels.append(deepcopy(relation))
        parts['word/_rels/synthetic-header.xml.rels'] = E.tostring(header_rels)
        body.append(section); parts['word/document.xml'] = E.tostring(doc)
        styles = E.fromstring(parts['word/styles.xml'])
        normal = next(s for s in styles.findall(WN+'style') if s.get(WN+'type')=='paragraph' and s.get(WN+'default')=='1')
        props = normal.find(WN+'rPr'); fonts = E.SubElement(props, WN+'rFonts')
        fonts.set(WN+'ascii','Arial');fonts.set(WN+'hAnsi','Arial')
        parts['word/styles.xml'] = E.tostring(styles)
        out = self.area / 'custom.docx';save(out,parts);return out

    def body_without_references(self, parts):
        body = E.fromstring(parts['word/document.xml']).find(WN + 'body')
        boundary, _ = first_section(body)
        rest = deepcopy(list(body)[boundary+1:])
        for block in rest:
            for section in block.iter(WN+'sectPr'):
                for ref in list(section):
                    if ref.tag in {WN+'headerReference',WN+'footerReference'}:section.remove(ref)
        return [E.tostring(b,method='c14n',exclusive=True) for b in rest]

    def test_all_cover_modes_preserve_body_table_media_and_original_styles(self):
        custom = self.custom()
        for mode, source in [('builtin',None),('from_sample',ASSETS/'base.docx'),('uploaded',custom)]:
            result = self.merge(mode, source)
            self.assertTrue(audit(result)['pass'])
            self.assertEqual(self.body_without_references(result), self.body_without_references(self.base))
            for name in ['word/media/image1.png','word/media/image2.png','word/media/image3.png']:
                self.assertEqual(result[name],self.base[name])
            old = E.fromstring(self.base['word/styles.xml']);new=E.fromstring(result['word/styles.xml'])
            lookup={s.get(WN+'styleId'):s for s in new.findall(WN+'style')}
            for style in old.findall(WN+'style'):
                self.assertEqual(E.tostring(style,method='c14n',exclusive=True),E.tostring(lookup[style.get(WN+'styleId')],method='c14n',exclusive=True))

    def test_custom_header_is_imported_and_blocked_from_inheriting_into_body(self):
        result = self.merge('uploaded', self.custom())
        doc = E.fromstring(result['word/document.xml']);body=doc.find(WN+'body');boundary,cover_section=first_section(body)
        main_section = next(s for b in list(body)[boundary+1:] for s in b.iter(WN+'sectPr'))
        cover_ref=cover_section.find(WN+'headerReference').get('{'+R+'}id')
        body_ref=main_section.find(WN+'headerReference').get('{'+R+'}id')
        self.assertNotEqual(cover_ref,body_ref)
        self.assertIn(b'Arial',result['word/styles.xml'])
        self.assertEqual(cover_section.find(WN+'pgMar').get(WN+'top'),'1984')
        self.assertEqual(main_section.find(WN+'pgMar').get(WN+'top'),'1134')
        self.assertEqual(body[boundary].find('w:pPr/w:spacing',NS).get(WN+'after'),'0')
        ids=[n.get('id') for name,raw in result.items() if name.endswith('.xml') for n in E.fromstring(raw).iter() if E.QName(n).localname=='docPr']
        self.assertEqual(len(ids),len(set(ids)))

    def test_choice_is_required_and_ambiguous_arguments_rejected(self):
        out=self.area/'result.docx'
        proc=subprocess.run([sys.executable,str(SCRIPTS/'word_cover.py'),'--out',str(out)],capture_output=True,text=True)
        self.assertEqual(proc.returncode,2);self.assertFalse(out.exists())
        self.call('--cover-source','builtin','--cover',ASSETS/'cover.docx','--out',out,code=2)
        self.call('--cover-source','uploaded','--out',out,code=2)
        self.assertFalse(out.exists())

    def test_uploaded_full_sample_is_rejected_before_output(self):
        out=self.area/'result.docx'
        self.call('--cover-source','uploaded','--cover',ASSETS/'base.docx','--out',out,code=2)
        self.assertFalse(out.exists())

    def test_existing_and_product_outputs_are_preserved(self):
        out=self.area/'result.docx';out.write_bytes(b'Keep current version')
        self.call('--cover-source','builtin','--out',out,code=2)
        self.assertEqual(out.read_bytes(),b'Keep current version')
        target=SOURCE/'word-result-must-not-exist.docx'
        self.call('--cover-source','builtin','--out',target,code=2)
        self.assertFalse(target.exists())

    def test_symlink_destination_is_rejected(self):
        outside=self.area/'outside';outside.mkdir();alias=self.area/'alias'
        try:alias.symlink_to(outside,target_is_directory=True)
        except OSError:self.skipTest('symlink unavailable')
        self.call('--cover-source','builtin','--out',alias/'result.docx',code=2)
        self.assertEqual(list(outside.iterdir()),[])

    def test_simple_and_split_cross_reference_fields_are_rejected(self):
        for index, fragment in enumerate(['<w:fldSimple w:instr=" REF other "/>','<w:r><w:instrText> PAGE</w:instrText></w:r><w:r><w:instrText>REF other </w:instrText></w:r>']):
            parts=read_package(ASSETS/'cover.docx');doc=E.fromstring(parts['word/document.xml'])
            paragraph=doc.find('w:body/w:p',NS)
            wrapper=E.fromstring(('<w:p xmlns:w="'+W+'">'+fragment+'</w:p>').encode())
            for node in wrapper:paragraph.append(node)
            parts['word/document.xml']=E.tostring(doc);cover=self.area/f'field{index}.docx';save(cover,parts)
            out=self.area/f'out{index}.docx'
            self.call('--cover-source','uploaded','--cover',cover,'--out',out,code=2)
            self.assertFalse(out.exists())

    def test_layout_without_explicit_cover_section_is_rejected(self):
        out=self.area/'result.docx'
        self.call('--layout',ASSETS/'cover.docx','--cover-source','builtin','--out',out,code=2)
        self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
