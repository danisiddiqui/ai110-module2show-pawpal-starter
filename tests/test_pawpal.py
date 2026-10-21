from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def make_scheduler():
    """Build an owner with two pets for tests."""
    owner = Owner(name="Jordan", available_minutes=60)
    dog = Pet(name="Mochi", species="dog")
    cat = Pet(name="Luna", species="cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner, dog, cat, Scheduler(owner)


# ---------- Phase 2 quick tests ----------

def test_mark_complete_changes_status():
    task = Task("Feeding", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi")
    assert pet.task_count() == 0
    pet.add_task(Task("Walk", "07:00"))
    assert pet.task_count() == 1
    assert pet.tasks[0].pet_name == "Mochi"


# ---------- Owner / multi-pet ----------

def test_owner_get_all_tasks_combines_every_pet():
    owner, dog, cat, _ = make_scheduler()
    dog.add_task(Task("Walk", "07:00"))
    cat.add_task(Task("Feeding", "08:00"))
    assert len(owner.get_all_tasks()) == 2


def test_pet_with_no_tasks():
    owner, _, _, scheduler = make_scheduler()
    assert owner.get_all_tasks() == []
    assert scheduler.sort_by_time() == []
    assert scheduler.detect_conflicts() == []


# ---------- Sorting ----------

def test_sort_by_time_returns_chronological_order():
    _, dog, cat, scheduler = make_scheduler()
    dog.add_task(Task("Evening walk", "18:00"))
    cat.add_task(Task("Feeding", "08:00"))
    dog.add_task(Task("Lunch", "12:30"))
    times = [t.time for t in scheduler.sort_by_time()]
    assert times == ["08:00", "12:30", "18:00"]


def test_sort_breaks_ties_by_priority():
    _, dog, _, scheduler = make_scheduler()
    dog.add_task(Task("Brush", "09:00", priority="low"))
    dog.add_task(Task("Meds", "09:00", priority="high"))
    assert [t.description for t in scheduler.sort_by_time()] == ["Meds", "Brush"]


# ---------- Filtering ----------

def test_filter_by_pet_and_status():
    _, dog, cat, scheduler = make_scheduler()
    walk = Task("Walk", "07:00")
    dog.add_task(walk)
    cat.add_task(Task("Feeding", "08:00"))
    walk.mark_complete()
    assert [t.description for t in scheduler.filter_tasks(pet_name="luna")] == ["Feeding"]
    assert [t.description for t in scheduler.filter_tasks(completed=True)] == ["Walk"]
    assert scheduler.filter_tasks(pet_name="Mochi", completed=False) == []


# ---------- Recurrence ----------

def test_completing_daily_task_creates_next_day_task():
    _, dog, _, scheduler = make_scheduler()
    today = date.today()
    walk = Task("Walk", "07:00", frequency="daily", due_date=today)
    dog.add_task(walk)

    next_walk = scheduler.mark_task_complete(walk)

    assert walk.completed is True
    assert next_walk is not None
    assert next_walk.due_date == today + timedelta(days=1)
    assert next_walk.completed is False
    assert dog.task_count() == 2


def test_completing_weekly_task_creates_task_next_week():
    _, _, cat, scheduler = make_scheduler()
    meds = Task("Flea meds", "08:00", frequency="weekly", due_date=date(2026, 10, 21))
    cat.add_task(meds)
    assert scheduler.mark_task_complete(meds).due_date == date(2026, 10, 28)


def test_one_time_task_does_not_repeat():
    _, dog, _, scheduler = make_scheduler()
    vet = Task("Vet", "14:00", frequency="once")
    dog.add_task(vet)
    assert scheduler.mark_task_complete(vet) is None
    assert dog.task_count() == 1


# ---------- Conflict detection ----------

def test_detect_conflicts_flags_duplicate_times():
    _, dog, cat, scheduler = make_scheduler()
    dog.add_task(Task("Walk", "08:00"))
    cat.add_task(Task("Feeding", "08:00"))
    cat.add_task(Task("Play", "12:00"))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Walk (Mochi)" in warnings[0] and "Feeding (Luna)" in warnings[0]


def test_completed_tasks_do_not_conflict():
    _, dog, cat, scheduler = make_scheduler()
    walk = Task("Walk", "08:00")
    dog.add_task(walk)
    cat.add_task(Task("Feeding", "08:00"))
    walk.mark_complete()
    assert scheduler.detect_conflicts() == []


# ---------- Daily plan ----------

def test_daily_plan_respects_available_time_and_priority():
    _, dog, cat, scheduler = make_scheduler()  # 60 minutes available
    dog.add_task(Task("Walk", "07:00", 40, "high"))
    cat.add_task(Task("Grooming", "09:00", 30, "low"))
    cat.add_task(Task("Feeding", "08:00", 10, "high"))
    scheduled, skipped = scheduler.build_daily_plan()
    assert [t.description for t in scheduled] == ["Walk", "Feeding"]
    assert [t.description for t in skipped] == ["Grooming"]
