"""Оконный интерфейс на Tkinter."""

import tkinter as tk
from tkinter import ttk, messagebox

from src.storage import TaskStorage
from src.models import Task

from datetime import date


PRIORITIES = ["Низкий", "Средний", "Высокий"]
STAGES = ["Анализ", "Разработка", "Тестирование", "Внедрение"]
STATUSES = ["Новая", "В работе", "Выполнена"]


class App:
    """Главное окно приложения."""

    def __init__(self, root):
        self.root = root
        self.root.title("Учёт задач команды разработки")
        self.root.geometry("1000x600")

        self.storage = TaskStorage()

        self._build_filters()
        self._build_table()
        self._build_buttons()

        self.refresh()

    # ── Фильтры сверху ──
    def _build_filters(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        ttk.Entry(frame, textvariable=self.search_var, width=25).pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(frame, text="Исполнитель:").pack(side=tk.LEFT)
        self.assignee_var = tk.StringVar(value="Все")
        assignee_combo = ttk.Combobox(frame, textvariable=self.assignee_var, width=15, state="readonly")
        assignee_combo["values"] = ["Все"]
        assignee_combo.pack(side=tk.LEFT, padx=(0, 15))
        assignee_combo.bind("<<ComboboxSelected>>", lambda *_: self.refresh())
        self.assignee_combo = assignee_combo

        ttk.Label(frame, text="Приоритет:").pack(side=tk.LEFT)
        self.priority_var = tk.StringVar(value="Все")
        priority_combo = ttk.Combobox(frame, textvariable=self.priority_var, width=12, state="readonly")
        priority_combo["values"] = ["Все"] + PRIORITIES
        priority_combo.pack(side=tk.LEFT, padx=(0, 15))
        priority_combo.bind("<<ComboboxSelected>>", lambda *_: self.refresh())

        ttk.Label(frame, text="Этап:").pack(side=tk.LEFT)
        self.stage_var = tk.StringVar(value="Все")
        stage_combo = ttk.Combobox(frame, textvariable=self.stage_var, width=15, state="readonly")
        stage_combo["values"] = ["Все"] + STAGES
        stage_combo.pack(side=tk.LEFT, padx=(0, 15))
        stage_combo.bind("<<ComboboxSelected>>", lambda *_: self.refresh())

        ttk.Label(frame, text="Статус:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="Все")
        status_combo = ttk.Combobox(frame, textvariable=self.status_var, width=12, state="readonly")
        status_combo["values"] = ["Все"] + STATUSES
        status_combo.pack(side=tk.LEFT)
        status_combo.bind("<<ComboboxSelected>>", lambda *_: self.refresh())

    # ── Таблица ──
    def _build_table(self):
        frame = ttk.Frame(self.root, padding=(10, 0))
        frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "title", "assignee", "priority", "stage", "due_date", "status")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")

        headings = {
            "id": "ID",
            "title": "Название",
            "assignee": "Исполнитель",
            "priority": "Приоритет",
            "stage": "Этап",
            "due_date": "Срок",
            "status": "Статус",
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100, anchor=tk.W)

        self.tree.column("id", width=40, anchor=tk.CENTER)
        self.tree.column("title", width=250)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.tag_configure("overdue", foreground="red")

    # ── Кнопки снизу ──
    def _build_buttons(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.X)

        ttk.Button(frame, text="Добавить", command=self.add_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Изменить", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Удалить", command=self.delete_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Сводка", command=self.show_summary).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Обновить", command=self.refresh).pack(side=tk.RIGHT, padx=5)

    # ── Обновить таблицу ──
    def refresh(self):
        # обновить список исполнителей в фильтре
        assignees = sorted(set(t.assignee for t in self.storage.get_all()))
        self.assignee_combo["values"] = ["Все"] + assignees

        # очистить таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        tasks = self.storage.get_all()

        # фильтры
        search = self.search_var.get().lower()
        assignee = self.assignee_var.get()
        priority = self.priority_var.get()
        stage = self.stage_var.get()
        status = self.status_var.get()

        if search:
            tasks = [t for t in tasks if search in t.title.lower()]
        if assignee != "Все":
            tasks = [t for t in tasks if t.assignee == assignee]
        if priority != "Все":
            tasks = [t for t in tasks if t.priority == priority]
        if stage != "Все":
            tasks = [t for t in tasks if t.stage == stage]
        if status != "Все":
            tasks = [t for t in tasks if t.status == status]

        for t in tasks:
            tag = "overdue" if t.is_overdue() else ""
            self.tree.insert("", tk.END, values=(
                t.id, t.title, t.assignee, t.priority, t.stage, t.due_date, t.status
            ), tags=(tag,))

    # ── Добавить задачу ──
    def add_task(self):
        TaskForm(self.root, self.storage, on_save=self.refresh)

    # ── Изменить задачу ──
    def edit_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите задачу в таблице")
            return

        values = self.tree.item(selected[0], "values")
        task_id = int(values[0])
        task = self.storage.get_by_id(task_id)
        if task:
            TaskForm(self.root, self.storage, task=task, on_save=self.refresh)

    # ── Удалить задачу ──
    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите задачу в таблице")
            return

        values = self.tree.item(selected[0], "values")
        task_id = int(values[0])
        task = self.storage.get_by_id(task_id)

        if not task:
            return

        if messagebox.askyesno("Подтверждение", f"Удалить задачу «{task.title}»?"):
            self.storage.delete(task_id)
            self.refresh()

    # ── Сводка ──
    def show_summary(self):
        tasks = self.storage.get_all()
        if not tasks:
            messagebox.showinfo("Сводка", "Задач пока нет")
            return

        lines = ["По статусам:"]
        for s in STATUSES:
            count = sum(1 for t in tasks if t.status == s)
            lines.append(f"  {s}: {count}")

        lines.append("\nПо исполнителям:")
        for a in sorted(set(t.assignee for t in tasks)):
            count = sum(1 for t in tasks if t.assignee == a)
            lines.append(f"  {a}: {count}")

        overdue = sum(1 for t in tasks if t.is_overdue())
        lines.append(f"\nПросроченных: {overdue}")
        lines.append(f"Всего задач: {len(tasks)}")

        messagebox.showinfo("Сводка по задачам", "\n".join(lines))


class TaskForm:
    """Окно добавления/изменения задачи."""

    def __init__(self, parent, storage, task=None, on_save=None):
        self.storage = storage
        self.task = task
        self.on_save = on_save

        self.win = tk.Toplevel(parent)
        self.win.title("Изменить задачу" if task else "Новая задача")
        self.win.geometry("450x450")
        self.win.transient(parent)
        self.win.grab_set()

        self._build()

        if task:
            self._fill(task)

    def _build(self):
        frame = ttk.Frame(self.win, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Название *").pack(anchor=tk.W)
        self.title_entry = ttk.Entry(frame, width=40)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="Исполнитель *").pack(anchor=tk.W)
        self.assignee_entry = ttk.Entry(frame, width=40)
        self.assignee_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="Приоритет").pack(anchor=tk.W)
        self.priority_combo = ttk.Combobox(frame, values=PRIORITIES, state="readonly")
        self.priority_combo.current(1)
        self.priority_combo.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="Этап").pack(anchor=tk.W)
        self.stage_combo = ttk.Combobox(frame, values=STAGES, state="readonly")
        self.stage_combo.current(1)
        self.stage_combo.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="Срок (ГГГГ-ММ-ДД) *").pack(anchor=tk.W)
        self.date_entry = ttk.Entry(frame, width=40)
        self.date_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="Статус").pack(anchor=tk.W)
        self.status_combo = ttk.Combobox(frame, values=STATUSES, state="readonly")
        self.status_combo.current(0)
        self.status_combo.pack(fill=tk.X, pady=(0, 10))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.win.destroy).pack(side=tk.RIGHT)

    def _fill(self, task):
        self.title_entry.insert(0, task.title)
        self.assignee_entry.insert(0, task.assignee)
        self.priority_combo.set(task.priority)
        self.stage_combo.set(task.stage)
        self.date_entry.insert(0, task.due_date)
        self.status_combo.set(task.status)

    def save(self):
        title = self.title_entry.get().strip()
        assignee = self.assignee_entry.get().strip()
        priority = self.priority_combo.get()
        stage = self.stage_combo.get()
        due_date = self.date_entry.get().strip()
        status = self.status_combo.get()

        if not title:
            messagebox.showerror("Ошибка", "Укажите название задачи")
            return
        if len(title) > 100:
            messagebox.showerror("Ошибка", "Название длиннее 100 символов")
            return
        if not assignee:
            messagebox.showerror("Ошибка", "Укажите исполнителя")
            return

        try:
            y, m, d = map(int, due_date.split("-"))
            date(y, m, d)
        except (ValueError, AttributeError):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД")
            return

        if self.task:
            self.task.title = title
            self.task.assignee = assignee
            self.task.priority = priority
            self.task.stage = stage
            self.task.due_date = due_date
            self.task.status = status
            self.storage.update(self.task)
        else:
            new_task = Task(
                task_id=self.storage.next_id(),
                title=title,
                assignee=assignee,
                priority=priority,
                stage=stage,
                due_date=due_date,
                status=status,
            )
            self.storage.add(new_task)

        if self.on_save:
            self.on_save()
        self.win.destroy()


def run():
    """Запустить приложение."""
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    run()