PawPal+ Project Reflection
1. System Design
Three core actions a user should be able to perform:
Add a pet: enter a pet's name, species, and age so the app can track care for more than one animal.
Schedule a care task: add a walk, feeding, medication, or appointment for a specific pet at a specific time, with a duration, priority, and whether it repeats daily or weekly.
See today's plan: view today's tasks across all pets in time order, with warnings when two tasks are at the same time and a note about anything that won't fit in the owner's available time.
a. Initial design
Briefly describe your initial UML design.
What classes did you include, and what responsibilities did you assign to each?
My initial UML (`diagrams/uml_draft.mmd`) had four classes in a simple chain: an Owner has many Pets, each Pet has many Tasks, and a Scheduler reads from the Owner. Task holds one activity: description, `"HH:MM"` time, duration, priority, frequency, due date, and a completed flag, plus `mark_complete()`. Pet stores the pet's info and its task list, with `add_task()` and `task_count()`. Owner manages the list of pets and has `get_all_tasks()` to combine every pet's tasks into one list. Scheduler is the "brain" that sorts, filters, detects conflicts, and marks tasks complete. I made Task, Pet, and Owner Python dataclasses since they mostly hold data. Scheduler is a regular class because it holds behavior, not data.
b. Design changes
Did your design change during implementation?
If yes, describe at least one change and why you made it.
Yes. First, I added a `pet_name` field to `Task`, set automatically by `Pet.add_task()`. Once the Scheduler pulled every task into one flat list through `Owner.get_all_tasks()`, a task no longer knew which pet it belonged to. That made it impossible to filter by pet or print "Feeding (Luna)" in a conflict warning. Second, I added `available_minutes` to `Owner` and a `build_daily_plan()` method to `Scheduler`, because the README scenario says the plan should consider how much time the owner has. Third, I added `Owner.get_pet()` so `mark_task_complete()` can find the right pet to attach the next recurring task to. I also moved the "make the next copy" logic into `Task.next_occurrence()`, so the Task decides its own next date and the Scheduler just adds it to the pet. All of these changes are in `diagrams/uml_final.mmd`.
---
2. Scheduling Logic and Tradeoffs
a. Constraints and priorities
What constraints does your scheduler consider (for example: time, priority, preferences)?
How did you decide which constraints mattered most?
The scheduler considers time of day (tasks sorted by `"HH:MM"`), due date (only today's tasks are planned), priority (high, medium, low), duration, the owner's available minutes, and completion status (finished tasks are left out of the plan and conflict checks). I decided priority mattered most when time runs out, because skipping a medication or feeding is worse than skipping a play session. So `build_daily_plan()` fills the time budget in priority order, then shows the chosen tasks in time order, because that's how an owner actually goes through their day. Priority is also the tie-breaker when two tasks share the same time.
b. Tradeoffs
Describe one tradeoff your scheduler makes.
Why is that tradeoff reasonable for this scenario?
Conflict detection only checks for tasks with the exact same start time, not overlapping durations. For example, a 30-minute walk at 07:30 and a feeding at 07:45 overlap but won't be flagged. I chose this because it's simple, easy to read, and easy to test: I group tasks by `(date, time)` and warn about any group with more than one task. Most pet care tasks are scheduled on round times like 08:00, so exact matches catch the most common mistake. Checking real overlaps would mean comparing start and end times for every pair of tasks, which adds complexity a busy pet owner probably doesn't need for a first version. A second tradeoff: the daily plan is greedy. It takes the highest-priority tasks first until time runs out, which is easy to explain but doesn't always fit the most tasks possible into the budget.
---
3. AI Collaboration
a. How you used AI
How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
What kinds of prompts or questions were most helpful?
I used Claude as my AI coding assistant for the whole project. I used it to brainstorm the four classes and draft the Mermaid UML, generate the dataclass skeleton, implement the Scheduler's sorting, filtering, recurrence, and conflict logic, write the `main.py` demo and the pytest suite, and connect everything to Streamlit with `st.session_state`. The most helpful prompts were specific and tied to my files, for example "Based on my skeleton in `pawpal_system.py`, how should the Scheduler get all tasks from the Owner's pets?" and "How do I sort `HH:MM` strings with a lambda key?" Asking it to run `main.py` and the tests after each change was also helpful, because I could see the output instead of just trusting that the code worked.
b. Judgment and verification
Describe one moment where you did not accept an AI suggestion as-is.
How did you evaluate or verify what the AI suggested?
The first version of `sort_by_time()` sorted only by the `time` string. When I ran `main.py` after marking the daily Morning walk complete, tomorrow's 07:30 walk showed up at the top of Mochi's list, ahead of today's 14:00 vet appointment, because "07:30" < "14:00" even though it was a different day. I didn't accept that version. I changed the sort key to `(due_date, time, priority)` so tasks are ordered by date first, and the next run of `main.py` showed tomorrow's walk at the bottom where it belongs. Another change: the AI's first `main.py` found the Morning walk with a list index (`filter_tasks(pet_name="Mochi")[1]`), which would silently grab the wrong task if I added tasks in a different order. I replaced it with a lookup by description. I verified both changes by rerunning `main.py` and `python -m pytest`.
---
4. Testing and Verification
a. What you tested
What behaviors did you test?
Why were these tests important?
The 13 tests in `tests/test_pawpal.py` check that `mark_complete()` changes status, adding a task raises a pet's task count, and `Owner.get_all_tasks()` combines every pet's tasks. They also check that `sort_by_time()` returns chronological order with priority breaking ties, and that `filter_tasks()` works by pet and by status. For recurrence, they check that a daily task creates a new task for tomorrow, a weekly task creates one for next week, and a one-time task doesn't repeat. For conflicts, they check that duplicate times are flagged across pets and completed tasks aren't. Finally, they check that `build_daily_plan()` respects the time budget, and that an owner with no tasks returns empty results instead of crashing. These tests matter because the scheduling algorithms are the "smart" part of the app, and a small mistake like a wrong date in recurrence would be easy to miss just by looking at the UI.
b. Confidence
How confident are you that your scheduler works correctly?
What edge cases would you test next if you had more time?
I'm about 4 out of 5 confident. All 13 tests pass, and I checked the CLI output and the Streamlit app by hand. Next I would test overlapping durations (07:30 for 30 minutes vs. 07:45), invalid times like `"25:99"` or `"8:00"` without a leading zero (which would sort wrong as text), duplicate pet names, a task longer than the owner's whole time budget, and what happens to a daily task that's never marked complete (it currently stays on its original date instead of rolling forward).
---
5. Reflection
a. What went well
What part of this project are you most satisfied with?
I'm most satisfied with the clean split between the logic layer and the UI. Because I built `pawpal_system.py` "CLI-first" and verified it with `main.py` and pytest, connecting it to Streamlit was mostly just calling methods that already worked. I'm also happy that the Scheduler always goes through `Owner.get_all_tasks()`, so every feature (sorting, filtering, conflicts, the daily plan) works across all pets automatically.
b. What you would improve
If you had another iteration, what would you improve or redesign?
I would store task times as real `datetime.time` objects instead of `"HH:MM"` strings, so invalid times are impossible and real overlap detection using durations is easy. I'd also add editing and deleting tasks in the UI, and save the owner's data to a JSON file so it survives closing the browser, since `st.session_state` resets when the session ends.
c. Key takeaway
What is one important thing you learned about designing systems or working with AI on this project?
Being the "lead architect" means the AI can write code quickly, but I still have to decide what the system should do and check that it actually does it. The AI's first sorting version passed a simple test but was wrong once recurring tasks created tasks on other days. I only caught that by running the demo and reading the output carefully. Designing the UML first gave me a blueprint to judge the AI's code against, and running the tests after every change is how I made sure it stayed correct.
AI strategy notes
Most effective AI features: having the AI generate code and then run it (`main.py`, `pytest`) in the same step, so I saw real output right away. Agent-style multi-file edits helped with recurrence, which touched both `Task` and `Scheduler`.
A suggestion I modified to keep the design clean: the date-blind sort key and the index-based task lookup in `main.py`, described in 3b.
Chat sessions: I mostly worked in one conversation but kept it organized by phase (design, then implementation, then algorithms, then tests, then UI and docs). Working one phase at a time kept the AI focused on one goal, and having the UML from Phase 1 made it easy to notice when the code started drifting from the design.
