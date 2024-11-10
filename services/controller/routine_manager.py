import asyncio
import datetime
import logging
import os
from dotenv import load_dotenv
import json

load_dotenv()
HOME_HOST = os.getenv("HOME_HOST")
HOME_PORT = os.getenv("HOME_PORT")


class RoutineManager:
    def __init__(self, routine_msg_handler):
        self.action_type_map = {}
        self.routine_msg_handler = routine_msg_handler
        self.scheduled_tasks = set()  # Use set to track scheduled tasks
        self.routines = {}
        self.actions = {}

    async def cancel_scheduled_tasks(self):
        """Cancel all currently scheduled routines."""
        for task in self.scheduled_tasks:
            if not task.cancelled():
                task.cancel()
        self.scheduled_tasks.clear()  # Clear the set after cancellation

    async def handle_action(self, routine):
        logging.info(f"Handling action for routine {routine['name']}")
        """Executes actions in the routine if the eval_condition evaluates to True."""
        eval_condition = (
            routine.get("eval_condition") or "True"
        )  # Handle None and empty string
        try:
            condition = eval(eval_condition)
        except Exception as e:
            logging.error(f"Failed to evaluate condition {eval_condition}: {e}")
            condition = False

        if condition:
            # Do routine!
            for action_id in routine["actions"]:
                if action_id in self.actions:
                    action = self.actions[action_id]
                    action_type = action["type"]
                    try:
                        params = eval(
                            action.get("eval_params") or "{}"
                        )  # Handle None and empty string

                        logging.info(
                            f"Sending routine message for action {action_type} with params: {params}"
                        )

                        self.routine_msg_handler(routine, action_type, params)
                    except Exception as e:
                        logging.error(f"Error handling action: {e}")
                else:
                    logging.error(f"Action UUID not found: {action_id}")

            routine["run_count"] += 1

    async def schedule_routine(self, routine, trigger_time):
        """Schedules the routine at the specified trigger_time, respecting repeat_interval if provided."""
        while True:
            now = datetime.datetime.now()
            if trigger_time <= now:
                logging.info(f"Executing routine '{routine['name']} immediately")
                await self.handle_action(routine)

                # Calculate next trigger time based on repeat interval
                repeat_interval = routine.get("repeat_interval")
                if repeat_interval:
                    try:
                        interval_parts = list(map(int, repeat_interval.split(":")))
                        interval_delta = datetime.timedelta(
                            hours=interval_parts[0],
                            minutes=interval_parts[1],
                            seconds=interval_parts[2],
                        )
                        trigger_time += interval_delta

                        # Skip missed intervals if the system was offline for a long time
                        while trigger_time < now:
                            trigger_time += interval_delta

                        logging.info(
                            f"Next trigger for '{routine['name']}' at {trigger_time}"
                        )
                    except Exception as e:
                        logging.error(
                            f"Invalid repeat interval: {repeat_interval}, {e}"
                        )
                        break
                else:
                    break  # Exit loop if no repeat interval

            # Calculate delay for next execution
            delay = (trigger_time - now).total_seconds()
            logging.info(
                f"Scheduling next execution of '{routine['name']}' in {delay} seconds"
            )
            await asyncio.sleep(delay)

    async def register_routines(self, routines, actions):
        logging.info("Registering routines")

        # Save for later
        self.routines = routines
        self.actions = actions

        # Clear the action_type_map and cancel all existing scheduled tasks
        self.action_type_map.clear()
        await self.cancel_scheduled_tasks()

        for routine in routines.values():
            routine["run_count"] = 0
            triggers = routine.get("triggers", "")
            repeat_interval = routine.get("repeat_interval")

            if not triggers and repeat_interval:
                logging.info(
                    f"Executing routine '{routine['name']}' immediately with repeat interval {repeat_interval}"
                )

                trigger_time = datetime.datetime.now()
                task = asyncio.create_task(self.schedule_routine(routine, trigger_time))
                task.add_done_callback(
                    self.scheduled_tasks.discard
                )  # Discard task when done
                self.scheduled_tasks.add(task)
                continue

            trigger_list = triggers.split(",") if triggers else []

            for trigger in trigger_list:
                try:
                    trigger = trigger.strip()
                    if "T" in trigger:  # ISO datetime
                        trigger_time = datetime.datetime.fromisoformat(trigger)
                    else:  # Time format HH:MM[:SS] (UTC)
                        now = datetime.datetime.now()
                        time_parts = list(map(float, trigger.split(":")))
                        hours, minutes = time_parts[0], time_parts[1]
                        seconds = time_parts[2] if len(time_parts) > 2 else 0
                        trigger_time = now.replace(
                            hour=int(hours),
                            minute=int(minutes),
                            second=int(seconds),
                            microsecond=int((seconds % 1) * 1_000_000),
                        )

                        if trigger_time <= now:
                            trigger_time += datetime.timedelta(days=1)

                    logging.info(
                        f"Scheduling routine '{routine['name']}' at {trigger_time}"
                    )
                    task = asyncio.create_task(
                        self.schedule_routine(routine, trigger_time)
                    )
                    task.add_done_callback(
                        self.scheduled_tasks.discard
                    )  # Discard task when done
                    self.scheduled_tasks.add(task)

                except ValueError:
                    action_type = trigger
                    if action_type not in self.action_type_map:
                        self.action_type_map[action_type] = []
                    self.action_type_map[action_type].append(routine)
                    logging.info(
                        f"Registered routine '{routine['name']}' for action type '{action_type}'"
                    )

    async def handle_message(self, message):
        """Handles incoming messages by looking up routines registered for the given action type."""
        try:
            # Parse JSON data and extract action
            data = json.loads(message)

            # Check if data is a dictionary with an "action" key
            if not isinstance(data, dict) or "action" not in data:
                logging.warning("Received a message without an 'action'; ignoring.")
                return

            action_type = data.get("action")
            if action_type in self.action_type_map:
                routines = self.action_type_map[action_type]
                logging.info(
                    f"Handling {len(routines)} routines for action {action_type}"
                )
                for routine in routines:
                    await self.handle_action(routine)
            else:
                logging.info(f"No routines registered for action type '{action_type}'")
        except json.JSONDecodeError:
            logging.warning("Received an invalid JSON message; ignoring.")
        except Exception as e:
            logging.error(f"Error handling message: {e}")
