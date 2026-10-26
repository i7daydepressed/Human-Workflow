"""Generate independent parser fixtures, never copy a user's case catalog."""
import json
from pathlib import Path


def write_catalog(root, language='ru'):
    root = Path(root)
    cases = []
    for number, value in enumerate(['1.4', '0.95'], 1):
        display = value.replace('.', ',') if language == 'ru' else value
        user = {'kind': 'user_report_rating', 'value': value, 'display': display,
                'rater': 'test-user', 'scope': 'report', 'source': 'fixture:user',
                'quote': 'Synthetic rating message', 'date': '2000-01-02',
                'scale_id': 'sample-relative-v1'}
        teacher = None
        if number == 1:
            teacher = {'kind': 'teacher_work_rating', 'value': '1.3',
                       'display': '1,3' if language == 'ru' else '1.3',
                       'rater': 'test-teacher', 'scope': 'whole work',
                       'source': 'teacher_reported_by_user', 'source_ref': 'fixture:clarification',
                       'quote': 'Synthetic report of a teacher rating', 'date': None,
                       'reported_date': '2000-01-03', 'scale_id': None}
        name = f'case-{number:03d}.md'
        headings = ((f'Текущая оценка отчета пользователем: **{display}**',
                     'Оценка преподавателя со слов пользователя: **1,3**') if language == 'ru' else
                    (f'Current user report rating: **{display}**',
                     'Teacher rating reported by the user: **1.3**'))
        text = f'# Synthetic case {number}\n\n{headings[0]}\n\n'
        if teacher:
            text += headings[1] + '\n\n'
        text += 'Synthetic parser fixture. No real submission or acceptance is claimed.\n'
        (root / name).write_text(text, encoding='utf-8')
        cases.append({'id': f'case-{number:03d}', 'title': f'Synthetic case {number}',
                      'case_file': name, 'user_rating': user, 'teacher_grade': teacher,
                      'acceptance': {'status': 'user_confirmed', 'quote': 'Synthetic acceptance message', 'date': None},
                      'use_for': 'Parser regression only', 'rating_history': []})
    data = {'schema_version': 2, 'synthetic': True,
            'scales': {'sample-relative-v1': {'kind': 'relative_preference', 'baseline': '1',
                       'min': None, 'max': None, 'higher_is_preferred': True,
                       'source': 'fixture:scale-definition', 'date': '2000-01-03'}},
            'cases': cases}
    path = root / 'ratings.json'
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path
