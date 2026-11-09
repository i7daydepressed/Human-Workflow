# Необязательный журнал запуска

Использовать только если проект предусматривает отдельные журналы исполнителей. Скрипт [agent_journal.py](../../scripts/agent_journal.py) создает agent-logs/<run-id>.md и соседний identity.json; он не ведет автоматически ai_work_log.md, impl_notes.md или рабочие заметки.

## Создание

Подготовить JSON с непустыми строками: `agent`, `agent_id`, `id_source`, `model`, `model_source`, `user`, `task`, `skill_version`, `timezone`. Неизвестное обозначить явно, без выдуманной идентичности и ненужных личных данных.

Выполнить `python3 <shared-scripts>/agent_journal.py start <папка-задачи> --identity <identity.json> --language ru`. Сохранить возвращенные run_id и пути. `<shared-scripts>` — абсолютный путь к обязательной папке skills/scripts; папка задачи должна быть вне установки.

## Добавление события

Подготовить JSON: обязательные непустые строки `goal` и `result`; по необходимости `actions`, `files`, `checks`, `user_decision`, `next_step` как строки или массивы строк. Факты готовит агент по реально выполненной работе.

Выполнить `python3 <shared-scripts>/agent_journal.py append <папка-задачи> --run-id <run-id> --entry <entry.json>`. Скрипт дописывает существующий собственный журнал с identity, сохраняя прежние записи. Результат cloud_synced=false не подтверждает синхронизацию.

Основной порядок учета и долговременного сохранения — в [SKILL.md](../SKILL.md). Этот помощник не заменяет общие записи проекта.
