from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A smart pet care planner: track tasks, sort your day, and catch scheduling conflicts.")

# ---------- App "memory" ----------
# Streamlit reruns this whole script on every click, so the Owner lives in session_state.
# It is only created once; after that we reuse the same object.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# ---------- Owner ----------
st.subheader("👤 Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = int(
        st.number_input("Time available today (minutes)", min_value=0, max_value=1440,
                        value=owner.available_minutes, step=15)
    )

# ---------- Pets ----------
st.subheader("🐶 Pets")
with st.form("add_pet", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with c2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with c3:
        age = st.number_input("Age", min_value=0, max_value=40, value=3)
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        elif owner.get_pet(pet_name.strip()):
            st.warning(f"{pet_name} is already in your list.")
        else:
            owner.add_pet(Pet(name=pet_name.strip(), species=species, age=int(age)))
            st.success(f"Added {pet_name}!")

if owner.pets:
    st.table([{"Name": p.name, "Species": p.species, "Age": p.age, "Tasks": p.task_count()}
              for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

# ---------- Tasks ----------
st.subheader("📝 Schedule a task")
if not owner.pets:
    st.caption("Add a pet first.")
else:
    with st.form("add_task", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            task_pet = st.selectbox("For which pet?", [p.name for p in owner.pets])
            description = st.text_input("Task", value="Morning walk")
            task_time = st.time_input("Time", value=None, step=900)
        with c2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["high", "medium", "low"])
            frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        if st.form_submit_button("Add task"):
            if task_time is None or not description.strip():
                st.error("Please enter a task name and a time.")
            else:
                owner.get_pet(task_pet).add_task(Task(
                    description=description.strip(),
                    time=task_time.strftime("%H:%M"),
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=frequency,
                ))
                st.success(f"Scheduled '{description}' for {task_pet} at {task_time.strftime('%H:%M')}.")

# ---------- Today's schedule ----------
st.divider()
st.subheader(f"📅 Today's Schedule ({date.today():%A, %b %d})")

for warning in scheduler.detect_conflicts():
    st.warning(f"{warning}. Consider moving one of these so you aren't doing two things at once.")

scheduled, skipped = scheduler.build_daily_plan()
if scheduled:
    used = sum(t.duration_minutes for t in scheduled)
    st.success(f"{len(scheduled)} task(s) planned, using {used} of {owner.available_minutes} minutes.")
    st.table([{"Time": t.time, "Pet": t.pet_name, "Task": t.description,
               "Minutes": t.duration_minutes, "Priority": t.priority, "Repeats": t.frequency}
              for t in scheduled])
else:
    st.info("Nothing left to do today. 🎉")

if skipped:
    st.warning("Not enough time today for: " + ", ".join(
        f"{t.description} ({t.pet_name}, {t.priority})" for t in skipped)
        + ". Lower-priority tasks are dropped first.")

# ---------- Complete a task ----------
todays_open = scheduler.sort_by_time(
    scheduler.filter_tasks(scheduler.get_tasks_for_date(), completed=False))
if todays_open:
    labels = [f"{t.time} · {t.pet_name} · {t.description}" for t in todays_open]
    choice = st.selectbox("Mark a task complete", labels)
    if st.button("✅ Mark complete"):
        task = todays_open[labels.index(choice)]
        next_task = scheduler.mark_task_complete(task)
        if next_task:
            st.toast(f"Done! Next '{task.description}' is set for {next_task.due_date}.")
        st.rerun()

# ---------- Browse all tasks ----------
with st.expander("🔎 Browse all tasks (filter)"):
    pet_filter = st.selectbox("Pet", ["All"] + [p.name for p in owner.pets])
    status_filter = st.radio("Status", ["All", "Incomplete", "Completed"], horizontal=True)
    filtered = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All" else pet_filter,
        completed={"All": None, "Incomplete": False, "Completed": True}[status_filter],
    )
    if filtered:
        st.table([{"Date": str(t.due_date), "Time": t.time, "Pet": t.pet_name,
                   "Task": t.description, "Done": "✅" if t.completed else "⬜"}
                  for t in scheduler.sort_by_time(filtered)])
    else:
        st.caption("No tasks match.")
