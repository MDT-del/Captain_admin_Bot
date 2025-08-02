from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    """
    A states group for various conversation forms.
    """
    waiting_for_footer = State()
    waiting_for_channel_forward = State()
