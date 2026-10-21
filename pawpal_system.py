"""PawPal+ logic layer: Task, Pet, Owner, and Scheduler classes."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
VALID_FREQUENCIES = ("once", "daily", "weekly")


@dataclass
class Task:
    """A single pet care activity, like a walk, feeding, or medication."""

    description: str
    time: str  # "HH:MM", 24-hour clock
    duration_minutes: int = 15
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return a fresh copy of this task for its next due date, or None if it doesn't repeat."""
        if self.frequency == "daily":
            return replace(self, due_date=self.due_date + timedelta(days=1), completed=False)
        if self.frequency == "weekly":
            return replace(self, due_date=self.due_date + timedelta(weeks=1), completed=False)
        return None


@dataclass
class Pet:
    """A pet and the list of care tasks that belong to it."""

    name: str
    species: str = "dog"
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet if it is present."""
        if task in self.tasks:
            self.tasks.remove(task)

    def task_count(self) -> int:
        """Return how many tasks this pet has."""
        return len(self.tasks)


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    available_minutes: int = 120  # how much care time the owner has per day
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Find a pet by name (case-insensitive), or return None."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Return every task from every pet in one list."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Scheduler:
    """The 'brain' that retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        """Create a scheduler that reads tasks from the given owner."""
        self.owner = owner

    # ---------- retrieval ----------

    def get_tasks_for_date(self, day: date | None = None) -> list[Task]:
        """Return all tasks (across every pet) that are due on the given day (default: today)."""
        day = day or date.today()
        return [t for t in self.owner.get_all_tasks() if t.due_date == day]

    # ---------- sorting & filtering ----------

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks in chronological order (date, then "HH:MM" time); ties go to higher priority."""
        tasks = self.owner.get_all_tasks() if tasks is None else tasks
        # Zero-padded "HH:MM" strings sort correctly as text ("08:00" < "13:30").
        return sorted(tasks, key=lambda t: (t.due_date, t.time, PRIORITY_RANK.get(t.priority, 1)))

    def filter_tasks(
        self,
        tasks: list[Task] | None = None,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Return tasks matching a pet name and/or completion status (None means 'any')."""
        tasks = self.owner.get_all_tasks() if tasks is None else tasks
        result = tasks
        if pet_name is not None:
            result = [t for t in result if t.pet_name.lower() == pet_name.lower()]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result

    # ---------- recurring tasks ----------

    def mark_task_complete(self, task: Task) -> Task | None:
        """Complete a task; if it repeats, add its next occurrence to the same pet and return it."""
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(next_task)
        return next_task

    # ---------- conflict detection ----------

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Return warning messages for incomplete tasks scheduled at the exact same date and time."""
        tasks = self.get_tasks_for_date() if tasks is None else tasks
        by_slot: dict[tuple[date, str], list[Task]] = {}
        for t in tasks:
            if not t.completed:
                by_slot.setdefault((t.due_date, t.time), []).append(t)

        warnings = []
        for (_, time), clashing in sorted(by_slot.items()):
            if len(clashing) > 1:
                names = ", ".join(f"{t.description} ({t.pet_name})" for t in clashing)
                warnings.append(f"⚠️ Conflict at {time}: {names}")
        return warnings

    # ---------- daily plan ----------

    def build_daily_plan(self, day: date | None = None) -> tuple[list[Task], list[Task]]:
        """Pick today's incomplete tasks that fit in the owner's available time, favoring high priority.

        Returns (scheduled, skipped). Scheduled tasks come back sorted by time.
        """
        todo = self.filter_tasks(self.get_tasks_for_date(day), completed=False)
        by_priority = sorted(todo, key=lambda t: (PRIORITY_RANK.get(t.priority, 1), t.time))

        scheduled, skipped = [], []
        minutes_left = self.owner.available_minutes
        for t in by_priority:
            if t.duration_minutes <= minutes_left:
                scheduled.append(t)
                minutes_left -= t.duration_minutes
            else:
                skipped.append(t)
        return self.sort_by_time(scheduled), skipped

    def explain_plan(self, day: date | None = None) -> str:
        """Return a readable, multi-line explanation of today's plan."""
        scheduled, skipped = self.build_daily_plan(day)
        used = sum(t.duration_minutes for t in scheduled)
        lines = [f"Today's Schedule for {self.owner.name} "
                 f"({used}/{self.owner.available_minutes} min used)"]
        lines.append("-" * 52)
        if not scheduled:
            lines.append("  No tasks scheduled for today.")
        for t in scheduled:
            lines.append(f"  {t.time}  {t.pet_name:<8} {t.description:<18} "
                         f"{t.duration_minutes:>3} min  [{t.priority}]")
        if skipped:
            lines.append("")
            lines.append("Skipped (not enough time left; lower priority goes first):")
            for t in skipped:
                lines.append(f"  {t.time}  {t.pet_name:<8} {t.description} ({t.duration_minutes} min, {t.priority})")
        return "\n".join(lines)
