from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from database.postgres_async import AsyncDatabase


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


class KeyTypes:
    callback_type = CallbackData('call', 'order')
    db = AsyncDatabase()

    def __init__(self, callback, subs):
        self.callback = callback
        self.subs = subs
        self.orders = InlineKeyboardMarkup(row_width=1)

    async def set_key(self):
        pool = await self.db.create_pool()
        subs_name = list(self.subs.keys())
        ids = await self.db.get_subs_id(pool)
        sub_id = 0
        subscribe_func = []
        for id in ids:
            if id['name'] in subs_name and id['id'] > sub_id:
                sub_id = id['id']
                subscribe_func = id['function']
        functions = await self.db.get_functions(pool, self.callback)
        for func in functions:
            if func['name'] in subscribe_func:
                button = InlineKeyboardButton(
                    text=func['alias'],
                    callback_data=self.callback_type.new(order=func['name'])
                )
                self.orders.insert(button)
        back = InlineKeyboardButton(
            text=f'\U0001F519 Назад',
            callback_data='back'
        )
        self.orders.add(back)
        await pool.close()
