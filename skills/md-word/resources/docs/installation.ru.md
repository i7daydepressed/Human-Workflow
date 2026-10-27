# Установка из одного GitHub-репозитория

[English](installation.en.md). Репозиторий: <https://github.com/i7daydepressed/Human-Workflow>.

Корень репозитория — сам плагин. `.agents/plugins/marketplace.json` и `.claude-plugin/marketplace.json` указывают на него. Техническое имя остаётся `workflow-tools-preview@workflow-tools`, отображаемое — Human Workflow.

## Codex CLI

```bash
codex plugin marketplace add https://github.com/i7daydepressed/Human-Workflow --json
codex plugin add workflow-tools-preview@workflow-tools --json
codex plugin list --marketplace workflow-tools --json
```

## Claude

```bash
claude plugin marketplace add https://github.com/i7daydepressed/Human-Workflow
claude plugin install workflow-tools-preview@workflow-tools
```

В интерфейсе плагинов выбрать Customize → Plugins → Add → Add marketplace и указать ссылку. Доступность зависит от клиента/аккаунта. После установки использовать новую сессию. Сохранить рабочую прежнюю установку и внешний профиль; старый каталог `workflow-preview-i04` — отдельная регистрация.

В I06 все runtime-ресурсы находятся внутри `resources/` каждого скила. Скил не должен требовать соседние папки за пределами копируемого каталога. Перед публикацией разработчик получает эти файлы из общих исходников; пользователю не нужно собирать ZIP. См. [размещение ресурсов](skill-resources.ru.md).

Для проверки установки явно вызвать md-word или human-step и запросить пути действительно прочитанных инструкций. Имя в списке не доказывает чтение и исполнение. Если путь отсутствует, сохранить реальную ошибку и сведения о среде; не восстанавливать workflow молча из описаний или сети. Автоматический выбор проверяется отдельно.

Задачи, журналы, результаты и явно выбранный профиль хранить вне установки/кеша. Помощники запускать по абсолютным путям от корня ресурсов выбранного скила. Инициализация профиля не выбирает оформление или титул. Языки инструкций, результата и журнала независимы. [Профиль](profile.ru.md), [Word](word-preset.ru.md).

Основным помощникам достаточно стандартной библиотеки Python; необязательная сборка титула требует `lxml`. Рендер и шрифты зависят от среды. Доказательства I04 и текущие ограничения описаны в [клиентских проверках](client-checks.ru.md). Локальная изоляция не доказывает реальный прогон Claude или обновление на Mac.
