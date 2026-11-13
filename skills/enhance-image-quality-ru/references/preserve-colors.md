# Стратегия: улучшение с сохранением цветов волос

Применять после выбора этой стратегии в [общем руководстве](enhancement.md). Улучшать качество того же кадра; сохранять существующие цвета волос и остальных областей. Самостоятельно не переключать стратегию по эстетическому предпочтению.

## 1. Подготовить конкретный запрос

1. Выполнить осмотр из [общего руководства](enhancement.md), заполнить [общую карточку наблюдений](observation-card.md) и сохранить ее как card.json в рабочей папке. Взять характеристики из фактически просмотренного исходника; не подменять их выбранным по памяти стилем.
2. Разделить характер контура и внутреннее затенение. Описать видимые цвета и рисунок глаз, тон кожи и светотеневые переходы лица. Для невидимых глаз или лица использовать NOT_VISIBLE по правилам формы.
3. В hair.base_and_existing_colors и hair.preserve_details отметить реальные оттенки, рефлексы, соседние ленты, отделку и неоднозначные полосы. В hair.accent_plan указать NOT_REQUESTED; план акцентов, если он есть для отдельного сравнения, в этой стратегии не попадет в запрос.
4. Сформировать запрос сборщиком; прочитать полученный файл и сопоставить описания с исходником до редактора. Проверка формы не подтверждает визуальную точность.

```bash
python scripts/prepare_request.py /path/to/card.json --strategy preserve-colors --out /path/to/preserve-colors.txt
```

Запускать команду от корня навыка либо использовать фактический абсолютный путь к scripts/prepare_request.py. Выходной файл не перезаписывается; для следующей попытки выбрать новое имя. Для проверки без записи добавить --check-only. Сборщик печатает квитанцию с хешами и длиной текста; эти длины не являются расходом токенов.

## 2. Полный промпт-образец

Указанные ограничения выражают требование; их выполнение проверять по результату. Полнота запроса не доказывает сохранность деталей и не гарантирует улучшения качества.

Заполнять карточку и все поля образца на английском языке. Использовать полный образец через сборщик, который переносит общие наблюдения без пропусков. Самостоятельный образец ниже остается доступен для чтения и разбора.

```text
Edit the supplied image 1 as the sole source and edit target. Improve the quality of this existing frame while preserving its composition and observed rendering style.

SOURCE APPEARANCE
Edge character: {{edge_character}}
Interior shading and material transitions: {{interior_shading}}
Eye visibility, geometry, internal pattern and local colors: {{eye_details}}
Face visibility, skin tones and lighting transitions: {{face_tones}}
Other existing colors and contrasting exceptions: {{other_colors}}
Hair base, existing colors and light reflections: {{hair_base_and_existing_colors}}
Hair details, adjacent materials and ambiguous color bands to preserve: {{hair_preserve_details}}
Identity, expression, pose, scene, crop and source-specific invariants: {{frame_and_identity}}

LOCAL QUALITY TARGET
{{local_improvement}}
Refine the specified existing contours while preserving their position, width and original edge character. Make existing edges continuous and clearly distinguishable where they are distinct in the source. Keep interior shading soft only where it is soft in the source, and preserve existing flat areas and defined facets where those are present.
Preserve the observed local color structure and its placement in the visible eyes and face. Keep existing colored forms, light-to-dark transitions and highlights distinguishable. Do not flatten existing transitions into a uniform pastel fill or add new hues, highlights or ornament.

HAIR OPERATION
Strictly preserve the observed hair colors, their placement within the same locks, existing shadows, highlights and colored light reflections. Do not add new shades or colored strands, remove existing colors, or intensify existing accents. Preserve adjacent ribbons, trim and ornaments separately from the hair. Leave ambiguous color bands unchanged.

SHARED PRESERVATION
Preserve the observed colors of the skin, eyes, clothing, ornaments, objects and background, including small contrasting exceptions. Retain the original lighting direction and color balance. Do not apply a new overall color filter or increase saturation across the whole image.
Preserve the original facial proportions, eye corners, eyelid opening, iris position, gaze, mouth shape, pose, hands and fingers. Preserve visible internal iris patterns, ornament shapes, spacing and occlusions. Do not replace an existing pattern with a similar new design or invent details of a hidden region.
Preserve the hair length, silhouette, fringe, parting and individual lock shapes; garment construction, accessories, objects, background geometry, camera angle, framing and aspect ratio. Keep cropped elements cropped. Do not add, remove or reposition elements.
Do not introduce a new rendering style, glossy finish, global sharpening, heavier outlines or additional texture merely to create an impression of greater detail.
Return one edited full version of this same frame, without captions, labels, a collage or a comparison sheet.
```

Количество результатов брать из поручения; для серии выполнять отдельные обработки, как описано в общем руководстве.

## 3. Адаптировать к исходнику и проверить

| Признак исходника или результата | Прием в запросе | Контроль после обработки |
| --- | --- | --- |
| Мягкий свет при четком контуре | Описать край и внутреннюю растушевку отдельно; сохранять каждый наблюдаемый признак | Контур остался читаемым, мягкие переходы внутри областей сохранились |
| Белые волосы с цветным светом | Сохранить основной цвет и существующее распределение рефлексов | Нет ли новых окрашенных прядей или удаления исходного оттенка |
| Несколько цветов и небольшой контрастный акцент | Перечислить акцент отдельно от основной гаммы | Сохранился ли его собственный цвет |
| Закрытые или прикрытые глаза | Указать фактическое состояние век; при закрытых глазах не описывать видимые радужки | Не открылись ли глаза, не изменились ли взгляд и выражение |
| Сложные радужки или орнамент | Назвать видимые оттенки, их размещение, формы, промежутки и внутренние линии | Отдельно сравнить цветовую структуру, рисунок и геометрию |
| На результате появились новые оттенки | Считать это отклонением выбранной стратегии | Перейти к диагностике и коррекции в общем руководстве |

После обработки вернуться к [сравнению, коррекции и показу результата](enhancement.md). Проверить также области вне перечисленных улучшений.
