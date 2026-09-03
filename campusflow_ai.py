"""
CampusFlow AI — Autonomous Campus Mission Planner
Workflow: UNDERSTAND -> PLAN -> ACT -> MONITOR -> REPLAN
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Task:
    task_id: str
    title: str
    location: str
    base_duration: int  # minutes
    queue_time: int  # minutes
    window_open: str
    window_close: str
    instruction: str


class CampusFlowAI:

    def __init__(self, accessibility_mode: bool = False):
        self.current_time_min = 12 * 60 + 45  # 12:45 PM in minutes
        self.deadline_min = 14 * 60  # 2:00 PM cutoff in minutes
        self.accessibility_mode = accessibility_mode
        self.walk_multiplier = 1.3 if accessibility_mode else 1.0

        # Knowledge Graph / Campus Resource State
        self.sensors = {
            "admin_queue": 3,
            "faculty_present": True,
            "store_kits_available": 8,
        }

    def format_time(self, minutes_from_midnight: int) -> str:
        hours = minutes_from_midnight // 60
        mins = minutes_from_midnight % 60
        period = "PM" if hours >= 12 else "AM"
        display_hour = hours if hours <= 12 else hours - 12
        return f"{display_hour}:{mins:02d} {period}"

    # STAGE 1: UNDERSTAND
    def understand(self, prompt: str):
        print("\n" + "=" * 65)
        print("STAGE 1: UNDERSTAND (Goal & Constraint Parsing)")
        print("=" * 65)
        print(f"Prompt: \"{prompt}\"")
        print(f"• Target Goal: Final arrival at Lab by 2:00 PM")
        print(
            f"• Accessibility Routing: {'Ramps/Elevators (1.3x)' if self.accessibility_mode else 'Standard Fast Walk'}"
        )

        # Extracted mission tasks
        return [
            Task(
                "submit",
                "Submit Hardcopy Assignment",
                "Admin Block (Window 2)",
                12,
                self.sensors["admin_queue"],
                "09:00 AM",
                "04:00 PM",
                "Drop in Tray B with barcode visible.",
            ),
            Task(
                "faculty",
                "Meet Faculty (Dr. Sharma)",
                "Cabin 204",
                15,
                0,
                "12:30 PM",
                "01:45 PM",
                "Review methodology before office hours close at 1:45 PM.",
            ),
            Task(
                "collect",
                "Collect IoT Hardware Kit",
                "Central Tech Store",
                10,
                2,
                "10:00 AM",
                "05:00 PM",
                "Present QR requisition ID #4092.",
            ),
            Task(
                "lab",
                "Arrive at CS Lab",
                "Computing Block Lab 4",
                5,
                0,
                "02:00 PM",
                "04:00 PM",
                "Final Lab arrival and terminal login.",
            ),
        ]

    # STAGE 2: PLAN
    def plan(self, tasks: List[Task]) -> List[Task]:
        print("\n" + "=" * 65)
        print("STAGE 2: PLAN (Smart Sequence & Slack Calculation)")
        print("=" * 65)

        total_duration = 0
        current_clock = self.current_time_min

        print(f"{'#':<3} | {'Task':<28} | {'Window':<18} | {'Time Needed'}")
        print("-" * 65)

        for i, t in enumerate(tasks, 1):
            effective_time = round(
                (t.base_duration + t.queue_time) * self.walk_multiplier
            )
            total_duration += effective_time
            start_str = self.format_time(current_clock)
            current_clock += effective_time
            end_str = self.format_time(current_clock)

            print(
                f"{i:<3} | {t.title:<28} | {start_str} - {end_str:<7} | {effective_time} mins"
            )

        slack_buffer = self.deadline_min - (
            self.current_time_min + total_duration
        )
        print("-" * 65)
        print(f"Total Mission Duration: {total_duration} mins")
        print(f"Arrival at Destination: {self.format_time(current_clock)}")
        print(
            f"Slack Buffer to 2:00 PM Cutoff: +{slack_buffer} mins (Safe margin)\n"
        )
        return tasks

    # STAGE 3: ACT
    def act(self, tasks: List[Task], active_step: int = 0):
        current_task = tasks[active_step]
        print("=" * 65)
        print(f"STAGE 3: ACT (Intelligent Guidance for Step {active_step + 1})")
        print("=" * 65)
        print(f"Next Action: Head to {current_task.location}")
        print(f"Instruction: {current_task.instruction}")
        print(
            f"Status: Queue is currently {current_task.queue_time} mins. Proceed now.\n"
        )

    # STAGE 4: MONITOR
    def monitor(self):
        print("=" * 65)
        print("STAGE 4: MONITOR (Live Sensor Telemetry)")
        print("=" * 65)
        print(
            f"• Admin Desk Queue Sensor : {self.sensors['admin_queue']} mins wait (Normal)"
        )
        print(
            f"• Faculty Cabin Occupancy : {'Present in Cabin' if self.sensors['faculty_present'] else 'AWAY'}"
        )
        print(
            f"• IoT Hardware Stock Level: {self.sensors['store_kits_available']} kits ready\n"
        )

    # STAGE 5: REPLAN
    def replan_on_disruption(
        self, tasks: List[Task], disruption_type: str
    ) -> List[Task]:
        print("=" * 65)
        print("STAGE 5: DYNAMIC REPLAN (Autonomous Conflict Resolution)")
        print("=" * 65)

        if disruption_type == "faculty_away":
            self.sensors["faculty_present"] = False
            print("ALERT: Sensor detected Dr. Sharma stepped out until 1:40 PM!")
            print(
                "ACTION: Re-ordering sequence -> Swapping Equipment pickup ahead of Faculty visit."
            )

            # Re-route sequence
            faculty_idx = next(
                i for i, t in enumerate(tasks) if t.task_id == "faculty"
            )
            collect_idx = next(
                i for i, t in enumerate(tasks) if t.task_id == "collect"
            )

            # Swap elements
            tasks[faculty_idx], tasks[collect_idx] = (
                tasks[collect_idx],
                tasks[faculty_idx],
            )

        elif disruption_type == "admin_queue_spike":
            self.sensors["admin_queue"] = 35
            print("ALERT: Admin Block queue spiked to 35 mins!")
            print(
                "ACTION: Re-routing assignment submission to 24/7 Digital Library Kiosk (0 mins wait)."
            )
            submit_task = next(t for t in tasks if t.task_id == "submit")
            submit_task.location = "Library Annex Kiosk 2"
            submit_task.queue_time = 0

        # Recalculate plan with new parameters
        return self.plan(tasks)


# ----------------------------------------------------------------------
# EXECUTION DEMO
# ----------------------------------------------------------------------
if __name__ == "__main__":
    prompt = "Before my 2 PM lab, I need to submit my assignment, collect the equipment and meet my faculty. Plan everything."

    # Initialize agent (set accessibility_mode=True for ramps/elevator routes)
    agent = CampusFlowAI(accessibility_mode=False)

    # 1. UNDERSTAND
    tasks = agent.understand(prompt)

    # 2. PLAN
    tasks = agent.plan(tasks)

    # 3. ACT
    agent.act(tasks, active_step=0)

    # 4. MONITOR
    agent.monitor()

    # 5. REPLAN (Simulating Faculty Stepping Out)
    print(">>> SIMULATING DISRUPTION EVENT: Faculty is unavailable for 20 mins...")
    replanned_tasks = agent.replan_on_disruption(
        tasks, disruption_type="faculty_away"
    )

    # Update guidance for newly sequenced step
    agent.act(replanned_tasks, active_step=1)
