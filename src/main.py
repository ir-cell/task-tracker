"""Первый рабочий сценарий: добавление задачи и просмотр списка."""

from datetime import date

from src.storage import TaskStorage
from src.models import Task


PRIORITIES = ["Низкий", "Средний", "Высокий"]
STAGES = ["Анализ", "Разработка", "Тестирование", "Внедрение"]
STATUSES = ["Новая", "В работе", "Выполнена"]


def validate_title(title):
    """Проверить название задачи."""
    if not title or not title.strip():
        return "Ошибка: название задачи не может быть пустым"
    if len(title) > 100:
        return "Ошибка: название длиннее 100 символов"
    return None


def validate_date(date_str):
    """Проверить дату в формате ГГГГ-ММ-ДД."""
    try:
        year, month, day = map(int, date_str.split("-"))
        date(year, month, day)
        return None
    except (ValueError, AttributeError):
        return "Ошибка: дата должна быть в формате ГГГГ-ММ-ДД (например, 2026-10-05)"


def ask_choice(prompt, options):
    """Спросить у пользователя выбор из списка."""
    print(f"{prompt} ({', '.join(options)})")
    while True:
        value = input("> ").strip()
        if value in options:
            return value
        print(f"Ошибка: выберите одно из: {', '.join(options)}")


def add_task_interactive(storage):
    """Диалог добавления задачи."""
    print("\n=== Добавление задачи ===\n")

    title = input("Название задачи: ").strip()
    error = validate_title(title)
    if error:
        print(error)
        return

    assignee = input("Исполнитель: ").strip()
    if not assignee:
        print("Ошибка: укажите исполнителя")
        return

    priority = ask_choice("Приоритет", PRIORITIES)
    stage = ask_choice("Этап", STAGES)

    due_date = input("Срок (ГГГГ-ММ-ДД): ").strip()
    error = validate_date(due_date)
    if error:
        print(error)
        return

    task = Task(
        task_id=storage.next_id(),
        title=title,
        assignee=assignee,
        priority=priority,
        stage=stage,
        due_date=due_date,
    )
    storage.add(task)
    print(f"\n✓ Задача «{task.title}» добавлена")


def show_tasks(storage):
    """Показать список всех задач."""
    tasks = storage.get_all()
    print("\n=== Список задач ===\n")

    if not tasks:
        print("Задач пока нет.")
        return

    for t in tasks:
        overdue = " [ПРОСРОЧЕНА]" if t.is_overdue() else ""
        print(f"{t.id}. {t.title}")
        print(f"   Исполнитель: {t.assignee}")
        print(f"   Приоритет: {t.priority} | Этап: {t.stage}")
        print(f"   Срок: {t.due_date} | Статус: {t.status}{overdue}")
        print()


def show_overdue(storage):
    """Показать только просроченные задачи."""
    tasks = [t for t in storage.get_all() if t.is_overdue()]
    print("\n=== Просроченные задачи ===\n")

    if not tasks:
        print("Просроченных задач нет.")
        return

    for t in tasks:
        print(f"{t.id}. {t.title}")
        print(f"   Исполнитель: {t.assignee}")
        print(f"   Срок: {t.due_date} | Статус: {t.status}")
        print()


def main():
    """Главное меню."""
    storage = TaskStorage()

    while True:
        print("\n--- Учёт задач команды ---")
        print("1. Добавить задачу")
        print("2. Показать все задачи")
        print("3. Показать просроченные задачи")
        print("0. Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == "1":
            add_task_interactive(storage)
        elif choice == "2":
            show_tasks(storage)
        elif choice == "3":
            show_overdue(storage)
        elif choice == "0":
            print("До встречи!")
            break
        else:
            print("Ошибка: выберите 1, 2, 3 или 0")


if __name__ == "__main__":
    main()