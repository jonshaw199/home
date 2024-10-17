import asyncio
import datetime
import logging
from aiohttp import ClientSession
import os
from dotenv import load_dotenv

load_dotenv()
HOME_HOST = os.getenv("HOME_HOST")
HOME_PORT = os.getenv("HOME_PORT")


def transform_routines_with_actions(routines, actions_map):
    filtered_routines = []
    for routine in routines:
        if not routine["active"]:
            continue

        # Replace action UUIDs with actual action objects from actions_map
        routine["actions"] = [
            actions_map.get(action_uuid)
            for action_uuid in routine["actions"]
            if actions_map.get(action_uuid) and actions_map[action_uuid].get("active")
        ]

        # Only keep the routine if it has any active actions
        if routine["actions"]:
            filtered_routines.append(routine)

    return filtered_routines


async def fetch_routines(token):
    """Fetch routines and actions from the API and assemble them."""
    routine_url = f"http://{HOME_HOST}:{HOME_PORT}/api/routines"
    actions_url = f"http://{HOME_HOST}:{HOME_PORT}/api/actions"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }

    async with ClientSession() as session:
        async with session.get(
            routine_url, headers=headers
        ) as routine_response, session.get(
            actions_url, headers=headers
        ) as actions_response:
            if routine_response.status == 200 and actions_response.status == 200:
                routines = await routine_response.json()
                actions = await actions_response.json()

                logging.info(f"Fetched routines: {routines}")
                logging.info(f"Fetched actions: {actions}")

                # Create a map of action UUIDs to action data
                actions_map = {action["uuid"]: action for action in actions}

                transformed = transform_routines_with_actions(routines, actions_map)
                logging.info(f"Transformed routines: {transformed}")
                return transformed
            else:
                logging.error(
                    f"Failed to fetch routines or actions. Status: Routines={routine_response.status}, Actions={actions_response.status}"
                )
                return []


class RoutineManager:
    def __init__(self, routine_msg_handler):
        self.action_type_map = {}
        self.routine_msg_handler = routine_msg_handler
        self.scheduled_tasks = set()  # Use set to track scheduled tasks

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
            for action in routine["actions"]:
                action_type = action["type"]
                params = eval(
                    action.get("eval_params") or "{}"
                )  # Handle None and empty string

                logging.info(
                    f"Sending routine message for action {action_type} with params: {params}"
                )

                self.routine_msg_handler(routine, action_type, params)

            routine["run_count"] += 1

    async def schedule_routine(self, routine, trigger_time):
        """Schedules the routine at the specified trigger_time, respecting the repeat_interval if provided."""
        while True:
            now = datetime.datetime.now()
            delay = (trigger_time - now).total_seconds()
            logging.info(f"Delay: {delay}")
            if delay > 0:
                logging.info(
                    f"Scheduling routine '{routine['name']}' in {delay} seconds."
                )
                await asyncio.sleep(delay)
            else:
                logging.info(f"Executing routine '{routine['name']} immediately")

            await self.handle_action(routine)

            # Handle repeat_interval
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
                    logging.info(
                        f"Routine '{routine['name']}' will repeat after {interval_delta}"
                    )
                except Exception as e:
                    logging.error(f"Invalid repeat interval: {repeat_interval}, {e}")
                    break  # Stop repeating if the interval is invalid
            else:
                logging.info(
                    f"Routine '{routine['name']}' has no repeat interval; routine complete."
                )
                break  # Exit loop if no repeat interval

    async def register_routines(self, routines):
        logging.info("Registering routines")

        # Clear the action_type_map and cancel all existing scheduled tasks
        self.action_type_map.clear()
        await self.cancel_scheduled_tasks()

        for routine in routines:
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

    async def handle_message(self, action_type):
        """Handles incoming messages by looking up routines registered for the given action type."""
        if action_type in self.action_type_map:
            for routine in self.action_type_map[action_type]:
                await self.handle_action(routine)
        else:
            logging.info(f"No routines registered for action type '{action_type}'")
