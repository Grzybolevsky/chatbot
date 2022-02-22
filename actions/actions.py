import calendar
import json
import re
from datetime import datetime
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List


class CheckIfNowOpen(Action):
    def name(self) -> Text:
        return "check_if_open_now"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_date = datetime.now()
        day_of_week = calendar.day_name[current_date.weekday()]
        hour = current_date.hour
        with open('db/opening_hours.json') as file:
            opening_time = json.load(file).get('items').get(day_of_week.capitalize())
        if opening_time is None:
            message = f"I couldn't understand {day_of_week}"
            dispatcher.utter_message(text=f"I couldn't understand {day_of_week}")
        else:
            opening_hour = int(opening_time.get('open'))
            close_hour = int(opening_time.get('close'))
            message = f"Yes, the restaurant is opened at {hour} on {day_of_week}" if \
                (hour > opening_hour) and (hour < close_hour) else \
                f"No, the restaurant won't be opened at {hour} on {day_of_week}"
        dispatcher.utter_message(text=message)
        return []


class CheckIfOpen(Action):
    def name(self) -> Text:
        return "check_if_open"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        day_of_week = ''
        hour = None
        for blob in tracker.latest_message['entities']:
            if blob['entity'] == 'day_of_week':
                day_of_week = blob['value']
            elif blob['entity'] == 'hour':
                hour = int(blob['value'])

        with open('db/opening_hours.json') as file:
            opening_time = json.load(file).get('items').get(day_of_week.capitalize())

        if opening_time is None:
            message = f"I couldn't understand {day_of_week}"
            dispatcher.utter_message(text=f"I couldn't understand {day_of_week}")
        elif hour is None:
            message = f"The restaurant at {day_of_week} is open from {opening_time.get('open')} to {opening_time.get('close')}"
        elif (int(hour) < 0) or (int(hour) > 24):
            message = f"Given hour is incorrect"
        else:
            opening_hour = int(opening_time.get('open'))
            close_hour = int(opening_time.get('close'))
            message = f"Yes, the restaurant is opened at {hour} on {day_of_week}" if \
                (hour > opening_hour) and (hour < close_hour) else \
                f"No, the restaurant won't be opened at {hour} on {day_of_week}"

        dispatcher.utter_message(text=message)
        return []


class ShowMenu(Action):
    def name(self) -> Text:
        return "show_menu"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with open('db/menu.json') as file:
            menu = json.load(file).get('items')
        message = 'The menu is:\n'
        for position in menu:
            message += f"{position.get('name')} {position.get('price')}$\n"
        dispatcher.utter_message(text=message)

        return []


class ShowOrder(Action):
    def name(self) -> Text:
        return "show_order"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        selected = tracker.get_slot('selected_meals').split(',')
        with open('db/menu.json') as menu_items:
            menu_items = json.load(menu_items).get('items')
        menu = [item.get('name') for item in menu_items]
        approved = []
        not_found = []

        for meal in selected:
            menu_contains_meal = False
            for meal_in_menu in menu:
                if meal_in_menu in meal:
                    menu_contains_meal = True
                    break
            if menu_contains_meal:
                approved.append(meal)
            else:
                not_found.append(meal)

        if not_found:
            not_found_items = ', '.join([item.lstrip() for item in not_found])
            dispatcher.utter_message(text=f"Cannot find meals with names {not_found_items}")

        price = 0
        time = 0
        for item in approved:
            count_found = re.search(r'\d+', item)
            if count_found:
                count = int(count_found.group())
            else:
                count = 1
            selected_meal = ''
            for meal in menu:
                if meal in item:  # if menu_meal is substr of item
                    selected_meal = meal

            extra_info_with_number = item.replace(selected_meal, '')
            extra_info = ''.join([i for i in extra_info_with_number if not i.isdigit()]).lstrip()

            item_price = 0
            item_time = 0
            for menu_item in menu_items:
                if menu_item.get('name') is selected_meal:
                    item_price = menu_item.get('price')
                    item_time = menu_item.get('preparation_time')

            price += item_price * count
            time += item_time * count
            meal_info = f'{count}x {selected_meal}, Price: {item_price}x{count}={item_price * count} \
             Estimated delivery time: {item_time}x{count}={item_time * count}'
            if extra_info:
                meal_info += f' Extra info: {extra_info}'

            dispatcher.utter_message(text=meal_info)
        dispatcher.utter_message(text=f'Order price is {price}$. Food will be prepared in {time} hours')
        return []


class SubmitOrderDelivery(Action):
    def name(self) -> Text:
        return "submit_order_delivery"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        address = tracker.get_slot('address')
        dispatcher.utter_message(text=f"Thank you, your order will be delivered to {address}")

        return []
