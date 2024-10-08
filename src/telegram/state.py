from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, User, Message
from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const

from src.telegram.db import select_key, edit_column_values, key_activated


class KeySG(StatesGroup):
    key = State()


def key_check(text: str):
    key = select_key(text)
    is_key_activated = key_activated(text)

    if key and not is_key_activated:
        return text
    raise ValueError


async def success_handler(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    user_id = dialog_manager.start_data["user_id"]

    await message.answer(text=f'The key has been activated, it was tied to your account\n\nYour ID: {user_id}')
    edit_column_values(text, user_id)

    await dialog_manager.done()

async def invalid_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: ValueError
):
    await message.answer("Invalid key")

async def cancel_click_process(callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager):
    await callback.message.edit_text("Canceled")
    await dialog_manager.mark_closed()

async def user_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    return {
        "username": event_from_user.username,
        "user_id": event_from_user.id
    }

key_dialog = Dialog(
    Window(
        Format("{username} ({user_id})\nWelcome to the key system\n\nEnter an access key: "),
        TextInput(
            id="key",
            type_factory=key_check,
            on_success=success_handler,
            on_error=invalid_handler,
        ),
        Button(
            text=Const("Cancel"),
            id="cancel",
            on_click=cancel_click_process,
        ),
        getter=user_getter,
        state=KeySG().key,
    ),
)