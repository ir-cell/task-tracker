from datetime import date


class Task:
    """Задача команды разработки."""

    def __init__(self, task_id, title, assignee, priority, stage, due_date, status="Новая", description=""):
        self.id = task_id
        self.title = title
        self.assignee = assignee
        self.priority = priority
        self.stage = stage
        self.due_date = due_date
        self.status = status
        self.description = description

    def is_overdue(self):
        """Просрочена ли задача: срок прошёл, а статус не «Выполнена»."""
        if self.status == "Выполнена":
            return False
        try:
            year, month, day = map(int, self.due_date.split("-"))
            deadline = date(year, month, day)
            return deadline < date.today()
        except (ValueError, AttributeError):
            return False

    def to_dict(self):
        """Превратить задачу в словарь."""
        return {
            "id": self.id,
            "title": self.title,
            "assignee": self.assignee,
            "priority": self.priority,
            "stage": self.stage,
            "due_date": self.due_date,
            "status": self.status,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data):
        """Создать задачу из словаря."""
        return cls(
            task_id=data["id"],
            title=data["title"],
            assignee=data["assignee"],
            priority=data["priority"],
            stage=data["stage"],
            due_date=data["due_date"],
            status=data.get("status", "Новая"),
            description=data.get("description", ""),
        )

    def __repr__(self):
        return f"Task(id={self.id}, title='{self.title}', assignee='{self.assignee}')"
