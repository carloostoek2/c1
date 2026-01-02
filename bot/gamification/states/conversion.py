"""
Finite State Machine (FSM) states for conversion flows.
"""
from aiogram.fsm.state import State, StatesGroup


class ConversionStates(StatesGroup):
    """
    States for the Free to VIP conversion flow.
    """
    waiting_for_payment_screenshot = State()
