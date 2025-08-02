from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    """
    A states group for the conversation form to set the footer.
    """
    waiting_for_footer = State()  # The state for waiting for the user to send their footer text.
