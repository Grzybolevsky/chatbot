from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class CheckIfOpen(Action):
    pass


class CheckMenu(Action):
    pass


class ShowOrder(Action):
    pass


class SubmitOrder(Action):
    pass
