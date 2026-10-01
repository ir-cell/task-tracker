import json
import os

from src.models import Task


class TaskStorage:
    """Хранилище задач: сохраняет и загружает их из JSON-файла."""

    def __init__(self, path="tasks.json"):
        self.path = path
        self.tasks = []
        self.load()

    def load(self):
        """Загрузить задачи из файла. Если файла нет — пустой список."""
        if not os.path.exists(self.path):
            self.tasks = []
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError):
            self.tasks = []

    def save(self):
        """Сохранить задачи в файл."""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.tasks], f, ensure_ascii=False, indent=2)

    def add(self, task):
        """Добавить задачу."""
        self.tasks.append(task)
        self.save()

    def get_all(self):
        """Получить все задачи."""
        return self.tasks

    def get_by_id(self, task_id):
        """Найти задачу по её id."""
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None

    def update(self, task):
        """Изменить задачу (по её id)."""
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                self.tasks[i] = task
                self.save()
                return True
        return False

    def delete(self, task_id):
        """Удалить задачу по id."""
        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                del self.tasks[i]
                self.save()
                return True
        return False

    def next_id(self):
        """Получить следующий свободный id."""
        if not self.tasks:
            return 1
        return max(t.id for t in self.tasks) + 1
