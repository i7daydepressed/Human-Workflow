# Стратегия: улучшение с согласованием цветов волос

Применять после разрешения цветовых акцентов в [общем руководстве](enhancement.md). Улучшать качество того же кадра и менять цвет внутри существующих прядей. Основной цвет волос сохранять; цвета остальных областей сохранять так же, как в стратегии без изменения волос.

## 1. Подготовить карту изменения волос

1. Выполнить осмотр из [общего руководства](enhancement.md), заполнить [общую карточку наблюдений](observation-card.md) и сохранить card.json в рабочей папке. Общие наблюдения для глаз, лица, контуров и заливок заполнять с той же подробностью, что в сохранении цветов.
2. Описать основной цвет волос, существующие оттенки, тени и рефлексы в hair.base_and_existing_colors. Отделить волосы от лент, отделки и украшений; перечислить сохраняемые исключения и неоднозначные полосы в hair.preserve_details.
3. В hair.accent_plan записать фактический план: выбранный оттенок, его видимый источник в одежде, аксессуаре или глазах и место внутри существующих локонов. Фон и сценический свет сами по себе новую палитру не задают. Не переносить оттенки из другого изображения или прошлой задачи.
4. Сохранить доминирование основного цвета, существующую геометрию и интенсивность имеющихся акцентов. Если данных для выбора недостаточно, уточнить конкретный недостающий ориентир до редактирования.
5. Сформировать запрос сборщиком, прочитать его и сопоставить с исходником. Проверка формы не подтверждает визуальную точность наблюдений или надежность выбора акцентов.

| Что определить для волос | Куда записать |
| --- | --- |
| Доминирующая основа, существующие оттенки и рефлексы | hair.base_and_existing_colors |
| Сохраняемые акценты, соседние материалы и неясные полосы | hair.preserve_details |
| Новый акцент, видимый источник оттенка и размещение внутри локона | hair.accent_plan |

```bash
python scripts/prepare_request.py /path/to/card.json --strategy harmonize-hair --out /path/to/harmonize-hair.txt
```

Запускать команду от корня навыка либо использовать фактический абсолютный путь к scripts/prepare_request.py. Для проверки без записи добавить --check-only. Требуется настоящий план акцентов; NOT_REQUESTED для этой стратегии не подходит. Выходной файл не перезаписывается. Квитанция содержит хеши и длины текста, а не расход токенов.

## 2. Полный промпт-образец

Карта выбора оттенков должна опираться на текущий исходник. Ограничения образца выражают требование; их выполнение проверять по результату. Удачный подбор акцентов не доказывает сохранность других деталей.

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
Preserve the observed dominant hair color and its existing lighting. Add only the following restrained color accents within existing locks: {{hair_accent_plan}}
Keep the main hair color visually dominant. Follow the original shadows, highlights and lighting direction; preserve existing light reflections and stated exceptions without automatically intensifying them. Do not recolor neighboring ribbons, trim or ornaments, change lock geometry, or replace the main color with an accent. Leave ambiguous color bands unchanged.

SHARED PRESERVATION
Preserve the observed colors of the skin, eyes, clothing, ornaments, objects and background, including small contrasting exceptions. Retain the original lighting direction and color balance. Do not apply a new overall color filter or increase saturation across the whole image.
Preserve the original facial proportions, eye corners, eyelid opening, iris position, gaze, mouth shape, pose, hands and fingers. Preserve visible internal iris patterns, ornament shapes, spacing and occlusions. Do not replace an existing pattern with a similar new design or invent details of a hidden region.
Preserve the hair length, silhouette, fringe, parting and individual lock shapes; garment construction, accessories, objects, background geometry, camera angle, framing and aspect ratio. Keep cropped elements cropped. Do not add, remove or reposition elements.
Do not introduce a new rendering style, glossy finish, global sharpening, heavier outlines or additional texture merely to create an impression of greater detail.
Return one edited full version of this same frame, without captions, labels, a collage or a comparison sheet.
```

Количество результатов брать из поручения; для серии выполнять отдельные обработки, как описано в общем руководстве.

## 3. Адаптировать акценты и проверить

| Условие | Прием | Контроль после обработки |
| --- | --- | --- |
| Основной цвет волос светлый | Сохранить светлую основу; разместить акценты внутри выбранных существующих прядей | Не стали ли волосы преимущественно цветом акцента |
| Акценты уже есть | Указать их как сохраняемые; отдельно назвать разрешенное добавление | Нет ли автоматического усиления всех полос и теней |
| Цветная полоса соседствует с украшением | Разделить материал волос и аксессуар; неясную полосу сохранить | Не перекрасились ли ленты, отделка и соседние пряди |
| Свет фона отличается от гаммы костюма | Брать ориентиры из персонажа; исходные рефлексы сохранить | Не превратился ли фоновой свет в новую доминирующую окраску |
| Четкие контуры сочетаются с мягким светом или сложными глазами | Заполнить отдельные поля контура, заливок, цветов глаз и лица | Проверить читаемость края, цветовые переходы, рисунок и геометрию независимо от волос |
| Результат изменил одежду, кожу или форму локонов | Считать это отклонением, а не частью согласования | Перейти к диагностике и коррекции в общем руководстве |

После обработки вернуться к [сравнению, коррекции и показу результата](enhancement.md). Сопоставить выбранную карту с фактическим размещением акцентов и проверить остальные области.
