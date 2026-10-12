"""Тесты для класса TaskStorage."""

import os
import unittest
from src.models import Task
from src.storage import TaskStorage


class TestTaskStorage(unittest.TestCase):

    def setUp(self):
        """Перед каждым тестом — чистое хранилище с временным файлом."""
        self.path = "test_tasks.json"
        if os.path.exists(self.path):
            os.remove(self.path)
        self.storage = TaskStorage(self.path)

    def tearDown(self):
        """После каждого теста — удалить тестовый файл."""
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_add_and_get(self):
        """Добавление и получение задач."""
        t = Task(1, "Тест", "Анна", "Высокий", "Разработка", "2026-10-05")
        self.storage.add(t)
        self.assertEqual(len(self.storage.get_all()), 1)
        self.assertEqual(self.storage.get_all()[0].title, "Тест")

    def test_get_by_id(self):
        """Поиск задачи по id."""
        t = Task(1, "Тест", "Анна", "Высокий", "Разработка", "2026-10-05")
        self.storage.add(t)
        found = self.storage.get_by_id(1)
        self.assertIsNotNone(found)
        self.assertEqual(found.title, "Тест")

    def test_get_by_id_not_found(self):
        """Поиск несуществующей задачи — None."""
        self.assertIsNone(self.storage.get_by_id(999))

    def test_update(self):
        """Изменение задачи."""
        t = Task(1, "Тест", "Анна", "Высокий", "Разработка", "2026-10-05")
        self.storage.add(t)
        t.status = "В работе"
        self.storage.update(t)
        self.assertEqual(self.storage.get_by_id(1).status, "В работе")

    def test_delete(self):
        """Удаление задачи."""
        t = Task(1, "Тест", "Анна", "Высокий", "Разработка", "2026-10-05")
        self.storage.add(t)
        self.storage.delete(1)
        self.assertEqual(len(self.storage.get_all()), 0)

    def test_next_id_empty(self):
        """next_id на пустом хранилище — 1."""
        self.assertEqual(self.storage.next_id(), 1)

    def test_next_id_after_add(self):
        """next_id после добавления задачи."""
        self.storage.add(Task(1, "Тест", "Анна", "Высокий", "Разработка", "2026-10-05"))
        self.storage.add(Task(3, "Тест2", "Анна", "Высокий", "Разработка", "2026-10-05"))
        self.assertEqual(self.storage.next_id(), 4)

    def test_save_and_load(self):
        """Сохранение и загрузка из файла."""
        t = Task(1, "Тест", "Анна", "Высокий", "Разработка", "2026-10-05")
        self.storage.add(t)

        storage2 = TaskStorage(self.path)
        self.assertEqual(len(storage2.get_all()), 1)
        self.assertEqual(storage2.get_all()[0].title, "Тест")


if __name__ == "__main__":
    unittest.main()