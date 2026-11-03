# Адаптированный исторический пакет: восемь точных правок

Это обезличенная адаптация прежнего пакета, не готовое поручение и не новый отчет исполнения. Репозиторий, ветка, SHA, даты и личные стилевые настройки исключены; классы/типы переименованы согласованно. Код — сохраненный иллюстративный фрагмент, он не компилировался в этом кандидате. Перед реальным применением получить исходники/версию задачи и проверить каждый якорь. Использовать язык и стиль задачи/репозитория. Оригинальный буквальный пакет остается приватным.

Содержание: 1. Добавить карточку контрастности; 2. Добавить кнопку линейной коррекции ЧБ; 3. Добавить кнопку нелинейной коррекции ЧБ; 4. Сделать каждый шаг коррекции самостоятельным ЧБ-преобразованием; 5. Добавить перемещение элемента очереди во ViewModel; 6. Добавить стрелки в строку очереди; 7. Показать гистограммы и на расширенной странице; 8. Убрать элементы преобразования с первой страницы

## 1. Добавить карточку контрастности

Файл `Views/EditorWindow.cs`, метод `EditorWindow.CreateToolbar()`. После проверки якоря в выбранном исходнике:

```csharp
adjustmentCards.Children.Add(saturationCard);
```

и до строки `// в правом столбце теперь находится контейнер карточек, а не одна карточка` вставь:

```csharp
// карточка контрастности выбирает значение для нового шага очереди
StackPanel contrastControls = new StackPanel {
    Spacing = 8
};
contrastControls.Children.Add(new TextBlock {
    Text = "Контрастность",
    FontWeight = FontWeight.SemiBold
});

Slider contrastSlider = new Slider {
    Width = 260,
    Minimum = -100,
    Maximum = 100,
    Value = 20,
    TickFrequency = 1,
    IsSnapToTickEnabled = true
};

TextBlock contrastValueText = new TextBlock();
contrastValueText.Bind(
    TextBlock.TextProperty,
    new Binding("Value") {
        Source = contrastSlider,
        StringFormat = "Текущее значение: {0:0}"
    });
contrastControls.Children.Add(contrastValueText);
contrastControls.Children.Add(contrastSlider);

Button addContrastButton = new Button {
    Content = "Добавить контрастность",
    HorizontalAlignment = HorizontalAlignment.Right
};
addContrastButton.Click += (_, _) => {
    if (DataContext is EditorModel viewModel) {
        // берем значение ползунка при нажатии и добавляем его в конец очереди
        viewModel.AddAdvancedStep(
            TransformKind.Contrast,
            contrastSlider.Value);
    }
};
contrastControls.Children.Add(addContrastButton);

Border contrastCard = new Border {
    Padding = new Thickness(12),
    BorderBrush = Brushes.Gray,
    BorderThickness = new Thickness(1),
    CornerRadius = new CornerRadius(6),
    HorizontalAlignment = HorizontalAlignment.Left,
    Child = contrastControls
};
adjustmentCards.Children.Add(contrastCard);
```

Проверка: два нажатия с разными значениями создают два отдельных шага контрастности. Значение на ползунке само по себе изображение не меняет.

## 2. Добавить кнопку линейной коррекции ЧБ

Файл `Views/EditorWindow.cs`, метод `EditorWindow.CreateToolbar()`. **Сразу после** строки:

```csharp
toolsContent.Children.Add(addGrayscaleButton);
```

вставь:

```csharp
// линейная коррекция добавляется как отдельный шаг после уже выбранных действий
Button addLinearCorrectionButton = new Button {
    Content = "Добавить линейную коррекцию ЧБ",
    HorizontalAlignment = HorizontalAlignment.Left
};
addLinearCorrectionButton.Click += (_, _) => {
    if (DataContext is EditorModel viewModel) {
        viewModel.AddAdvancedStep(TransformKind.LinearGrayscaleCorrection);
    }
};
toolsContent.Children.Add(addLinearCorrectionButton);
```

Не вызывай старый `ApplyLinearGrayscaleCorrectionButton_OnClick()`: он меняет `Settings`. Проверка: в очереди появляется строка «Линейная коррекция ЧБ».

## 3. Добавить кнопку нелинейной коррекции ЧБ

Тот же файл и метод. **Сразу после** новой строки:

```csharp
toolsContent.Children.Add(addLinearCorrectionButton);
```

вставь:

```csharp
// нелинейная коррекция тоже становится отдельным шагом очереди
Button addNonlinearCorrectionButton = new Button {
    Content = "Добавить нелинейную коррекцию ЧБ",
    HorizontalAlignment = HorizontalAlignment.Left
};
addNonlinearCorrectionButton.Click += (_, _) => {
    if (DataContext is EditorModel viewModel) {
        viewModel.AddAdvancedStep(TransformKind.NonlinearGrayscaleCorrection);
    }
};
toolsContent.Children.Add(addNonlinearCorrectionButton);
```

Не вызывай `ApplyNonlinearGrayscaleCorrectionButton_OnClick()` из старой панели. Проверка: у очереди появился второй вид коррекции и при сохранении расширенного результата он применяется.

## 4. Сделать каждый шаг коррекции самостоятельным ЧБ-преобразованием

Файл `Services/TransformService.cs`, метод `TransformService.ApplySteps()`. Найди в `switch (step.Type)` эти две ветви:

```csharp
case TransformKind.LinearGrayscaleCorrection:
    ApplyLinearCorrection(processedImage);
    break;

case TransformKind.NonlinearGrayscaleCorrection:
    ApplyLogarithmicCorrection(processedImage);
    break;
```

Замени **только эти ветви** на:

```csharp
case TransformKind.LinearGrayscaleCorrection:
    // коррекция сначала переводит текущий результат в серый
    ConvertToGrayscale(processedImage);
    ApplyLinearCorrection(processedImage);
    break;

case TransformKind.NonlinearGrayscaleCorrection:
    // шаг работает и без отдельного действия градаций серого в очереди
    ConvertToGrayscale(processedImage);
    ApplyLogarithmicCorrection(processedImage);
    break;
```

Не вставляй дополнительный скрытый `TransformStep` в `Steps`. Преобразование в серый является частью каждого шага коррекции, так что удаление или перестановка соседнего `Grayscale` не меняет смысл названия шага. Проверь обе коррекции на цветном изображении без отдельного шага градаций серого.

## 5. Добавить перемещение элемента очереди во ViewModel

Файл `ViewModels/EditorModel.cs`. **Между методами** `RemoveAdvancedStep()` и `AddAdvancedStep()` вставь:

```csharp
// меняет положение шага и заново применяет очередь в новом порядке
public void MoveAdvancedStep(TransformStep? step, int offset) {
    if (step is null || (offset != -1 && offset != 1)) {
        return;
    }

    int oldIndex = Steps.IndexOf(step);
    int newIndex = oldIndex + offset;

    if (oldIndex < 0 || newIndex < 0 || newIndex >= Steps.Count) {
        return;
    }

    Steps.Move(oldIndex, newIndex);
    advancedQueueCustomized = true;
    ApplyAdvancedQueue();
}
```

Метод двигает сам объект `TransformStep`, поэтому одинаково названные шаги с разными параметрами не перепутаются. Для первого шага вверх и для последнего вниз ничего не должно происходить. Существующий `PrepareAdvancedQueue()` пока оставь: он еще используется при переходе со старой страницы.

## 6. Добавить стрелки в строку очереди

Файл `Views/EditorWindow.cs`, метод `EditorWindow.CreateToolbar()`, шаблон `queueList.ItemTemplate`.

**Замени** строку внутри `Grid row`:

```csharp
ColumnDefinitions = new ColumnDefinitions("*,Auto"),
```

на:

```csharp
ColumnDefinitions = new ColumnDefinitions("*,Auto,Auto,Auto"),
```

**После** существующей строки `row.Children.Add(name);` и **перед** `Button removeButton = new Button {` вставь:

```csharp
Button moveUpButton = new Button {
    Content = "↑",
    MinWidth = 28
};
moveUpButton.Click += (_, _) => {
    if (DataContext is EditorModel viewModel) {
        viewModel.MoveAdvancedStep(step, -1);
    }
};
Grid.SetColumn(moveUpButton, 1);
row.Children.Add(moveUpButton);

Button moveDownButton = new Button {
    Content = "↓",
    MinWidth = 28
};
moveDownButton.Click += (_, _) => {
    if (DataContext is EditorModel viewModel) {
        viewModel.MoveAdvancedStep(step, 1);
    }
};
Grid.SetColumn(moveDownButton, 2);
row.Children.Add(moveDownButton);
```

**Замени** существующую строку после обработчика минуса:

```csharp
Grid.SetColumn(removeButton, 1);
```

на:

```csharp
Grid.SetColumn(removeButton, 3);
```

Остальной обработчик минуса не меняй. Проверка: стрелки перемещают тот `step`, у которого они расположены; список и предпросмотр обновляются. Для наглядного сравнения поменяй порядок яркости и нелинейной коррекции ЧБ.

## 7. Показать гистограммы и на расширенной странице

Файл `Views/EditorWindow.cs`. Здесь несколько **точечных** правок одного класса, потому что `HistogramPanel` нельзя помещать одновременно в два визуальных дерева.

**7.1. Поле.** Сразу после:

```csharp
private readonly HistogramPanel histogramPanel = new HistogramPanel();
```

вставь:

```csharp
private readonly HistogramPanel advancedHistogramPanel = new HistogramPanel();
```

**7.2. Размещение.** В `CreateToolbar()` сразу после:

```csharp
advancedContent.Children.Add(advancedToolsPanel);
```

вставь:

```csharp
// вторая панель показывает ту же пару гистограмм под инструментами
advancedContent.Children.Add(advancedHistogramPanel);
```

**7.3. Первичная передача данных.** В конце `EditorWindow_OnDataContextChanged()` после существующей строки:

```csharp
histogramPanel.ShowComparison(histogramViewModel?.HistogramComparison);
```

вставь:

```csharp
advancedHistogramPanel.ShowComparison(histogramViewModel?.HistogramComparison);
```

**7.4. Обновление.** В `HistogramViewModel_OnPropertyChanged()` после:

```csharp
histogramPanel.ShowComparison(viewModel.HistogramComparison);
```

вставь:

```csharp
advancedHistogramPanel.ShowComparison(viewModel.HistogramComparison);
```

Не переносить `histogramPanel` из `CreateLayout()`: он остается на первой странице. Проверка: на расширенной странице гистограммы обновляются после добавления, удаления, перемещения и сброса шагов.

## 8. Убрать элементы преобразования с первой страницы

Файл `Views/EditorWindow.cs`. **Замени целиком** текущий метод `CreateSidebar()` (от `private TabControl CreateSidebar() {` до закрывающей скобки этого метода) на:

```csharp
private Border CreateSidebar() {
    // первая страница показывает сведения об изображении без инструментов обработки
    return CreateScrollablePanel(CreateInformationPanel());
}
```

Вызов `workspace.Children.Add(CreateSidebar());` в `CreateLayout()` не меняй: `Border` тоже является `Control`. Методы `CreateInformationPanel()` и `CreateScrollablePanel()` не меняй, EXIF должен остаться.

**В конструкторе** `EditorWindow()` найди:

```csharp
DataContextChanged += EditorWindow_OnDataContextChanged;
InitializeNumericInputs();
```

и замени на:

```csharp
DataContextChanged += EditorWindow_OnDataContextChanged;
```

`InitializeNumericInputs()` обслуживал поля `NumericUpDown` старой панели. Файл `EditorWindow.Transformations.cs`, старые обработчики в `EditorWindow.Actions.cs` и `Settings` пока **не удаляй**: это отдельная чистка после проверки, и `PrepareAdvancedQueue()` все еще обращается к `Settings`. В этом шаге меняется именно видимая первая страница.

Проверка: на первой странице есть загрузка, информация, EXIF, обе картинки и гистограмма, но нет вкладки «Преобразования»; в расширенном режиме инструменты и сохранение продолжают работать.

## Итог для Codex

Выполни `dotnet build` и приведи результат. Если можешь запустить GUI, пройди цепочку: открыть изображение → перейти в расширенный режим → добавить контрастность и коррекцию ЧБ → поменять порядок → удалить шаг → сохранить и сравнить с предпросмотром → сбросить очередь → вернуться на первую страницу → войти снова. Если GUI недоступен, прямо укажи это.

Не выдавай эти восемь шагов за полный перенос архитектуры: после них старый `Settings` и неиспользуемые методы прежней панели еще остаются в коде, а `CreateToolbar()` остается длинным. Следующей отдельной задачей станут удаление старого пути обработки и декомпозиция метода; затем можно перейти к морфологии из Практической работы №2.
