import asyncio
import datetime
import logging
from aiohttp import ClientSession
import os
from dotenv import load_dotenv

load_dotenv()
HOME_HOST = os.getenv("HOME_HOST")
HOME_PORT = os.getenv("HOME_PORT")


async def fetch_routines(token):
    """Fetch routines from the API."""
    url = f"http://{HOME_HOST}:{HOME_PORT}/api/routines"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }

    async with ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                routines = await response.json()
                logging.info(f"Fetched routines: {routines}")
                return routines
            else:
                logging.error(f"Failed to fetch routines. Status: {response.status}")
                return []


class RoutineManager:
    def __init__(self):
        self.action_type_map = {}

    async def handle_action(self, routine):
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
            for action in routine["actions"]:
                action_type = action["type"]
                params = eval(
                    action.get("eval_params") or "{}"
                )  # Handle None and empty string
                logging.info(f"Executing action: {action_type} with params: {params}")
                # Here you'd send the action to the relevant device/service

    async def schedule_routine(self, routine, trigger_time):
        """Schedules the routine at the specified trigger_time, respecting the repeat_interval if provided."""
        while True:
            now = datetime.datetime.now()
            delay = (trigger_time - now).total_seconds()
            if delay > 0:
                logging.info(
                    f"Scheduling routine '{routine['name']}' in {delay} seconds."
                )
                await asyncio.sleep(delay)

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
                break  # Exit loop if no repeat interval

    def register_routines(self, routines):
        logging.info("Registering routines")

        for routine in routines:
            triggers = routine.get("triggers", "")
            repeat_interval = routine.get("repeat_interval")

            # Handle case where no triggers are defined but repeat_interval is provided (immediate execution)
            if not triggers and repeat_interval:
                logging.info(
                    f"Executing routine '{routine['name']}' immediately with repeat interval {repeat_interval}"
                )
                # Immediately run the routine's action without any initial delay
                asyncio.create_task(self.handle_action(routine))
                # Now schedule subsequent executions with the repeat interval
                trigger_time = datetime.datetime.now() + datetime.timedelta(
                    seconds=1
                )  # 1 second buffer
                asyncio.create_task(self.schedule_routine(routine, trigger_time))
                continue

            # Split triggers into individual trigger entries if it's a comma-separated string
            trigger_list = triggers.split(",") if triggers else []

            for trigger in trigger_list:
                try:
                    # Check if the trigger is in ISO format or HH:MM[:SS] format
                    trigger = trigger.strip()  # Strip any extra whitespace
                    if "T" in trigger:  # ISO datetime
                        trigger_time = datetime.datetime.fromisoformat(trigger)
                    else:  # Time format HH:MM[:SS]
                        now = datetime.datetime.now()
                        time_parts = list(map(float, trigger.split(":")))

                        # Handle case where only HH:MM is provided
                        if len(time_parts) == 2:
                            hours, minutes = time_parts
                            seconds = 0
                        else:
                            hours, minutes, seconds = time_parts

                        trigger_time = now.replace(
                            hour=int(hours),
                            minute=int(minutes),
                            second=int(seconds),
                            microsecond=int((seconds % 1) * 1_000_000),
                        )

                        if (
                            trigger_time <= now
                        ):  # If the time is in the past, schedule for the next day
                            trigger_time += datetime.timedelta(days=1)

                    # Schedule the routine if trigger_time is a valid datetime
                    logging.info(
                        f"Scheduling routine '{routine['name']}' at {trigger_time}"
                    )
                    asyncio.create_task(self.schedule_routine(routine, trigger_time))

                except ValueError:
                    # If not a valid datetime, assume it's an action type string
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
