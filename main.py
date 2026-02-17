import random


# =========================================================
# DOMAIN
# =========================================================

class Task:
    def __init__(self, name, phases, priority=1):
        self.name = name
        self.phases = list(phases.items())  # ordered list
        self.priority = priority

        self.phase_index = 0
        self.remaining = self.phases[0][1]
        self.done = False

    @property
    def current_phase(self):
        if self.done:
            return "done"
        return self.phases[self.phase_index][0]

    def work(self, amount):
        if self.done:
            return

        self.remaining -= amount

        if self.remaining <= 0:
            self.phase_index += 1

            if self.phase_index >= len(self.phases):
                self.done = True
            else:
                self.remaining = self.phases[self.phase_index][1]

    def __str__(self):
        if self.done:
            return f"{self.name}: DONE"
        return f"{self.name}: {self.current_phase} ({self.remaining:.2f})"


class Employee:
    def __init__(self, name, role, capacity=1.0):
        self.name = name
        self.role = role
        self.base_capacity = capacity
        self.capacity = capacity

        self.task = None
        self.last_task = None

    def assign(self, task):
        self.last_task = self.task
        self.task = task

    def reset_day(self):
        self.capacity = self.base_capacity


# =========================================================
# MECHANICS SYSTEM
# =========================================================

class Mechanic:
    def start_day(self, state): pass
    def before_work(self, state, employee): pass
    def after_work(self, state, employee): pass
    def end_day(self, state): pass


# ---- Lunch mechanic

class Lunch(Mechanic):
    def start_day(self, state):
        for e in state["employees"]:
            e.capacity *= 0.85  # eats time


# ---- Context switch penalty

class ContextSwitch(Mechanic):
    def before_work(self, state, employee):
        if employee.task != employee.last_task:
            employee.capacity *= 0.7


# ---- Shift-left testing

class ShiftLeft(Mechanic):
    def start_day(self, state):
        if not state["enabled"]["shift_left"]:
            return

        for task in state["tasks"]:
            if task.current_phase == "analytics":
                task.remaining *= 0.9  # better clarity -> faster


# =========================================================
# ENGINE
# =========================================================

class Engine:
    def __init__(self, employees, tasks, mechanics, days=10, seed=1):
        self.employees = employees
        self.tasks = tasks
        self.mechanics = mechanics
        self.days = days
        self.random = random.Random(seed)

    def run(self):

        state = {
            "employees": self.employees,
            "tasks": self.tasks,
            "enabled": {
                "shift_left": True
            }
        }

        print("\n=== Sprint start ===\n")

        for day in range(1, self.days + 1):

            print(f"\nDAY {day}")
            print("-------------------")

            # reset capacity
            for e in self.employees:
                e.reset_day()

            # mechanics start
            for m in self.mechanics:
                m.start_day(state)

            # work phase
            for e in self.employees:

                for m in self.mechanics:
                    m.before_work(state, e)

                if e.task and not e.task.done:
                    e.task.work(e.capacity)
                    print(f"{e.name} worked on {e.task.name} ({e.capacity:.2f})")
                else:
                    print(f"{e.name} idle")

                for m in self.mechanics:
                    m.after_work(state, e)

            # mechanics end
            for m in self.mechanics:
                m.end_day(state)

            # log tasks
            print("\nTasks:")
            for t in self.tasks:
                print(" ", t)

        # result
        all_done = all(t.done for t in self.tasks)

        print("\n=== RESULT ===")
        if all_done:
            print("SPRINT SUCCESS ✅")
        else:
            print("SPRINT FAILED ❌")

        for t in self.tasks:
            print(" ", t)


# =========================================================
# SCENARIO (CONFIG IN CODE)
# =========================================================

if __name__ == "__main__":

    # Employees
    dev = Employee("Dev1", "dev")
    qa = Employee("QA1", "qa")

    # Tasks
    t1 = Task("Feature-A", {
        "analytics": 1,
        "dev": 3,
        "test": 2
    })

    t2 = Task("Feature-B", {
        "analytics": 1,
        "dev": 2,
        "test": 2
    })

    # Manual planning
    dev.assign(t1)
    qa.assign(t2)

    # Mechanics
    mechanics = [
        Lunch(),
        ContextSwitch(),
        ShiftLeft(),
    ]

    # Run
    Engine(
        employees=[dev, qa],
        tasks=[t1, t2],
        mechanics=mechanics,
        days=10
    ).run()
