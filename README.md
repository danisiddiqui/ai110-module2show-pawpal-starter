PawPal+ (Module 2 Project)
You are building PawPal+, a Streamlit app that helps a pet owner plan care tasks for their pet.
Scenario
A busy pet owner needs help staying consistent with pet care. They want an assistant that can:
Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
Consider constraints (time available, priority, owner preferences)
Produce a daily plan and explain why it chose that plan
Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.
What you will build
Your final app should:
Let a user enter basic owner + pet info
Let a user add/edit tasks (duration + priority at minimum)
Generate a daily schedule/plan based on constraints and priorities
Display the plan clearly (and ideally explain the reasoning)
Include tests for the most important scheduling behaviors
Getting started
Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Suggested workflow
Read the scenario carefully and identify requirements and edge cases.
Draft a UML diagram (classes, attributes, methods, relationships).
Convert UML into Python class stubs (no logic yet).
Implement scheduling logic in small increments.
Add tests to verify key behaviors.
Connect your logic to the Streamlit UI in `app.py`.
Refine UML so it matches what you actually built.
🏗️ What I Built
PawPal+ is a pet care planner split into a logic layer (`pawpal_system.py`) and a Streamlit UI (`app.py`). I built and tested the logic in the terminal first with `main.py`, then connected the UI.
How the classes work together:
`Task` (dataclass): one care activity. It holds the description, time (`"HH:MM"`), duration, priority, frequency (`once`/`daily`/`weekly`), due date, and completion status. `mark_complete()` flips the status, and `next_occurrence()` builds the next copy of a repeating task.
`Pet` (dataclass): a pet's info plus its list of tasks. `add_task()` attaches a task and tags it with the pet's name.
`Owner` (dataclass): manages multiple pets and how many minutes they have for pet care today. `get_all_tasks()` returns every pet's tasks in one list.
`Scheduler`: the "brain." It always reads tasks through `Owner.get_all_tasks()`, so it works across all pets. It sorts, filters, detects conflicts, handles recurrence, and builds the daily plan.
```
Owner ──has many──▶ Pet ──has many──▶ Task
  ▲
  └── Scheduler reads owner.get_all_tasks()
```
The UML diagrams are in `diagrams/uml_draft.mmd` (Phase 1) and `diagrams/uml_final.mmd` (final). Paste either into mermaid.live to view it.
✨ Features
Multi-pet management: add any number of pets, each with its own tasks.
Sorting by time: tasks come out in chronological order, with ties broken by priority.
Filtering: by pet name and/or completed vs. incomplete.
Conflict warnings: flags two or more tasks at the exact same time, even across different pets.
Daily and weekly recurrence: completing a repeating task automatically creates the next one.
Time-budget planning: fits today's tasks into the owner's available minutes, dropping low-priority tasks first, and explains what was skipped.
🚀 How to Run
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python main.py                   # CLI demo
python -m streamlit run app.py   # web app
python -m pytest                 # tests
```
🖥️ Sample Output
Output of `python main.py` (one owner, two pets, tasks added out of order, one conflict):
```
====================================================
Today's Schedule for Jordan (90/90 min used)
----------------------------------------------------
  07:30  Mochi    Morning walk        30 min  [high]
  08:00  Luna     Feeding             10 min  [high]
  08:00  Luna     Flea medication      5 min  [high]
  12:00  Luna     Play session        15 min  [low]
  18:00  Mochi    Evening walk        30 min  [medium]

Skipped (not enough time left; lower priority goes first):
  14:00  Mochi    Vet appointment (60 min, low)
====================================================

All tasks sorted by time:
  ⬜ 07:30  Mochi    Morning walk (2026-10-21)
  ⬜ 08:00  Luna     Feeding (2026-10-21)
  ⬜ 08:00  Luna     Flea medication (2026-10-21)
  ⬜ 12:00  Luna     Play session (2026-10-21)
  ⬜ 14:00  Mochi    Vet appointment (2026-10-21)
  ⬜ 18:00  Mochi    Evening walk (2026-10-21)

Only Luna's tasks:
  ⬜ 08:00  Luna     Feeding (2026-10-21)
  ⬜ 08:00  Luna     Flea medication (2026-10-21)
  ⬜ 12:00  Luna     Play session (2026-10-21)

Conflict check:
  ⚠️ Conflict at 08:00: Feeding (Luna), Flea medication (Luna)

Marked 'Morning walk' complete. Next one auto-created for 2026-10-22.

Mochi's incomplete tasks now:
  ⬜ 14:00  Mochi    Vet appointment (2026-10-21)
  ⬜ 18:00  Mochi    Evening walk (2026-10-21)
  ⬜ 07:30  Mochi    Morning walk (2026-10-22)
```
🧪 Testing PawPal+
Run the tests with:
```bash
python -m pytest
```
The 13 tests in `tests/test_pawpal.py` cover:
Basics: `mark_complete()` changes status; adding a task increases the pet's task count.
Multi-pet: `Owner.get_all_tasks()` combines tasks from every pet.
Sorting: tasks come back in chronological order, and same-time ties are ordered by priority.
Filtering: by pet name (case-insensitive) and by completion status.
Recurrence: a daily task creates a new task for tomorrow, a weekly task creates one 7 days out, and one-time tasks don't repeat.
Conflicts: duplicate times are flagged across pets; completed tasks don't count as conflicts.
Daily plan: respects the owner's available minutes and drops low-priority tasks first.
Edge case: an owner with pets but no tasks returns empty results instead of crashing.
Sample test output:
```
============================= test session starts ==============================
platform linux -- Python 3.13.16, pytest-9.1.1, pluggy-1.7.0
rootdir: pawpal
plugins: anyio-4.15.1
collected 13 items

tests/test_pawpal.py .............                                       [100%]

============================== 13 passed in 0.03s ==============================
```
Confidence level: ⭐⭐⭐⭐ (4/5). Every core behavior has a passing test, and I checked the CLI and the Streamlit app by hand. It isn't 5 stars because conflict detection only checks exact start times (not overlapping durations), and there are no tests for bad input like `"25:99"`.
📐 Smarter Scheduling
Feature	Method(s)	Notes
Task sorting	`Scheduler.sort_by_time()`	Uses `sorted()` with a lambda key `(due_date, time, priority_rank)`. Zero-padded `"HH:MM"` strings sort correctly as text, and same-time ties go to higher priority.
Filtering	`Scheduler.filter_tasks(pet_name=..., completed=...)`	Filter by pet (case-insensitive), completion status, or both. `None` means "any."
Conflict handling	`Scheduler.detect_conflicts()`	Groups incomplete tasks by `(date, time)` and returns a warning string for any slot with 2+ tasks, across all pets. It returns warnings instead of raising errors, so the app never crashes.
Recurring tasks	`Task.next_occurrence()`, `Scheduler.mark_task_complete()`	Completing a `daily` task adds a copy due `+ timedelta(days=1)`; `weekly` adds `timedelta(weeks=1)`. `once` tasks don't repeat.
Daily plan	`Scheduler.build_daily_plan()`, `Scheduler.explain_plan()`	Picks today's incomplete tasks by priority until the owner's `available_minutes` runs out, then shows them in time order and lists what was skipped.
📸 Demo Walkthrough
Describe your app in numbered steps so a reader can follow along without watching a video:
Main UI features: owner name and daily time budget, an "Add pet" form, a "Schedule a task" form (pet, task, time, duration, priority, repeats), today's schedule table with conflict and time-budget warnings, a "Mark complete" control, and a filterable "Browse all tasks" view.
Example workflow:
Run `python -m streamlit run app.py`. Set the owner name to Jordan and time available to 120 minutes.
Add a pet Mochi (dog, 3) and click Add pet. A green "Added Mochi!" appears, and Mochi shows in the pets table with 0 tasks.
Add a second pet Luna (cat, 5).
Schedule Morning walk for Mochi at 07:30, 30 min, high priority, repeats daily.
Schedule Feeding for Luna at 08:00, 10 min, high, daily. Then schedule Brush teeth for Mochi at 08:00, 5 min, low, weekly.
Today's Schedule shows a table sorted by time (07:30 Morning walk, 08:00 Feeding, 08:00 Brush teeth, with high priority first at 08:00), a green "3 task(s) planned, using 45 of 120 minutes," and a yellow ⚠️ Conflict at 08:00: Brush teeth (Mochi), Feeding (Luna) warning that suggests moving one.
Choose 07:30 · Mochi · Morning walk under "Mark a task complete" and click ✅ Mark complete. A toast says the next Morning walk is set for tomorrow, and the walk leaves today's list.
Open 🔎 Browse all tasks and filter to Mochi / Completed to see the finished walk. Switch to Incomplete to see tomorrow's auto-created walk.
Lower time available to 10 minutes. The plan keeps only the high-priority Feeding and warns that the other tasks didn't fit.
Key Scheduler behaviors shown: sorting by time, conflict warnings across pets, daily recurrence, filtering by pet and status, and priority-based time budgeting.
Sample CLI output (`python main.py`):
```
====================================================
Today's Schedule for Jordan (90/90 min used)
----------------------------------------------------
  07:30  Mochi    Morning walk        30 min  [high]
  08:00  Luna     Feeding             10 min  [high]
  08:00  Luna     Flea medication      5 min  [high]
  12:00  Luna     Play session        15 min  [low]
  18:00  Mochi    Evening walk        30 min  [medium]

Skipped (not enough time left; lower priority goes first):
  14:00  Mochi    Vet appointment (60 min, low)
====================================================

All tasks sorted by time:
  ⬜ 07:30  Mochi    Morning walk (2026-10-21)
  ⬜ 08:00  Luna     Feeding (2026-10-21)
  ⬜ 08:00  Luna     Flea medication (2026-10-21)
  ⬜ 12:00  Luna     Play session (2026-10-21)
  ⬜ 14:00  Mochi    Vet appointment (2026-10-21)
  ⬜ 18:00  Mochi    Evening walk (2026-10-21)

Only Luna's tasks:
  ⬜ 08:00  Luna     Feeding (2026-10-21)
  ⬜ 08:00  Luna     Flea medication (2026-10-21)
  ⬜ 12:00  Luna     Play session (2026-10-21)

Conflict check:
  ⚠️ Conflict at 08:00: Feeding (Luna), Flea medication (Luna)

Marked 'Morning walk' complete. Next one auto-created for 2026-10-22.

Mochi's incomplete tasks now:
  ⬜ 14:00  Mochi    Vet appointment (2026-10-21)
  ⬜ 18:00  Mochi    Evening walk (2026-10-21)
  ⬜ 07:30  Mochi    Morning walk (2026-10-22)
```
