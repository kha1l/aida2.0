from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

class KeyStart:
    callback = CallbackData('s', 'type')

    type_order = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f'\U0001F50A Уведомления',
                callback_data=callback.new(type='notice')
            )],
        [
            InlineKeyboardButton(
                text=f'\U0001F4D1 Отчеты',
                callback_data=callback.new(type='reports')
            )],
        [
            InlineKeyboardButton(
                text=f'\U0001F6E0 Настройки',
                callback_data=callback.new(type='settings')
            )],
        [
            InlineKeyboardButton(
                text=f'\U00002716 Закрыть меню',
                callback_data='exit'
            )]
    ])
