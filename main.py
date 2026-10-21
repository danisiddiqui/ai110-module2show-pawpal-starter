"""CLI demo for PawPal+. Run with: python main.py"""

from pawpal_system import Owner, Pet, Task, Scheduler


def print_tasks(title, tasks):
    """Print a titled list of tasks in a readable format."""
    print(f"\n{title}")
    for t in tasks:
        status = "✅" if t.completed else "⬜"
        print(f"  {status} {t.time}  {t.pet_name:<8} {t.description} ({t.due_date})")


def main():
    owner = Owner(name="Jordan", available_minutes=90)
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Tasks are added out of order on purpose to show sorting.
    mochi.add_task(Task("Evening walk", "18:00", 30, "medium", "daily"))
    mochi.add_task(Task("Morning walk", "07:30", 30, "high", "daily"))
    luna.add_task(Task("Feeding", "08:00", 10, "high", "daily"))
    luna.add_task(Task("Flea medication", "08:00", 5, "high", "weekly"))  # same time -> conflict
    mochi.add_task(Task("Vet appointment", "14:00", 60, "low", "once"))
    luna.add_task(Task("Play session", "12:00", 15, "low", "daily"))

    scheduler = Scheduler(owner)

    print("=" * 52)
    print(scheduler.explain_plan())
    print("=" * 52)

    print_tasks("All tasks sorted by time:", scheduler.sort_by_time())
    print_tasks("Only Luna's tasks:", scheduler.filter_tasks(pet_name="Luna"))

    print("\nConflict check:")
    for warning in scheduler.detect_conflicts() or ["No conflicts."]:
        print(f"  {warning}")

    morning_walk = next(t for t in mochi.tasks if t.description == "Morning walk")
    next_walk = scheduler.mark_task_complete(morning_walk)
    print(f"\nMarked '{morning_walk.description}' complete. "
          f"Next one auto-created for {next_walk.due_date}.")

    print_tasks("Mochi's incomplete tasks now:",
                scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi", completed=False)))


if __name__ == "__main__":
    main()
