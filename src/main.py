"""Учёт задач команды разработки."""

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


def ask_id(prompt="Введите ID задачи: "):
    """Спросить у пользователя ID."""
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите число")


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


def print_tasks(tasks):
    """Напечатать список задач."""
    if not tasks:
        print("Задач не найдено.")
        return

    for t in tasks:
        overdue = " [ПРОСРОЧЕНА]" if t.is_overdue() else ""
        print(f"{t.id}. {t.title}")
        print(f"   Исполнитель: {t.assignee}")
        print(f"   Приоритет: {t.priority} | Этап: {t.stage}")
        print(f"   Срок: {t.due_date} | Статус: {t.status}{overdue}")
        print()


def show_tasks(storage):
    """Показать список всех задач."""
    print("\n=== Список задач ===\n")
    print_tasks(storage.get_all())


def show_overdue(storage):
    """Показать только просроченные задачи."""
    tasks = [t for t in storage.get_all() if t.is_overdue()]
    print("\n=== Просроченные задачи ===\n")
    print_tasks(tasks)


def filter_tasks(storage):
    """Фильтрация задач по разным полям."""
    print("\n=== Фильтрация задач ===")
    print("Оставьте поле пустым, чтобы не фильтровать.\n")

    assignee = input("Исполнитель: ").strip()
    priority = input("Приоритет: ").strip()
    stage = input("Этап: ").strip()
    status = input("Статус: ").strip()

    tasks = storage.get_all()

    if assignee:
        tasks = [t for t in tasks if t.assignee.lower() == assignee.lower()]
    if priority:
        tasks = [t for t in tasks if t.priority.lower() == priority.lower()]
    if stage:
        tasks = [t for t in tasks if t.stage.lower() == stage.lower()]
    if status:
        tasks = [t for t in tasks if t.status.lower() == status.lower()]

    print(f"\n=== Найдено задач: {len(tasks)} ===\n")
    print_tasks(tasks)


def search_tasks(storage):
    """Поиск задач по части названия."""
    query = input("\nВведите часть названия: ").strip()
    if not query:
        print("Ошибка: пустой запрос")
        return

    tasks = [t for t in storage.get_all() if query.lower() in t.title.lower()]
    print(f"\n=== Найдено задач: {len(tasks)} ===\n")
    print_tasks(tasks)


def edit_task(storage):
    """Изменение задачи по ID."""
    task_id = ask_id("\nВведите ID задачи для изменения: ")
    task = storage.get_by_id(task_id)

    if not task:
        print(f"Ошибка: задачи с ID {task_id} не существует")
        return

    print(f"\n=== Изменение задачи «{task.title}» ===")
    print("Оставьте поле пустым, чтобы не менять.\n")

    new_title = input(f"Название [{task.title}]: ").strip()
    if new_title:
        error = validate_title(new_title)
        if error:
            print(error)
            return
        task.title = new_title

    new_assignee = input(f"Исполнитель [{task.assignee}]: ").strip()
    if new_assignee:
        task.assignee = new_assignee

    print(f"Текущий приоритет: {task.priority}")
    new_priority = input(f"Новый приоритет ({', '.join(PRIORITIES)}) или пусто: ").strip()
    if new_priority:
        if new_priority in PRIORITIES:
            task.priority = new_priority
        else:
            print(f"Ошибка: приоритет должен быть из {', '.join(PRIORITIES)}")
            return

    print(f"Текущий этап: {task.stage}")
    new_stage = input(f"Новый этап ({', '.join(STAGES)}) или пусто: ").strip()
    if new_stage:
        if new_stage in STAGES:
            task.stage = new_stage
        else:
            print(f"Ошибка: этап должен быть из {', '.join(STAGES)}")
            return

    new_date = input(f"Срок [{task.due_date}]: ").strip()
    if new_date:
        error = validate_date(new_date)
        if error:
            print(error)
            return
        task.due_date = new_date

    print(f"Текущий статус: {task.status}")
    new_status = input(f"Новый статус ({', '.join(STATUSES)}) или пусто: ").strip()
    if new_status:
        if new_status in STATUSES:
            task.status = new_status
        else:
            print(f"Ошибка: статус должен быть из {', '.join(STATUSES)}")
            return

    storage.update(task)
    print(f"\n✓ Задача «{task.title}» обновлена")


def delete_task(storage):
    """Удаление задачи по ID с подтверждением."""
    task_id = ask_id("\nВведите ID задачи для удаления: ")
    task = storage.get_by_id(task_id)

    if not task:
        print(f"Ошибка: задачи с ID {task_id} не существует")
        return

    print(f"\nЗадача: «{task.title}» (исполнитель: {task.assignee})")
    confirm = input("Удалить? (да/нет): ").strip().lower()

    if confirm in ("да", "y", "yes", "д"):
        storage.delete(task_id)
        print(f"✓ Задача «{task.title}» удалена")
    else:
        print("Удаление отменено")


def show_summary(storage):
    """Показать сводку по задачам."""
    tasks = storage.get_all()
    print("\n=== Сводка по задачам ===\n")

    if not tasks:
        print("Задач пока нет.")
        return

    print("По статусам:")
    for status in STATUSES:
        count = sum(1 for t in tasks if t.status == status)
        print(f"  {status}: {count}")

    print("\nПо исполнителям:")
    assignees = sorted(set(t.assignee for t in tasks))
    for a in assignees:
        count = sum(1 for t in tasks if t.assignee == a)
        print(f"  {a}: {count}")

    overdue = [t for t in tasks if t.is_overdue()]
    print(f"\nПросроченных задач: {len(overdue)}")
    print(f"Всего задач: {len(tasks)}")


def main():
    """Главное меню."""
    storage = TaskStorage()

    while True:
        print("\n--- Учёт задач команды ---")
        print("1. Добавить задачу")
        print("2. Показать все задачи")
        print("3. Показать просроченные задачи")
        print("4. Показать сводку")
        print("5. Фильтровать задачи")
        print("6. Найти задачу по названию")
        print("7. Изменить задачу")
        print("8. Удалить задачу")
        print("0. Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == "1":
            add_task_interactive(storage)
        elif choice == "2":
            show_tasks(storage)
        elif choice == "3":
            show_overdue(storage)
        elif choice == "4":
            show_summary(storage)
        elif choice == "5":
            filter_tasks(storage)
        elif choice == "6":
            search_tasks(storage)
        elif choice == "7":
            edit_task(storage)
        elif choice == "8":
            delete_task(storage)
        elif choice == "0":
            print("До встречи!")
            break
        else:
            print("Ошибка: выберите 1–8 или 0")


if __name__ == "__main__":
    main()