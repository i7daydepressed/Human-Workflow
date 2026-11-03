"""Localized generated audit prose; machine keys stay stable."""
MESSAGES = {
    'duplicate_heading': ('Строка {line}: повтор номера заголовка {number}', 'Line {line}: duplicate heading number {number}'),
    'parent_heading': ('Строка {line}: не найден родитель заголовка {number}', 'Line {line}: parent heading not found for {number}'),
    'heading_order': ('Строка {line}: номер {number}, ожидался конец {expected}', 'Line {line}: heading {number}; expected final component {expected}'),
    'introduction': ('Не найдено ненумерованное введение; проверить требования задания', 'No unnumbered introduction found; check task requirements'),
    'next_figure': ('Строка {line}: нет пояснения после рисунка на строке {first}', 'Line {line}: no explanation after the figure at line {first}'),
    'external_image': ('Строка {line}: внешнее изображение требует локальной копии: {target}', 'Line {line}: external image requires a local copy: {target}'),
    'outside_image': ('Строка {line}: изображение вне папки отчета: {target}', 'Line {line}: image is outside the project: {target}'),
    'missing_image': ('Строка {line}: отсутствует {target}', 'Line {line}: missing image {target}'),
    'orphan_caption': ('Строка {line}: подпись без предшествующего рисунка', 'Line {line}: caption without a preceding image'),
    'new_block': ('Строка {line}: новый блок без пояснения после рисунка на строке {first}', 'Line {line}: new block without explanation after the figure at line {first}'),
    'missing_caption': ('Рисунок на строке {first}: подпись не найдена до текста', 'Figure at line {first}: caption missing before the following text'),
    'end_explanation': ('Конец отчета: нет пояснения после рисунка на строке {first}', 'End of report: no explanation after the figure at line {first}'),
    'caption_order': ('Нарушена последовательность подписей: {captions}', 'Caption sequence is invalid: {captions}'),
    'unmatched_caption': ('Есть подписи без распознанной группы изображений', 'Some captions have no recognized image group'),
    'reference_images': ('Есть reference-style изображения: проверить пути вручную', 'Reference-style images require manual path checks'),
    'placeholder': ('Найдена возможная заглушка: {token}', 'Possible placeholder found: {token}'),
}


def message(language, key, **values):
    return MESSAGES[key][1 if language == 'en' else 0].format(**values)
