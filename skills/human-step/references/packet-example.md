# Adapted historical packet: eight bounded edits

This is a de-identified adaptation of an earlier packet, not a ready assignment or a new execution record. Repository, branch, SHA, dates and personal style defaults are omitted; class/type names are neutralized consistently. Code is a preserved illustrative fragment, not compiled in this candidate. Before actual use obtain the target sources/version and verify every anchor. Use the task/repository language and style. The original literal packet remains private.

Contents: 1. Add a contrast card; 2. Add linear grayscale-correction button; 3. Add nonlinear grayscale-correction button; 4. Make each correction an independent grayscale conversion; 5. Add queue movement in the ViewModel; 6. Add arrows to queue rows; 7. Show histograms on the advanced page too; 8. Remove transformations from the first page

## 1. Add a contrast card

File `Views/EditorWindow.cs`, method `EditorWindow.CreateToolbar()`. After verifying this anchor in the selected source:

```csharp
adjustmentCards.Children.Add(saturationCard);
```

Before `// в правом столбце теперь находится контейнер карточек, а не одна карточка`, insert:

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

Check: clicking twice with different values creates two separate contrast steps. Moving the slider alone does not change the image.

## 2. Add linear grayscale-correction button

File `Views/EditorWindow.cs`, method `EditorWindow.CreateToolbar()`. **Immediately after**:

```csharp
toolsContent.Children.Add(addGrayscaleButton);
```

Insert:

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

Do not call old `ApplyLinearGrayscaleCorrectionButton_OnClick()`; it changes `Settings`. Check: the queue contains “Линейная коррекция ЧБ”.

## 3. Add nonlinear grayscale-correction button

Same file/method. **Immediately after** the newly added line:

```csharp
toolsContent.Children.Add(addLinearCorrectionButton);
```

Insert:

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

Do not call `ApplyNonlinearGrayscaleCorrectionButton_OnClick()` from the old panel. Check: the queue has the second correction type and applies it when saving the advanced result.

## 4. Make each correction an independent grayscale conversion

File `Services/TransformService.cs`, method `TransformService.ApplySteps()`. Find these two branches in `switch (step.Type)`:

```csharp
case TransformKind.LinearGrayscaleCorrection:
    ApplyLinearCorrection(processedImage);
    break;

case TransformKind.NonlinearGrayscaleCorrection:
    ApplyLogarithmicCorrection(processedImage);
    break;
```

Replace **only these branches** with:

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

Do not insert a hidden `TransformStep` into `Steps`. Grayscale conversion belongs inside each correction so removing/reordering adjacent `Grayscale` does not invalidate the step name. Check both corrections on a color image without a separate grayscale step.

## 5. Add queue movement in the ViewModel

File `ViewModels/EditorModel.cs`. Insert **between methods** `RemoveAdvancedStep()` and `AddAdvancedStep()`:

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

Move the actual `TransformStep` object so identically named steps with different parameters stay distinct. Moving the first up or last down must do nothing. Retain `PrepareAdvancedQueue()`; transition from the old page still uses it.

## 6. Add arrows to queue rows

File `Views/EditorWindow.cs`, method `EditorWindow.CreateToolbar()`, `queueList.ItemTemplate`.

**Replace** this line inside `Grid row`:

```csharp
ColumnDefinitions = new ColumnDefinitions("*,Auto"),
```

With:

```csharp
ColumnDefinitions = new ColumnDefinitions("*,Auto,Auto,Auto"),
```

**After** `row.Children.Add(name);` and **before** `Button removeButton = new Button {`, insert:

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

**Replace** the existing line after the minus handler:

```csharp
Grid.SetColumn(removeButton, 1);
```

With:

```csharp
Grid.SetColumn(removeButton, 3);
```

Keep the rest of the minus handler. Check: arrows move their own `step`, updating list/preview. Compare brightness and nonlinear grayscale correction in reversed order.

## 7. Show histograms on the advanced page too

File `Views/EditorWindow.cs`. Use **targeted** edits because one `HistogramPanel` cannot belong to two visual trees.

**7.1. Field.** Immediately after:

```csharp
private readonly HistogramPanel histogramPanel = new HistogramPanel();
```

Insert:

```csharp
private readonly HistogramPanel advancedHistogramPanel = new HistogramPanel();
```

**7.2. Placement.** In `CreateToolbar()`, immediately after:

```csharp
advancedContent.Children.Add(advancedToolsPanel);
```

Insert:

```csharp
// вторая панель показывает ту же пару гистограмм под инструментами
advancedContent.Children.Add(advancedHistogramPanel);
```

**7.3. Initial data.** At the end of `EditorWindow_OnDataContextChanged()`, after:

```csharp
histogramPanel.ShowComparison(histogramViewModel?.HistogramComparison);
```

Insert:

```csharp
advancedHistogramPanel.ShowComparison(histogramViewModel?.HistogramComparison);
```

**7.4. Updates.** In `HistogramViewModel_OnPropertyChanged()`, after:

```csharp
histogramPanel.ShowComparison(viewModel.HistogramComparison);
```

Insert:

```csharp
advancedHistogramPanel.ShowComparison(viewModel.HistogramComparison);
```

Do not move `histogramPanel` from `CreateLayout()`; it remains on the first page. Check advanced histograms after adding, removing, moving, and resetting steps.

## 8. Remove transformations from the first page

File `Views/EditorWindow.cs`. **Replace the entire** `CreateSidebar()` method, from `private TabControl CreateSidebar() {` through its closing brace, with:

```csharp
private Border CreateSidebar() {
    // первая страница показывает сведения об изображении без инструментов обработки
    return CreateScrollablePanel(CreateInformationPanel());
}
```

Keep `workspace.Children.Add(CreateSidebar());` in `CreateLayout()`; `Border` is also a `Control`. Keep `CreateInformationPanel()` and `CreateScrollablePanel()` and retain EXIF.

**In constructor** `EditorWindow()`, find:

```csharp
DataContextChanged += EditorWindow_OnDataContextChanged;
InitializeNumericInputs();
```

Replace with:

```csharp
DataContextChanged += EditorWindow_OnDataContextChanged;
```

`InitializeNumericInputs()` served the old panel's `NumericUpDown` fields. **Do not delete** `EditorWindow.Transformations.cs`, old `EditorWindow.Actions.cs` handlers, or `Settings` yet; cleanup follows verification, and `PrepareAdvancedQueue()` still uses `Settings`. This step changes the visible first page.

Check: first page retains loading, information, EXIF, both images, and histogram but no “Преобразования” tab. Advanced tools/saving still work.

## Return to Codex

Run `dotnet build` and report the result. If GUI is available: open image → enter advanced mode → add contrast/grayscale correction → reorder → delete → save/compare with preview → reset → return to first page → enter again. State GUI unavailability directly.

Do not call these eight steps a complete architecture migration. Old `Settings`, unused legacy panel methods, and long `CreateToolbar()` remain. Removing the old processing path and decomposing the method are separate next tasks; morphology from Practical Work 2 follows them.
