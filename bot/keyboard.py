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
                callback_data='settings'
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
    subscribe_func = []
    subs_dict = {}
    func_name = {}

    def __init__(self, callback, subs):
        self.callback = callback
        self.subs = subs
        self.orders = InlineKeyboardMarkup(row_width=1)
        self.stops = InlineKeyboardMarkup(row_width=1)

    async def set_key(self):
        pool = await self.db.create_pool()
        subs_name = list(self.subs.keys())
        ids = await self.db.get_subs_id(pool)
        sub_id = 0
        for id in ids:
            self.subs_dict[id['name']] = id['function']
            if id['name'] in subs_name and id['id'] > sub_id:
                sub_id = id['id']
                self.subscribe_func = id['function']
        functions = await self.db.get_functions(pool, self.callback)
        for func in functions:
            if func['name'] in self.subscribe_func:
                self.func_name[func['name']] = func['alias']
                if func['name'] == 'stops':
                    button = InlineKeyboardButton(
                        text=func['alias'],
                        callback_data=func['name']
                    )
                else:
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

    async def set_stops(self):
        pool = await self.db.create_pool()
        functions = await self.db.get_func(pool, 'stops')
        for func in functions:
            if func['name'] in self.subscribe_func:
                self.func_name[func['name']] = func['alias']
                button = InlineKeyboardButton(
                    text=func['alias'],
                    callback_data=self.callback_type.new(order=func['name'])
                )
                self.stops.insert(button)
        back = InlineKeyboardButton(
            text=f'\U0001F519 Назад',
            callback_data='back'
        )
        self.stops.add(back)
        await pool.close()


class KeyRest:
    callback_rest = CallbackData('rest', 'unit')

    def __init__(self):
        self.rest = InlineKeyboardMarkup(row_width=2)

    async def set_rest(self, call, units, orders, subs_dict):
        for unit in units:
            value = subs_dict[unit['subs']]
            if call in value:
                if unit['uuid'] in orders:
                    em = f'\U00002705'
                else:
                    em = f'☑️'
                button = InlineKeyboardButton(
                    text=f"{em} {unit['name']}",
                    callback_data=self.callback_rest.new(unit=unit['uuid'])
                )
                self.rest.insert(button)
        commit = InlineKeyboardButton(
            text=f'\U0001F44C Применить',
            callback_data=self.callback_rest.new(unit='commit')
        )
        back = InlineKeyboardButton(
            text=f'\U0001F519 Назад',
            callback_data='back'
        )
        self.rest.add(commit)
        self.rest.add(back)


class KeySettings:
    call_settings = CallbackData('set', 'types')
    setting = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f'\U0001F515 Отключить уведомления',
                callback_data=call_settings.new(types='remove')
            )],
        [
            InlineKeyboardButton(
                text=f'\U0001F4F1 Управлять приложением',
                url='https://marketplace.dodois.io/apps/11ECF3AAF97D059CB9706F21406EBD44'
            )],
        [
            InlineKeyboardButton(
                text=f'\U0001F504 Обновить подписку',
                callback_data=call_settings.new(types='update')
            )],
        [
            InlineKeyboardButton(
                text=f'\U0001F519 Назад',
                callback_data='back'
            )]
    ])


class KeyOut:
    callback_out = CallbackData('s', 'sub')
    post = {
        'stops_rest': '\U0001F3E2 Стопы по каналам продаж',
        'stops_ings': '\U0001F9C0 Стопы по ингредиентам',
        'stops_key_ings': '\U0001F355 Стопы по ключевым ингредиентам',
        'stops_sector': '\U0001F5FE Стопы по секторам',
        'tickets': '\U0001F4D8 Тикеты клиентов',
        'birthday': '\U0001F389 Дни рождения',
        'couriers': '\U0001F69B Отчеты по курьерам',
        'refusal': '\U0001F17E Отмененные заказы',
        'metrics': '\U0001F4C9 Ключевые метрики',
        'stationary': '\U0001F373 Опоздания в ресторане',
        'revenue': '\U0001F4B5 Выручка по сети',
        'stock': '\U0001F69A Складские остатки',
        'staff': '\U0001F9FE Информация о сотрудниках'
    }

    def __init__(self, subs):
        self.out = InlineKeyboardMarkup(row_width=1)
        for sub in subs:
            button = InlineKeyboardButton(
                text=f"{self.post[sub]}",
                callback_data=self.callback_out.new(sub=f"{sub}")
            )
            self.out.insert(button)
        back = InlineKeyboardButton(
            text=f'\U0001F519 Назад',
            callback_data='back'
        )
        self.out.add(back)
