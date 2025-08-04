from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    """
    A states group for various conversation forms.
    """
    # Footer states
    waiting_for_footer = State()

    # Channel registration states
    waiting_for_channel_forward = State()

    # Broadcasting states
    selecting_channels = State()
    waiting_for_caption = State()

    # Scheduling states
    selecting_schedule_date = State()
    selecting_schedule_time = State()
    
    # Premium management states
    waiting_for_user_id_premium = State()
    waiting_for_user_id_remove_premium = State()
    waiting_for_user_id_info = State()
    waiting_for_custom_days = State()
    
    # Channel premium purchase states
    selecting_channel_for_premium = State()
    waiting_for_payment_receipt = State()