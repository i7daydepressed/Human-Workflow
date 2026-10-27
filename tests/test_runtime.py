"""Behavioral regressions for local runtime; no host install or visual Word claims."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

from synthetic_cases import write_catalog

SOURCE = Path(__file__).resolve().parents[1]
SCRIPTS = SOURCE / 'shared/scripts'


def call(script, *args, code=0):
    result = subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                            cwd='/', capture_output=True, text=True)
    if result.returncode != code:
        raise AssertionError(f'{script}: expected {code}, got {result.returncode}: {result.stdout} {result.stderr}')
    return json.loads(result.stdout) if result.stdout.strip() else {}


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def docx(path, field):
    with ZipFile(path, 'w') as z:
        z.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + field + '<w:sectPr/></w:body></w:document>')


class Runtime(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.area = Path(self.temporary.name)
        self.root = self.area / 'Проект с пробелами'
        self.root.mkdir()

    def link(self, path, target, directory=True):
        try:
            path.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError):
            self.skipTest('symlink unavailable on this OS')

    def report(self, text):
        (self.root / 'figure.png').write_bytes(b'parser fixture, not an image quality test')
        (self.root / 'report.md').write_text(text, encoding='utf-8')

    def test_english_report_and_figure_pass(self):
        self.report('# Report\n\n## Introduction\n\nPurpose.\n\n![Panel](figure.png)\n\nFigure 1 – Example\n\nObserved result.\n')
        result = call('report_workspace.py', 'audit', self.root, '--language', 'en')
        self.assertEqual((result['captions'], result['images']), (1, 1))
        self.assertEqual((result['errors'], result['warnings']), ([], []))

    def test_english_missing_caption_fails(self):
        self.report('## Introduction\n\n![Panel](figure.png)\n\nObserved result.\n')
        result = call('report_workspace.py', 'audit', self.root, '--language', 'en', code=1)
        self.assertIn('caption missing', ' '.join(result['errors']))

    def test_english_duplicate_number_fails(self):
        block = '![Panel](figure.png)\n\nFigure 1 - Example\n\nObserved result.\n\n'
        self.report('## Introduction\n\n' + block * 2)
        result = call('report_workspace.py', 'audit', self.root, '--language', 'en', code=1)
        self.assertEqual(result['captions'], 2)

    def test_profile_style_is_not_forced_by_audit(self):
        self.report('## Введение\n\nОбъём — характеристика.\n\n![Панель](figure.png)\n\nРисунок 1 — Пример.\n\nПояснение.\n')
        result = call('report_workspace.py', 'audit', self.root)
        self.assertFalse(result['warnings'])

    def test_english_init_no_private_sample_and_preserves_edits(self):
        call('report_workspace.py', 'init', self.root, '--language', 'en')
        self.assertIn('Introduction', (self.root / 'report.md').read_text())
        self.assertIn('content_authority', (self.root / 'project.md').read_text())
        self.assertFalse(list(self.root.rglob('*.docx')))
        (self.root / 'report.md').write_text('Manual edit')
        call('report_workspace.py', 'init', self.root, '--language', 'ru')
        self.assertEqual((self.root / 'report.md').read_text(), 'Manual edit')

    def test_checkpoint_destination_external_symlink_rejected(self):
        outside = self.area / 'outside'; outside.mkdir()
        (self.root / 'project.md').write_text('State')
        self.link(self.root / 'checkpoints', outside)
        call('report_workspace.py', 'checkpoint', self.root, '--mode', 'accompany', code=2)
        self.assertEqual(list(outside.iterdir()), [])

    def test_checkpoint_destination_internal_symlink_rejected(self):
        target = self.root / 'other'; target.mkdir()
        (self.root / 'project.md').write_text('State')
        self.link(self.root / 'checkpoints', target)
        call('report_workspace.py', 'checkpoint', self.root, '--mode', 'accompany', code=2)
        self.assertEqual(list(target.iterdir()), [])

    def test_checkpoint_destination_file_rejected(self):
        (self.root / 'project.md').write_text('State')
        path = self.root / 'checkpoints'; path.write_bytes(b'keep')
        call('report_workspace.py', 'checkpoint', self.root, '--mode', 'accompany', code=2)
        self.assertEqual(path.read_bytes(), b'keep')

    def test_init_preflights_symlink_parent_before_writes(self):
        outside = self.area / 'outside'; outside.mkdir()
        self.link(self.root / 'assets', outside)
        call('report_workspace.py', 'init', self.root, code=2)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.root / 'report.md').exists())
        self.assertFalse((self.root / 'agent-logs').exists())

    def test_init_rejects_existing_file_symlink(self):
        target = self.area / 'state.md'; target.write_text('Keep')
        self.link(self.root / 'project.md', target, directory=False)
        call('report_workspace.py', 'init', self.root, '--mode', 'accompany', code=2)
        self.assertEqual(target.read_text(), 'Keep')

    def test_toc_is_required_only_when_selected(self):
        old = self.root / 'old.docx'; new = self.root / 'new.docx'
        docx(old, '<w:p><w:r><w:instrText> TOC \\o "1-3" </w:instrText></w:r></w:p>')
        docx(new, '<w:p><w:r><w:t>No TOC</w:t></w:r></w:p>')
        result = call('docx_guard.py', old, new, '--require-toc', code=1)
        self.assertFalse(result['toc_field_present'])
        partial = call('docx_guard.py', old, new, '--tables')
        self.assertTrue(partial['pass'])

    def test_simple_and_split_toc_fields_are_recognized(self):
        path = self.root / 'field.docx'
        for field in ['<w:p><w:fldSimple w:instr=" TOC \\o &quot;1-3&quot; "/></w:p>',
                      '<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText> TO</w:instrText></w:r><w:r><w:instrText>C \\o "1-3" </w:instrText></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>']:
            docx(path, field)
            self.assertTrue(call('docx_guard.py', path, path, '--require-toc')['pass'])

    def test_hyperlink_with_toc_in_target_is_not_a_toc(self):
        path = self.root / 'field.docx'
        docx(path, '<w:p><w:r><w:instrText> HYPERLINK "https://example.org/TOC " </w:instrText></w:r></w:p>')
        call('docx_guard.py', path, path, '--require-toc', code=1)

    def test_english_catalog_labels_and_index(self):
        path = write_catalog(self.root, 'en')
        call('case_catalog.py', 'validate', path)
        out = self.root / 'index.md'
        call('case_catalog.py', 'index', path, '--language', 'en', '--out', out)
        self.assertIn('| 1.4 | 1.3 |', out.read_text())
        self.assertIn('No maximum specified', out.read_text())

    def test_index_output_symlink_rejected(self):
        path = write_catalog(self.root)
        outside = self.area / 'outside.md'; outside.write_text('Keep')
        out = self.root / 'index.md'; self.link(out, outside, directory=False)
        call('case_catalog.py', 'index', path, '--out', out, code=2)
        self.assertEqual(outside.read_text(), 'Keep')


class InstallationWrites(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.area = Path(self.temporary.name).resolve()
        self.source = self.area / 'product-copy'
        shutil.copytree(SOURCE / 'shared', self.source / 'shared',
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        self.scripts = self.source / 'shared/scripts'
        self.identity = self.area / 'identity.json'
        write_json(self.identity, {key: 'synthetic' for key in
                   ['agent', 'agent_id', 'id_source', 'model', 'model_source',
                    'user', 'task', 'skill_version', 'timezone']})
        self.entry = self.area / 'entry.json'
        write_json(self.entry, {'goal': 'Synthetic regression', 'result': 'Checked'})
        self.catalog = write_catalog(self.area, 'en')

    def snapshot(self):
        return {p.relative_to(self.source).as_posix():
                ('symlink', str(p.readlink())) if p.is_symlink() else
                ('file', p.read_bytes()) if p.is_file() else ('directory', None)
                for p in self.source.rglob('*')}

    def run_cli(self, script, *args, expected=0):
        result = subprocess.run([sys.executable, '-B', str(self.scripts / script),
                                 *map(str, args)], cwd=self.area, capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def imported(self, expression, *args):
        code = ('import sys\nfrom pathlib import Path\n'
                'sys.path.insert(0, sys.argv[1])\n'
                'import report_workspace, agent_journal\n'
                'args = [Path(p) for p in sys.argv[2:]]\n' + expression)
        return subprocess.run([sys.executable, '-B', '-c', code, str(self.scripts),
                               *map(str, args)], cwd=self.area, capture_output=True, text=True)

    def assert_import_rejected(self, expression, *args):
        before = self.snapshot()
        result = self.imported(expression, *args)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('outside the product source/installation', result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_imported_workspace_and_journal_reject_internal_roots_before_writes(self):
        target = self.source / 'task'
        self.assert_import_rejected("report_workspace.initialize(args[0], 'Test', 'accompany')", target)
        target.mkdir()
        (target / 'project.md').write_text('Keep state')
        self.assert_import_rejected("report_workspace.checkpoint(args[0], 'draft', mode='accompany')", target)
        self.assert_import_rejected('agent_journal.start(args[0], args[1])', target, self.identity)
        self.assert_import_rejected("agent_journal.append(args[0], 'synthetic', args[1])", target, self.entry)
        logs = target / 'agent-logs'; logs.mkdir()
        (logs / 'synthetic.md').write_text('Keep original log')
        (logs / 'synthetic.identity.json').write_text('{}')
        self.assert_import_rejected("agent_journal.append(args[0], 'synthetic', args[1])", target, self.entry)

    def test_equal_root_and_symlink_alias_into_installation_are_rejected(self):
        self.assert_import_rejected("report_workspace.initialize(args[0], 'Test')", self.source)
        alias = self.area / 'alias'
        try:
            alias.symlink_to(self.source, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('symlink unavailable')
        self.assert_import_rejected("report_workspace.initialize(args[0], 'Test')", alias / 'task')
        self.assert_import_rejected('agent_journal.start(args[0], args[1])', alias, self.identity)

    def test_internal_output_guards_preserve_bundled_reads(self):
        sample = self.source / 'shared/assets/word/base.docx'
        before = self.snapshot()
        for out in [self.source / 'new/inventory.json', self.source]:
            result = self.run_cli('inspect_word_sample.py', sample, '--out', out, expected=1)
            self.assertIn('outside the product source/installation', result.stderr)
        result = self.run_cli('case_catalog.py', 'index', self.catalog,
                              '--out', self.source / 'new/index.md', expected=2)
        self.assertIn('outside the product source/installation', result.stdout)
        self.assertEqual(self.snapshot(), before)
        inspected = json.loads(self.run_cli('inspect_word_sample.py', sample).stdout)
        self.assertEqual(inspected['sha256'], hashlib.sha256(sample.read_bytes()).hexdigest())
        self.assertTrue(inspected['blocks'])
        self.assertIn('Accepted work and ratings',
                      self.run_cli('case_catalog.py', 'index', self.catalog, '--language', 'en').stdout)
        self.assertEqual(self.snapshot(), before)

    def test_external_similar_prefix_and_repeat_operations_preserve_work(self):
        root = self.area / 'product-copy-next'
        initial = self.imported("report_workspace.initialize(args[0], 'Test', 'accompany', 'en')", root)
        self.assertEqual(initial.returncode, 0, initial.stderr)
        (root / 'project.md').write_text('Manual state')
        repeated = self.imported("report_workspace.initialize(args[0], 'Changed', 'accompany', 'en')", root)
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertEqual((root / 'project.md').read_text(), 'Manual state')
        checkpoint = self.imported("report_workspace.checkpoint(args[0], 'draft', mode='accompany')", root)
        self.assertEqual(checkpoint.returncode, 0, checkpoint.stderr)
        saved = Path(json.loads(checkpoint.stdout)['checkpoint'])
        self.assertEqual((saved / 'project.md').read_text(), 'Manual state')
        started = json.loads(self.run_cli('agent_journal.py', 'start', root, '--identity', self.identity).stdout)
        journal = Path(started['journal']); old = journal.read_bytes()
        self.run_cli('agent_journal.py', 'append', root, '--run-id', started['run_id'], '--entry', self.entry)
        self.assertTrue(journal.read_bytes().startswith(old))
        self.assertIn(b'Synthetic regression', journal.read_bytes())
        sample = self.source / 'shared/assets/word/base.docx'
        inventory = root / 'inventory.json'
        self.run_cli('inspect_word_sample.py', sample, '--out', inventory)
        self.assertEqual(json.loads(inventory.read_text())['sha256'], hashlib.sha256(sample.read_bytes()).hexdigest())
        index = root / 'index.md'
        self.run_cli('case_catalog.py', 'index', self.catalog, '--language', 'en', '--out', index)
        self.assertIn('Accepted work and ratings', index.read_text())

    def test_output_leaf_symlinks_remain_rejected(self):
        outside = self.area / 'preserve.txt'; outside.write_text('Keep')
        sample = self.source / 'shared/assets/word/base.docx'
        for script, arguments, code in [
                ('inspect_word_sample.py', [sample], 1),
                ('case_catalog.py', ['index', self.catalog], 2)]:
            with self.subTest(script=script):
                output = self.area / (script + '.out')
                try:
                    output.symlink_to(outside)
                except (OSError, NotImplementedError):
                    self.skipTest('symlink unavailable')
                result = self.run_cli(script, *arguments, '--out', output, expected=code)
                self.assertIn('symlink', result.stdout + result.stderr)
                self.assertEqual(outside.read_text(), 'Keep')


class Profiles(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.area = Path(self.temporary.name)
        self.root = self.area / 'owner'

    def init(self):
        return call('profile.py', 'init', self.root, '--instruction-language', 'en',
                    '--output-language', 'ru', '--log-language', 'ru')

    def profile(self):
        return json.loads((self.root / 'profile.json').read_text())

    def with_resource(self):
        self.init()
        resource = self.root / 'resources/layout.docx'; resource.parent.mkdir()
        resource.write_bytes(b'User-owned opaque template bytes')
        data = self.profile()
        data['word']['layout'] = {'source': 'file', 'resource': {'path': 'resources/layout.docx', 'sha256': hashlib.sha256(resource.read_bytes()).hexdigest()}}
        data['workspace'] = {'kind': 'local', 'locator': str(self.area / 'old-workspace')}
        write_json(self.root / 'profile.json', data)
        return resource

    def test_repeat_setup_is_byte_preserving(self):
        first = self.init(); before = (self.root / 'profile.json').read_bytes()
        second = call('profile.py', 'init', self.root, '--instruction-language', 'ru')
        self.assertFalse(second['created']); self.assertTrue(second['unchanged'])
        self.assertEqual(before, (self.root / 'profile.json').read_bytes())
        self.assertEqual(first['profile_id'], second['profile_id'])
        self.assertEqual(self.profile()['word']['cover']['source'], 'unselected')

    def test_unknown_future_schema_is_not_rewritten(self):
        self.init(); data = self.profile(); data['schema_version'] = 99
        write_json(self.root / 'profile.json', data); before = (self.root / 'profile.json').read_bytes()
        call('profile.py', 'init', self.root, code=2)
        self.assertEqual(before, (self.root / 'profile.json').read_bytes())

    def test_transfer_preserves_selected_template_without_old_paths(self):
        resource = self.with_resource(); original = resource.read_bytes()
        (self.root / 'not-selected.log').write_text('Private history must stay here')
        exported = self.area / 'exported'
        call('profile.py', 'export', self.root, exported)
        self.assertFalse((exported / 'not-selected.log').exists())
        self.assertNotIn(str(self.area), (exported / 'profile.json').read_text())
        imported = self.area / 'different-machine'
        call('profile.py', 'import', exported, imported)
        call('profile.py', 'validate', imported)
        self.assertEqual((imported / 'resources/layout.docx').read_bytes(), original)
        self.assertEqual(resource.read_bytes(), original)
        call('profile.py', 'init', imported)
        self.assertEqual((imported / 'resources/layout.docx').read_bytes(), original)

    def test_tampered_transfer_rejected_before_import(self):
        self.with_resource(); exported = self.area / 'exported'
        call('profile.py', 'export', self.root, exported)
        (exported / 'resources/layout.docx').write_bytes(b'altered')
        target = self.area / 'target'
        call('profile.py', 'import', exported, target, code=2)
        self.assertFalse(target.exists())

    def test_import_identity_conflict_preserves_existing(self):
        self.init(); exported = self.area / 'exported'
        call('profile.py', 'export', self.root, exported)
        before = (self.root / 'profile.json').read_bytes()
        call('profile.py', 'import', exported, self.root, code=2)
        self.assertEqual(before, (self.root / 'profile.json').read_bytes())

    def test_profile_cannot_live_in_product_source(self):
        target = SOURCE / 'private-test-profile'
        call('profile.py', 'init', target, code=2)
        self.assertFalse(target.exists())

    def test_escaping_resource_rejected(self):
        self.init(); data = self.profile()
        data['word']['cover'] = {'source': 'uploaded', 'resource': {'path': '../outside.docx', 'sha256': '0' * 64}}
        write_json(self.root / 'profile.json', data)
        call('profile.py', 'validate', self.root, code=2)

    def test_symlink_profile_is_not_overwritten(self):
        self.root.mkdir()
        target = self.area / 'outside.json'; target.write_text('{}')
        try:
            (self.root / 'profile.json').symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest('symlink unavailable')
        call('profile.py', 'init', self.root, code=2)
        self.assertEqual(target.read_text(), '{}')

    def test_layout_and_cover_choices_are_independent(self):
        self.with_resource(); data = self.profile()
        data['word']['cover'] = {'source': 'builtin', 'preset_id': 'base-cover-pending'}
        write_json(self.root / 'profile.json', data)
        call('profile.py', 'validate', self.root)
        self.assertEqual(data['word']['layout']['source'], 'file')
        self.assertEqual(data['word']['cover']['source'], 'builtin')

    def test_invalid_profile_resource_keys_rejected(self):
        self.init(); data = self.profile(); data['word']['cover'] = {'source': 'unselected', 'resource': {}}
        write_json(self.root / 'profile.json', data)
        call('profile.py', 'validate', self.root, code=2)

    def test_export_through_dangling_symlink_is_rejected(self):
        self.init(); outside = self.area / 'outside'; alias = self.area / 'alias'
        try:
            alias.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('symlink unavailable')
        call('profile.py', 'export', self.root, alias, code=2)
        self.assertFalse(outside.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
