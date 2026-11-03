#!/usr/bin/env python3
"""Validate accepted cases and build an index from recorded ratings and scales."""
import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sys
from safe_paths import destination, external_path


def score(value):
    if not isinstance(value, str):
        raise ValueError('Числовая оценка должна быть строкой, а не float')
    try:
        number = Decimal(value.replace(',', '.'))
    except InvalidOperation as exc:
        raise ValueError('Оценка не является числом') from exc
    if not number.is_finite():
        raise ValueError('Оценка должна быть конечной')
    return number


def display(rating):
    if rating is None:
        return 'не сообщена'
    return rating.get('display', rating.get('value', '').replace('.', ','))


def validate_rating(rating, *, role, schema, scales, cid):
    if not isinstance(rating, dict):
        raise ValueError(f'{cid}: оценка должна быть объектом либо null')
    value = score(rating.get('value'))
    if not rating.get('quote'):
        raise ValueError(f'{cid}: у оценки нет исходного сообщения')
    if role == 'user':
        if rating.get('kind') not in ['user_report_rating', 'user_work_rating']:
            raise ValueError(f'{cid}: пользовательская и преподавательская оценки различаются')
        if not all(rating.get(k) for k in (['rater', 'source', 'date'] if schema == 1 else ['rater', 'source'])):
            raise ValueError(f'{cid}: у пользовательской оценки отсутствует происхождение')
    elif rating.get('source') != 'teacher_reported_by_user':
        raise ValueError(f'{cid}: преподавательская оценка без отдельного источника')
    if schema == 2:
        if not rating.get('scope') or not rating.get('rater'):
            raise ValueError(f'{cid}: нужны объект оценки и оценивающий')
        if not (rating.get('date') or rating.get('reported_date')):
            raise ValueError(f'{cid}: нужна дата оценки либо дата сообщения о ней')
        if role == 'teacher' and rating.get('kind') not in ['teacher_work_rating', 'teacher_report_rating', 'teacher_official_grade']:
            raise ValueError(f'{cid}: неизвестный вид преподавательской оценки')
        if role == 'teacher' and not rating.get('source_ref'):
            raise ValueError(f'{cid}: у преподавательской оценки нет ссылки на источник сообщения')
    if score(display(rating)) != value:
        raise ValueError(f'{cid}: display противоречит value')
    scale_id = rating.get('scale_id')
    if scale_id is not None and scale_id not in scales:
        raise ValueError(f'{cid}: неизвестная шкала {scale_id}')
    scale = scales.get(scale_id, {})
    for bound, comparison in [('min', lambda x, y: x < y), ('max', lambda x, y: x > y)]:
        own = rating.get(f'scale_{bound}')
        shared = scale.get(bound)
        if own is not None and shared is not None and score(own) != score(shared):
            raise ValueError(f'{cid}: противоречащие границы шкалы')
        limit = own if own is not None else shared
        if limit is not None and comparison(value, score(limit)):
            raise ValueError(f'{cid}: оценка вне явно заданной границы шкалы')


def load(path):
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema_version') not in [1, 2] or not isinstance(data.get('cases'), list):
        raise ValueError('Нужны schema_version=1 или 2 и cases[]')
    schema = data['schema_version']
    scales = data.get('scales', {})
    if not isinstance(scales, dict):
        raise ValueError('scales должен быть объектом')
    for sid, scale in scales.items():
        if not isinstance(scale, dict):
            raise ValueError(f'{sid}: шкала должна быть объектом')
        for key in ['baseline', 'min', 'max']:
            if scale.get(key) is not None:
                score(scale[key])
        if scale.get('kind') == 'relative_preference':
            if scale.get('baseline') is None or not scale.get('source') or not scale.get('date'):
                raise ValueError(f'{sid}: у шкалы предпочтительности нет основания')
            if scale.get('higher_is_preferred') is not True:
                raise ValueError(f'{sid}: не задано направление предпочтительности')
    ids = set()
    for case in data['cases']:
        if not isinstance(case, dict):
            raise ValueError('Кейс должен быть объектом')
        cid = case.get('id')
        if not isinstance(cid, str) or not cid or cid in ids:
            raise ValueError('ID кейса пустой или повторяется')
        ids.add(cid)
        relative = case.get('case_file')
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
            raise ValueError(f'{cid}: нужен относительный путь MD-кейса')
        target = (path.parent / relative).resolve()
        if not target.is_relative_to(path.parent.resolve()) or not target.is_file():
            raise ValueError(f'{cid}: MD-кейс отсутствует или выходит за папку')
        acceptance = case.get('acceptance', {})
        if acceptance.get('status') != 'user_confirmed' or not acceptance.get('quote'):
            raise ValueError(f'{cid}: нет явного подтверждения сдачи')
        first_lines = '\n'.join(target.read_text(encoding='utf-8').splitlines()[:24])
        for role, key in [('user', 'user_rating'), ('teacher', 'teacher_grade')]:
            rating = case.get(key)
            if rating is None:
                continue
            validate_rating(rating, role=role, schema=schema, scales=scales, cid=cid)
            if role == 'user' and rating['kind'] == 'user_report_rating':
                headings = [f'Текущая оценка отчета пользователем: **{display(rating)}**',
                            f'Current user report rating: **{display(rating)}**']
                if not any(heading in first_lines for heading in headings):
                    raise ValueError(f'{cid}: шапка MD не совпадает с пользовательской оценкой')
            if role == 'teacher' and schema == 2:
                headings = [f'Оценка преподавателя со слов пользователя: **{display(rating)}**',
                            f'Teacher rating reported by the user: **{display(rating)}**']
                if not any(heading in first_lines for heading in headings):
                    raise ValueError(f'{cid}: шапка MD не совпадает с преподавательской оценкой')
    return data


def index(data, language='ru'):
    if language == 'en':
        return english_index(data)
    snapshot = data.get('catalog_role') == 'version_snapshot'
    title = '# Снимок принятых работ и оценок' if snapshot else '# Принятые работы и оценки'
    lines = [title, '']
    if snapshot:
        lines += [f"Снимок выпуска {data.get('skill_version', 'версия не указана')} на {data.get('as_of', 'дату не указали')}. Новые сведения вести в согласованном общем каталоге; этот снимок не является автоматически обновляемым реестром.", '']
    for sid, scale in data.get('scales', {}).items():
        if scale.get('kind') == 'relative_preference':
            baseline = scale['baseline'].replace('.', ',')
            maximum = scale.get('max')
            end = f"Максимум: {maximum}." if maximum is not None else 'Максимум не задан.'
            lines += [f'Шкала {sid}: {baseline} – нормальный результат; выше – предпочтительнее, ниже – менее предпочтительно. {end}', '']
    if any(r and not r.get('scale_id') for c in data['cases'] for r in [c.get('user_rating'), c.get('teacher_grade')]):
        lines += ['Для оценок без указанной шкалы ее смысл и границы неизвестны; не нормализовать их.', '']
    lines += ['Оценки разных авторов, факт приемки и проверки результата учитываются отдельно. Числа не являются процентами и не объясняют причины качества.', '',
              '| Кейс | Пользователь | Преподаватель со слов пользователя | Подтверждение сдачи | Когда полезен |',
              '| --- | --- | --- | --- | --- |']
    for case in data['cases']:
        title = case['title'].replace('|', '\\|')
        useful = case.get('use_for', '').replace('|', '\\|')
        accepted = case['acceptance'].get('date') or 'дата неизвестна'
        target = case.get('case_url') or case['case_file']
        lines.append(f"| [{title}]({target}) | {display(case.get('user_rating'))} | {display(case.get('teacher_grade'))} | {accepted} – со слов пользователя | {useful} |")
    lines += ['', 'Источники оценок, объекты оценки и история уточнений: ratings.json. Выбирать пример по требованиям и подтвержденным свойствам; высокий балл не делает его обязательным шаблоном.']
    if data.get('canonical_catalog'):
        lines += ['', f"Актуальный общий каталог: {data['canonical_catalog']}."]
    return '\n'.join(lines) + '\n'


def english_index(data):
    snapshot = data.get('catalog_role') == 'version_snapshot'
    lines = ['# Accepted work and ratings' + (' — release snapshot' if snapshot else ''), '']
    if snapshot:
        lines += [f"Release snapshot: {data.get('skill_version', 'unknown')}; as of {data.get('as_of', 'unknown')}. New observations belong to the selected current catalog.", '']
    for sid, scale in data.get('scales', {}).items():
        if scale.get('kind') == 'relative_preference':
            maximum = f"Maximum: {scale['max']}." if scale.get('max') is not None else 'No maximum specified.'
            lines += [f"Scale {sid}: {scale['baseline']} means a normal result; higher is preferred, lower is less preferred. {maximum}", '']
    if any(r and not r.get('scale_id') for c in data['cases'] for r in [c.get('user_rating'), c.get('teacher_grade')]):
        lines += ['An unspecified scale has unknown meaning and bounds; do not normalize it.', '']
    lines += ['Raters, acceptance, and checks are separate. Values are not percentages or a causal explanation of quality.', '',
              '| Case | User | Teacher reported by user | Acceptance | Use for |',
              '| --- | --- | --- | --- | --- |']
    def value(rating):
        return rating['value'] if rating is not None else 'not reported'
    for case in data['cases']:
        title = case['title'].replace('|', '\\|')
        useful = case.get('use_for', '').replace('|', '\\|')
        date = case['acceptance'].get('date') or 'date unknown'
        target = case.get('case_url') or case['case_file']
        lines.append(f"| [{title}]({target}) | {value(case.get('user_rating'))} | {value(case.get('teacher_grade'))} | {date} — reported by user | {useful} |")
    lines += ['', 'Sources, scopes, and clarification history: ratings.json. Select examples by requirements and verified properties.']
    if data.get('canonical_catalog'):
        lines += ['', f"Current catalog: {data['canonical_catalog']}."]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate', 'index'])
    parser.add_argument('catalog', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--language', choices=['ru', 'en'], default='ru')
    args = parser.parse_args()
    try:
        data = load(args.catalog.resolve())
        if args.command == 'index':
            result = index(data, args.language)
            if args.out:
                external_path(args.out, __file__)
                output = destination(args.out.expanduser().parent.resolve(), args.out.name)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(result, encoding='utf-8')
            else:
                print(result, end='')
        else:
            print(json.dumps({'valid': True, 'cases': len(data['cases']), 'schema_version': data['schema_version']}, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
