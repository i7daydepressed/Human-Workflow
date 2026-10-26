import json, subprocess, sys, tempfile, unittest, hashlib, copy
from pathlib import Path
from zipfile import ZipFile
from synthetic_cases import write_catalog

S=Path(__file__).resolve().parents[1]
RESULTS=[]
def call(script,*args,code=0):
 p=subprocess.run([sys.executable,str(S/'shared/scripts'/script),*map(str,args)],capture_output=True,text=True)
 if p.returncode!=code: raise AssertionError(f'{script}: expected {code}, got {p.returncode}: {p.stdout} {p.stderr}')
 return json.loads(p.stdout) if p.stdout.strip() else {}

def tiny_docx(path,cover='Титул',cell='Ручная таблица',width='1000',font='28',media=b'PNG-SAME'):
 xml=f'''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"><w:body><w:p><w:r><w:t>{cover}</w:t></w:r></w:p><w:p><w:r><w:instrText> TOC \\o "1-3" </w:instrText></w:r></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:rPr><w:sz w:val="{font}"/></w:rPr><w:t>{cell}</w:t></w:r></w:p></w:tc></w:tr></w:tbl><w:p><w:r><w:drawing><wp:inline><wp:extent cx="{width}" cy="500"/></wp:inline></w:drawing></w:r></w:p><w:sectPr/></w:body></w:document>'''
 with ZipFile(path,'w') as z:
  z.writestr('word/document.xml',xml);z.writestr('word/media/a.png',media)

class Scripts(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
 def init(self):return call('report_workspace.py','init',self.root,'--title','Проверка')
 def test_01_init_is_idempotent(self):
  self.init();p=self.root/'report.md';p.write_text('Согласованный текст');self.init();self.assertEqual(p.read_text(),'Согласованный текст');self.assertTrue((self.root/'agent-logs').is_dir())
 def report(self,text):
  self.init();(self.root/'draft_short.md').write_text(text);(self.root/'assets/a.png').write_bytes(b'a')
 def test_02_grouped_figures_custom_report(self):
  self.report('# Отчет\n\n## Введение\n\nТекст.\n\n![А](assets/a.png)\n\n![Б](assets/a.png)\n\nРисунок 1 – Пример\n\nРезультат.\n')
  r=call('report_workspace.py','audit',self.root,'--report','draft_short.md');self.assertEqual((r['images'],r['captions']),(2,1));self.assertFalse(r['errors']);self.assertFalse(r['warnings'])
 def test_03_missing_picture_is_error(self):
  self.report('![А](assets/missing.png)\n\nРисунок 1 – Пример\n\nРезультат.')
  r=call('report_workspace.py','audit',self.root,'--report','draft_short.md',code=1);self.assertTrue(any('отсутствует' in e for e in r['errors']))
 def test_04_no_text_after_figure_is_error(self):
  self.report('![А](assets/a.png)\n\nРисунок 1 – Пример\n\n## 1. Заголовок')
  call('report_workspace.py','audit',self.root,'--report','draft_short.md',code=1)
 def test_05_no_caption_is_error(self):
  self.report('![А](assets/a.png)\n\nРезультат.')
  r=call('report_workspace.py','audit',self.root,'--report','draft_short.md',code=1);self.assertTrue(any('подпись' in e for e in r['errors']))
 def test_06_checkpoint_has_hashes_and_preserves_previous(self):
  self.report('# Отчет');(self.root/'output/result.docx').write_bytes(b'docx');(self.root/'agent-logs/run.md').write_text('Лог');(self.root/'word-conversion/build.py').write_text('pass');(self.root/'checks').mkdir();(self.root/'checks/audit.json').write_text('{}')
  a=call('report_workspace.py','checkpoint',self.root,'--report','draft_short.md','--label','user-final');old=Path(a['checkpoint']);before=(old/'manifest.json').read_bytes()
  (self.root/'assets/a.png').write_bytes(b'new')
  b=call('report_workspace.py','checkpoint',self.root,'--report','draft_short.md');new=Path(b['checkpoint']);self.assertEqual(before,(old/'manifest.json').read_bytes());self.assertEqual((old/'assets/a.png').read_bytes(),b'a')
  m=json.loads((new/'manifest.json').read_text());self.assertIn('draft_short.md',m['files_sha256']);self.assertIn('output/result.docx',m['files_sha256']);self.assertIn('agent-logs/run.md',m['files_sha256']);self.assertIn('word-conversion/build.py',m['files_sha256']);self.assertIn('checks/audit.json',m['files_sha256']);self.assertFalse(any('checkpoints' in p for p in m['files_sha256']))
  for p,h in m['files_sha256'].items():self.assertEqual(hashlib.sha256((new/p).read_bytes()).hexdigest(),h)
 def test_07_acceptance_requires_confirmation(self):
  self.init();call('report_workspace.py','checkpoint',self.root,'--label','teacher-accepted',code=2)
  f=self.root/'confirmation.json';f.write_text(json.dumps({'user':'test-user','quote':'Подтверждение приемки синтетического тестового случая','status':'user_confirmed'}))
  r=call('report_workspace.py','checkpoint',self.root,'--label','teacher-accepted','--confirmation',f);self.assertTrue(Path(r['checkpoint']).exists())
 def test_08_paths_cannot_escape_or_symlink(self):
  self.init();call('report_workspace.py','audit',self.root,'--report','../outside.md',code=2)
  (self.root/'alias.md').symlink_to(self.root/'report.md');call('report_workspace.py','audit',self.root,'--report','alias.md',code=2)
  (self.root/'assets/link.png').symlink_to(self.root/'report.md');call('report_workspace.py','checkpoint',self.root,code=2)
 def identity(self):
  f=self.root/'identity.json';f.write_text(json.dumps({k:'неизвестно' for k in ['agent','agent_id','id_source','model','model_source','user','task','skill_version','timezone']}));return f
 def test_09_journal_append_and_identity(self):
  r=call('agent_journal.py','start',self.root,'--identity',self.identity());p=Path(r['journal']);before=p.read_bytes();e=self.root/'entry.json';e.write_text(json.dumps({'goal':'Проверка','actions':['Прочитали MD'],'result':'Успешно','checks':['Аудит']}));call('agent_journal.py','append',self.root,'--run-id',r['run_id'],'--entry',e);self.assertTrue(p.read_bytes().startswith(before));self.assertIn('Проверка',p.read_text());self.assertTrue(Path(r['identity']).is_file())
 def test_10_bad_journal_input_rejected(self):
  f=self.root/'bad.json';f.write_text('{}');call('agent_journal.py','start',self.root,'--identity',f,code=2);call('agent_journal.py','append',self.root,'--run-id','../someone','--entry',f,code=2)
 def catalog(self):
  return write_catalog(self.root)
 def test_11_ratings_known_preference_separate_grade(self):
  p=self.catalog();r=call('case_catalog.py','validate',p);self.assertEqual(r['cases'],2);call('case_catalog.py','index',p,'--out',self.root/'index.md');t=(self.root/'index.md').read_text();self.assertIn('1,4',t);self.assertIn('0,95',t);self.assertIn('1 – нормальный результат',t);self.assertIn('| 1,4 | 1,3 |',t);self.assertIn('Максимум не задан',t)
 def test_12_rating_mismatch_and_false_acceptance_rejected(self):
  p=self.catalog();d=json.loads(p.read_text());d['cases'][0]['user_rating']['value']='1.2';p.write_text(json.dumps(d));call('case_catalog.py','validate',p,code=2)
  p=self.catalog();d=json.loads(p.read_text());d['cases'][0]['acceptance']['quote']='';p.write_text(json.dumps(d));call('case_catalog.py','validate',p,code=2)
 def test_13_docx_preservation_and_format_only_change(self):
  a=self.root/'a.docx';b=self.root/'b.docx';tiny_docx(a);tiny_docx(b,font='24');r=call('docx_guard.py',a,b,'--cover-before','1','--tables','--media','--geometry');self.assertTrue(r['pass']);self.assertTrue(r['toc_field_present'])
 def test_14_docx_detects_each_selected_change(self):
  a=self.root/'a.docx';b=self.root/'b.docx';tiny_docx(a)
  for fields,flag in [({'cover':'Другой титул'},['--cover-before','1']),({'cell':'Старый MD потерял ручную правку'},['--tables']),({'width':'9999'},['--geometry']),({'media':b'changed'},['--media'])]:
   tiny_docx(b,**fields);r=call('docx_guard.py',a,b,*flag,code=1);self.assertFalse(r['pass'])
 def test_15_invalid_docx_reports_error(self):
  a=self.root/'bad.docx';a.write_bytes(b'bad');call('docx_guard.py',a,a,'--tables',code=2)


 def test_16_accompany_creates_no_report_or_word(self):
  call('report_workspace.py','init',self.root,'--mode','accompany','--title','Работа')
  self.assertTrue((self.root/'project.md').is_file());self.assertTrue((self.root/'agent-logs').is_dir())
  self.assertFalse((self.root/'report.md').exists());self.assertFalse((self.root/'word-examples').exists());self.assertFalse((self.root/'assets').exists())
  (self.root/'project.md').write_text('Согласованные требования и состояние')
  call('report_workspace.py','init',self.root,'--mode','accompany')
  self.assertEqual((self.root/'project.md').read_text(),'Согласованные требования и состояние')
 def test_17_accompany_checkpoint_keeps_spec_without_report(self):
  call('report_workspace.py','init',self.root,'--mode','accompany')
  (self.root/'tasks').mkdir();(self.root/'tasks/spec.md').write_text('Редакция 2.5')
  result=call('report_workspace.py','checkpoint',self.root,'--mode','accompany','--include','tasks/spec.md')
  snap=Path(result['checkpoint']);m=json.loads((snap/'manifest.json').read_text())
  self.assertIsNone(m['report']);self.assertEqual(m['mode'],'accompany');self.assertIn('tasks/spec.md',m['files_sha256']);self.assertFalse((snap/'report.md').exists())
  import hashlib
  self.assertEqual(m['files_sha256']['tasks/spec.md'],hashlib.sha256((snap/'tasks/spec.md').read_bytes()).hexdigest())
 def test_18_include_rejects_missing_escape_and_checkpoints(self):
  call('report_workspace.py','init',self.root,'--mode','accompany')
  for path in ['missing.md','../outside.md','checkpoints','/etc/passwd','.']:
   call('report_workspace.py','checkpoint',self.root,'--mode','accompany','--include',path,code=2)
 def test_19_legacy_unknown_scale_still_supported(self):
  p=self.catalog();d=json.loads(p.read_text());d['schema_version']=1;d.pop('scales');d['cases'][0]['teacher_grade']=None
  for c in d['cases']:c['user_rating'].pop('scale_id')
  p.write_text(json.dumps(d));call('case_catalog.py','validate',p);call('case_catalog.py','index',p,'--out',self.root/'legacy-index.md')
  self.assertIn('шкалы ее смысл и границы неизвестны',(self.root/'legacy-index.md').read_text())
 def test_20_teacher_header_and_provenance_checked(self):
  p=self.catalog();d=json.loads(p.read_text());d['cases'][0]['teacher_grade']['value']='1.7';d['cases'][0]['teacher_grade']['display']='1,7';p.write_text(json.dumps(d));call('case_catalog.py','validate',p,code=2)
  p=self.catalog();d=json.loads(p.read_text());d['cases'][0]['teacher_grade']['source_ref']='';p.write_text(json.dumps(d));call('case_catalog.py','validate',p,code=2)
 def test_21_explicit_bounds_and_unknown_scale_not_invented(self):
  p=self.catalog();d=json.loads(p.read_text());d['scales']['sample-relative-v1']['max']='1';p.write_text(json.dumps(d));call('case_catalog.py','validate',p,code=2)
  p=self.catalog();d=json.loads(p.read_text());d['cases'][0]['user_rating']['scale_id']='absent';p.write_text(json.dumps(d));call('case_catalog.py','validate',p,code=2)
 def test_22_grade_date_unknown_is_not_report_date(self):
  p=self.catalog();d=json.loads(p.read_text());t=d['cases'][0]['teacher_grade'];self.assertIsNone(t['date']);self.assertEqual(t['reported_date'],'2000-01-03');call('case_catalog.py','validate',p)
 def test_23_nonfinite_and_float_ratings_rejected(self):
  for value in ['NaN','Infinity',1.4]:
   p=self.catalog();d=json.loads(p.read_text());d['cases'][0]['user_rating']['value']=value;p.write_text(json.dumps(d));call('case_catalog.py','validate',p,code=2)


 def test_24_catalog_index_uses_recorded_provider_url(self):
  p=self.catalog();d=json.loads(p.read_text());url='https://example.org/cases/case-001';d['cases'][0]['case_url']=url;p.write_text(json.dumps(d))
  call('case_catalog.py','index',p,'--out',self.root/'provider-index.md');self.assertIn(']('+url+')',(self.root/'provider-index.md').read_text())


 def test_25_normalized_internal_path_is_actually_in_snapshot(self):
  call('report_workspace.py','init',self.root,'--mode','accompany');(self.root/'nested').mkdir();(self.root/'target.txt').write_text('Сохраняемый материал')
  alias=f'nested/../../{self.root.name}/target.txt'
  result=call('report_workspace.py','checkpoint',self.root,'--mode','accompany','--include',alias);snap=Path(result['checkpoint']);m=json.loads((snap/'manifest.json').read_text())
  self.assertEqual((snap/'target.txt').read_text(),'Сохраняемый материал');self.assertIn('target.txt',m['files_sha256']);self.assertFalse(any('..' in Path(p).parts for p in m['files_sha256']))
 def test_26_include_through_internal_symlink_is_rejected(self):
  call('report_workspace.py','init',self.root,'--mode','accompany');(self.root/'data').mkdir();(self.root/'data/x.txt').write_text('Данные');(self.root/'alias').symlink_to(self.root/'data',target_is_directory=True)
  call('report_workspace.py','checkpoint',self.root,'--mode','accompany','--include','alias/x.txt',code=2)

if __name__=='__main__':unittest.main(verbosity=2)
