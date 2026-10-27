"""Source checkpoint checks. These do not stand in for a host install test."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

SOURCE = Path(__file__).resolve().parents[1]


class SourcePackage(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.area = Path(self.temporary.name)

    def clone(self):
        root = self.area / 'source'; root.mkdir()
        for name in json.loads((SOURCE / 'packaging/source-allowlist.json').read_text()):
            target = root / name; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((SOURCE / name).read_bytes())
        return root

    def build(self, root, name='source.zip', code=0):
        output = self.area / name
        result = subprocess.run([sys.executable, str(SOURCE / 'tools/build_source.py'),
                                 '--root', str(root), '--out', str(output)],
                                cwd='/', capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return output

    def test_allowlist_and_manifest_match_bytes_and_exclude_unknown_files(self):
        root = self.clone()
        (root / 'unlisted-private.txt').write_text('Synthetic exclusion sentinel')
        (root / '.DS_Store').write_bytes(b'synthetic finder data')
        archive = self.build(root)
        allowed = json.loads((root / 'packaging/source-allowlist.json').read_text())
        with ZipFile(archive) as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(set(z.namelist()), set(allowed) | {'SOURCE-MANIFEST.json'})
            manifest = json.loads(z.read('SOURCE-MANIFEST.json'))
            self.assertFalse(manifest['installable_plugin'])
            for name, digest in manifest['files_sha256'].items():
                self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(), digest)
                self.assertEqual(z.read(name), (root / name).read_bytes())

    def test_build_is_byte_reproducible(self):
        first = self.build(SOURCE, 'first.zip')
        second = self.build(SOURCE, 'second.zip')
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_allowlist_escape_and_duplicates_rejected(self):
        root = self.clone(); allow = root / 'packaging/source-allowlist.json'
        for value in [['../outside.txt'], ['README.md', 'README.md']]:
            allow.write_text(json.dumps(value))
            result = self.build(root, code=2)
            self.assertFalse(result.exists())

    def test_allowlisted_symlink_rejected(self):
        root = self.clone(); path = root / 'README.md'; path.unlink()
        outside = self.area / 'outside.md'; outside.write_text('Synthetic external sentinel')
        try:
            path.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest('symlink unavailable')
        result = self.build(root, code=2)
        self.assertFalse(result.exists())

    def test_two_entrypoints_and_paired_contract_ids(self):
        entries = sorted(p.relative_to(SOURCE).as_posix() for p in SOURCE.rglob('SKILL.md'))
        self.assertEqual(entries, ['skills/human-step/SKILL.md', 'skills/md-word/SKILL.md'])
        registry = json.loads((SOURCE / 'packaging/contracts.json').read_text())
        for workflow, ids in registry['contracts'].items():
            for language in ['en', 'ru']:
                text = (SOURCE / f'locales/{language}/{workflow}/workflow.md').read_text()
                found = re.findall(r'<!-- contract:([A-Z_]+) -->', text)
                self.assertEqual(found, ids)

    def test_local_markdown_links_resolve(self):
        names = json.loads((SOURCE / 'packaging/source-allowlist.json').read_text())
        self.assertFalse(any(name.startswith(('docs/codex/', 'docx/codex/')) for name in names))
        for path in (SOURCE / name for name in names if name.endswith('.md')):
            for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text()):
                if re.match(r'^[a-z]+:', target) or target.startswith('#'):
                    continue
                target = target.split('#', 1)[0]
                self.assertTrue((path.parent / target).is_file(), f'{path.name}: {target}')

    def test_private_marker_scanner_sees_split_xml_runs(self):
        root = self.area / 'payload'; root.mkdir()
        marker = 'SyntheticPrivatePerson'
        xml = '<document><run>Synthetic</run><run>PrivatePerson</run></document>'
        with ZipFile(root / 'sample.docx', 'w') as z:
            z.writestr('word/document.xml', xml)
        config = self.area / 'private-markers.json'; config.write_text(json.dumps({'literals': [marker]}))
        result = subprocess.run([sys.executable, str(SOURCE / 'tools/audit_payload.py'), str(root), '--markers', str(config)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertGreater(json.loads(result.stdout)['findings'], 0)
        self.assertNotIn(marker, result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
