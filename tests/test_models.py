"""Тесты для класса Task."""

import unittest
from src.models import Task


class TestTask(unittest.TestCase):

    def test_create_task(self):
        """Создание задачи с полями."""
        t = Task(1, "Тест", "Анна", "Высокий", "Разработка", "2026-10-05")
        self.assertEqual(t.id, 1)
        self.assertEqual(t.title, "Тест")
        self.assertEqual(t.assignee, "Анна")
        self.assertEqual(t.priority, "Высокий")
        self.assertEqual(t.stage, "Разработка")
        self.assertEqual(t.due_date, "2026-10-05")
        self.assertEqual(t.status, "Новая")

    def test_is_overdue_future(self):
        """Задача со сроком в будущем — не просрочена."""
        t = Task(1, "Тест", "Анна", "Высокий", "Разработка", "2099-12-31")
        self.assertFalse(t.is_overdue())

    def test_is_overdue_past(self):
        """Задача со сроком в прошлом — просрочена."""
        t = Task(1, "Тест", "Анна", "Высокий", "Разработка", "2020-01-01")
        self.assertTrue(t.is_overdue())

    def test_is_overdue_done(self):
        """Выполненная задача не считается просроченной."""
        t = Task(1, "Тест", "Анна", "Высокий", "Разработка", "2020-01-01", status="Выполнена")
        self.assertFalse(t.is_overdue())

    def test_is_overdue_bad_date(self):
        """Задача с неправильной датой не падает."""
        t = Task(1, "Тест", "Анна", "Высокий", "Разработка", "абракадабра")
        self.assertFalse(t.is_overdue())

    def test_to_dict(self):
        """Превращение в словарь."""
        t = Task(1, "Тест", "Анна", "Высокий", "Разработка", "2026-10-05")
        d = t.to_dict()
        self.assertEqual(d["id"], 1)
        self.assertEqual(d["title"], "Тест")
        self.assertEqual(d["assignee"], "Анна")

    def test_from_dict(self):
        """Создание из словаря."""
        data = {
            "id": 1,
            "title": "Тест",
            "assignee": "Анна",
            "priority": "Высокий",
            "stage": "Разработка",
            "due_date": "2026-10-05",
        }
        t = Task.from_dict(data)
        self.assertEqual(t.id, 1)
        self.assertEqual(t.title, "Тест")
        self.assertEqual(t.status, "Новая")


if __name__ == "__main__":
    unittest.main()