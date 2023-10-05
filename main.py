from loggs.logger import Log
from aiogram import executor, types
from configuration.conf import Config
from aiogram.dispatcher.filters import CommandStart
from database.postgres_async import AsyncDatabase
from utils.cleaners import Clean
from utils.stationary import add_stationary, Stationary
from aiogram.dispatcher import FSMContext
from authorization.users import Users, DataUser
from bot.keyboard import KeyStart, KeyTypes, KeyRest, KeySettings, KeyOut, KeyStats, KeyLive, KeyHide
from bot.states import States
from utils.update import update_tokens_app, update_subs
from functions.birthday import send_birthday
from functions.refusal import send_refusal
from functions.metrics import send_metrics, command_metrics
from functions.revenue import send_revenue, command_revenue
from functions.couriers import get_orders, send_couriers
from functions.stationary import send_stationary
from functions.staff import send_staff
from functions.tickets import send_tickets
from functions.stock import send_stock
from functions.stops import stops_rest, stops_sector, stops_ings, stops_key_ings
from datetime import datetime


# Config.scheduler.add_job(update_subs_day, 'cron', day_of_week='*', hour=17, minute=0)
Config.scheduler.add_job(update_tokens_app, 'cron', day_of_week="*", hour=11, minute=26)
Config.scheduler.add_job(send_stock, 'cron', day_of_week="*", hour=18, minute=25)
Config.scheduler.add_job(send_birthday, 'cron', day_of_week="*", hour='0-23', minute=20)
Config.scheduler.add_job(send_metrics, 'cron', day_of_week="*", hour='0-23', minute=0)
Config.scheduler.add_job(send_couriers, 'cron', day_of_week="*", hour='0-23', minute=38)
Config.scheduler.add_job(send_staff, 'cron', day_of_week="*", hour='0-23', minute=29)
Config.scheduler.add_job(send_stationary, 'cron', day_of_week="*", hour='0-23', minute=40)
Config.scheduler.add_job(send_revenue, 'cron', day_of_week="*", hour='0-23', minute=30)
Config.scheduler.add_job(send_refusal, 'cron', day_of_week="*", hour='0-23', minute=15)
Config.scheduler.add_job(stops_key_ings, 'interval', minutes=10, start_date=datetime(2023, 10, 5, 17, 24, 0))
Config.scheduler.add_job(stops_ings, 'interval', minutes=10, start_date=datetime(2023, 10, 5, 17, 27, 0))
Config.scheduler.add_job(stops_rest, 'interval', minutes=10, start_date=datetime(2023, 10, 5, 17, 30, 0))
Config.scheduler.add_job(stops_sector, 'interval', minutes=5, start_date=datetime(2023, 10, 5, 17, 33, 0))
Config.scheduler.add_job(send_tickets, 'interval', minutes=10, start_date=datetime(2023, 10, 5, 17, 35, 0))


@Config.dp.message_handler(CommandStart(), state=['*'])
async def start_func(message: types.Message, state: FSMContext):
    await state.finish()
    db = AsyncDatabase()
    pool = await db.create_pool()
    cleaner = Clean()
    code = message.get_args()
    user_id = str(message.from_user.id)
    mess = await message.answer(f'Идет сбор данных \U0001F4C0\nПодождите, пожалуйста')
    if code:
        user = Users(code)
        await user.get_tokens()
        account = await db.check_auth(pool, user_id)
        if not account:
            data = DataUser(user.access)
            await data.get_person()
            record = await db.add_user(pool, user_id, message.from_user.username,
                                       message.from_user.first_name, user.sub)
            await db.add_person(pool, record['id'], data)
            await db.add_tokens(pool, record['id'], user.access, user.refresh)
            access_units, subs = await add_stationary(record['id'], user.access)
            for units in access_units:
                reach = await db.check_stationary(pool, units['uuid'])
                if reach:
                    if reach['subs'] != units['subs'] or reach['expires'] != units['expires'] \
                            or units['user_id'] not in reach['user_id']:
                        await db.update_stationary(pool, units)
                else:
                    await db.add_stationary(pool, units)
            sorted_units = sorted(access_units, key=lambda x: x["name"])
            await state.update_data(units=sorted_units, user_id=record['id'])
            await cleaner.delete_message(mess)
            await message.answer(f'Привет, {message.from_user.full_name}! \n\n'
                                 f'Я - Aida. Помогаю удаленно управлять рестораном или сетью ресторанов '
                                 f'Dodo Brands и принимать правильные управленческие решения',
                                 reply_markup=KeyStart.type_order)
            await States.types.set()

        else:
            await db.update_tokens(pool, account['id'], user.access, user.refresh)
            access_units, subs = await add_stationary(account['id'], user.access)
            for units in access_units:
                reach = await db.check_stationary(pool, units['uuid'])
                if reach:
                    if units['user_id'] not in reach['user_id']:
                        await db.update_stationary(pool, units)
                    else:
                        if reach['expires'] != units['expires'] \
                                or reach['subs'] != units['subs']:
                            await db.update_stationary_sub_and_expires(pool, units)
                else:
                    await db.add_stationary(pool, units)
            sorted_units = sorted(access_units, key=lambda x: x["name"])
            await state.update_data(units=sorted_units, user_id=account['id'])
            await cleaner.delete_message(mess)
            await message.answer(f'Привет, {message.from_user.full_name}! \n\n'
                                 f'Я - Aida. Помогаю удаленно управлять рестораном или сетью ресторанов '
                                 f'Dodo Brands и принимать правильные управленческие решения',
                                 reply_markup=KeyStart.type_order)
            await States.types.set()
    else:
        account = await db.check_auth(pool, user_id)
        if account:
            units = await db.select_stationary(pool, account['id'])
            rests = Stationary(units)
            access_units = rests.process_units()
            await cleaner.delete_message(mess)
            sorted_units = sorted(access_units, key=lambda x: x["name"])
            await state.update_data(units=sorted_units, user_id=account['id'])
            await message.answer(f'Привет, {message.from_user.full_name}! \n\n'
                                 f'Я - Aida. Помогая удаленно управлять рестораном или сетью ресторанов '
                                 f'Dodo Brands и принимать правильные управленческие решения',
                                 reply_markup=KeyStart.type_order)
            await States.types.set()
        else:
            await cleaner.delete_message(mess)
            await message.answer(f'Привет, {message.from_user.full_name}\n\n'
                                 f'Я - Aida. Помогаю удаленно управлять рестораном или сетью ресторанов '
                                 f'Dodo Brands и принимать правильные управленческие решения\n'
                                 f'Авторизуйтесь на странице приложения в маркетплейсе\n'
                                 f'https://marketplace.dodois.io/apps/11ECF3AAF97D059CB9706F21406EBD44')
    await pool.close()


@Config.dp.callback_query_handler(text='settings', state="*")
async def settings_work(call: types.CallbackQuery):
    cleaner = Clean()
    await cleaner.delete_markup(call)
    await cleaner.delete_message(call.message)
    await call.answer()
    await call.message.answer(f'Настройки приложения: \U0001F9BE', reply_markup=KeySettings.setting)
    await States.settings.set()


@Config.dp.callback_query_handler(KeyHide.call_hide.filter())
async def statistics(call: types.CallbackQuery):
    cleaner = Clean()
    await cleaner.modify_message(call.message)
    await call.answer()


@Config.dp.callback_query_handler(KeySettings.call_settings.filter(), state=States.settings)
async def call_settings(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    cleaner = Clean()
    subs_list = []
    chat = str(call.message.chat.id)
    db = AsyncDatabase()
    pool = await db.create_pool()
    data = await state.get_data()
    await cleaner.delete_markup(call)
    await cleaner.delete_message(call.message)
    if callback_data['types'] == 'remove':
        subs = await db.get_subs(pool, chat)
        for sub in subs:
            subs_list.append(sub['post'])
        key = KeyOut(subs_list)
        await state.update_data(subs=subs_list, chat_id=chat)
        await call.message.answer(f'Выберите уведомления(отчёты), которые хотите отключить.', reply_markup=key.out)
        await States.out_call.set()
    else:
        await call.answer()
        mess = await call.message.answer(f'Идет сбор данных \U0001F4C0\nПодождите, пожалуйста')
        try:
            add_units, upd_units = await update_subs(id=data['user_id'])
            if add_units and upd_units:
                await call.message.answer(f'Обновлены данные у следующих заведений: '
                                          f'{", ".join(str(row) for row in upd_units)}\n\n'
                                          f'Добавлены следующие заведения: {", ".join(str(row) for row in add_units)}')
                await cleaner.delete_message(mess)
            elif add_units:
                await call.message.answer(f'Добавлены следующие заведения: {", ".join(str(row) for row in add_units)}')
                await cleaner.delete_message(mess)
            elif upd_units:
                await call.message.answer(f'Обновлены данные у следующих заведений: '
                                          f'{", ".join(str(row) for row in upd_units)}')
                await cleaner.delete_message(mess)
            else:
                await call.message.answer(f'Изменения не найдены. Попробуйте позднее, возможно данные еще '
                                          f'не успели обновиться.')
                await cleaner.delete_message(mess)
            await call.message.answer(f'Настройки приложения: \U0001F9BE', reply_markup=KeySettings.setting)
            await States.settings.set()
        except KeyError as e:
            logger.error(f'ERROR - {data} - {e}')
    await pool.close()


@Config.dp.callback_query_handler(KeyOut.callback_out.filter(), state=States.out_call)
async def out_subs(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    cleaner = Clean()
    await cleaner.delete_markup(call)
    await cleaner.delete_message(call.message)
    db = AsyncDatabase()
    pool = await db.create_pool()
    data = await state.get_data()
    subs_list = data['subs']
    post = callback_data.get('sub')
    name = {
        'stops_rest': 'стопах по каналам продаж',
        'stops_ings': 'стопах по ингредиентам',
        'stops_key_ings': 'стопах по ключевым ингредиентам',
        'stops_sector': 'стопах по секторам',
        'tickets': 'тикетах клиентов',
        'birthday': 'днях рождения',
        'couriers': 'отчетах о курьерах',
        'refusal': 'отмененных заказах',
        'metrics': 'ключевых метрик',
        'stationary': 'опозданиях в ресторане',
        'revenue': 'выручке по сети',
        'stock': 'складских остатках',
        'staff': 'информации о сотрудниках'
    }
    try:
        subs_list.remove(post)
        key = KeyOut(subs_list)
        await db.remove_order(pool, data['chat_id'], post)
        await state.update_data(subs=subs_list)
        await call.message.answer(f'Вы отключили уведомления о {name[post]}', reply_markup=key.out)
    except ValueError:
        pass
    await pool.close()


@Config.dp.callback_query_handler(KeyStats.wait_callback.filter())
async def statistics(call: types.CallbackQuery, callback_data: dict):
    await call.answer('Подождите, отчет собирается')
    dt = call.message.date
    post = callback_data.get('func_id')
    user = str(call.from_user.id)
    chat = str(call.message.chat.id)
    await get_orders(dt, post, chat, user)


@Config.dp.callback_query_handler(KeyLive.callback.filter(), state=States.command)
async def live_functions(call: types.CallbackQuery, callback_data: dict):
    db = AsyncDatabase()
    pool = await db.create_pool()
    callback = callback_data.get('type')
    cleaner = Clean()
    await cleaner.delete_message(call.message)
    if callback == 'metrics':
        orders = await db.select_orders_metrics(pool, 'metrics', str(call.from_user.id))
        if orders:
            await call.answer('Подождите, отчет собирается')
            for order in orders:
                await command_metrics(order, db, pool)
            await call.message.answer(f'Выбери интересующее действие:', reply_markup=KeyLive.data_type)
            await States.command.set()
        else:
            await call.answer('Вы не подписаны в метриках, ни на одну из пиццерий.')
    else:
        orders = await db.select_orders_metrics(pool, 'revenue', str(call.from_user.id))
        if orders:
            for order in orders:
                await command_revenue(order, db, pool)
            await call.answer('Подождите, отчет собирается')
            await call.message.answer(f'Выбери интересующее действие:', reply_markup=KeyLive.data_type)
            await States.command.set()
        await call.answer('Вы не подписаны в выручке, ни на одну из пиццерий.')
    await pool.close()


@Config.dp.callback_query_handler(KeyStart.callback.filter(), state=States.types)
async def subscribe(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    cleaner = Clean()
    await cleaner.delete_message(call.message)
    callback = callback_data['type']
    if callback != 'operation':
        subs = {}
        data = await state.get_data()
        for item in data["units"]:
            sub = item['subs']
            uuid = item['uuid']
            if sub in subs:
                subs[sub].append(uuid)
            else:
                subs[sub] = [uuid]
        dict_name = {}
        for unit in data['units']:
            dict_name[unit['uuid']] = unit['name']
        key = KeyTypes(callback_data['type'], subs)
        state_now = await state.get_state()
        await key.set_key()
        await state.update_data(name=dict_name, subs=subs, key=key, types=callback, stc=state_now)
        await call.message.answer(f'Выбери подписку:', reply_markup=key.orders)
        await States.rest.set()
    else:
        await call.message.answer(f'Выбери интересующее действие:', reply_markup=KeyLive.data_type)
        await States.command.set()


@Config.dp.callback_query_handler(text='stops', state=States.rest)
async def stops_menu(call: types.CallbackQuery, state: FSMContext):
    cleaner = Clean()
    data = await state.get_data()
    key = data['key']
    await cleaner.delete_markup(call)
    await key.set_stops()
    await cleaner.delete_message(call.message)
    await state.update_data(key=key)
    await call.message.answer(f'Стопы', reply_markup=key.stops)
    await States.stops.set()


@Config.dp.callback_query_handler(KeyTypes.callback_type.filter(), state=[States.rest, States.stops])
async def stationary(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    cleaner = Clean()
    await cleaner.delete_markup(call)
    await cleaner.delete_message(call.message)
    in_orders = False
    id_order = 0
    units_order = []
    db = AsyncDatabase()
    pool = await db.create_pool()
    data = await state.get_data()
    key = data['key']
    subs_dict = key.subs_dict
    key_rest = KeyRest()
    params = data['units'][0]
    try:
        code = params['country_code']
        tz = params['timezone']
    except KeyError:
        code = 'ru'
        tz = 3
    state_now = await state.get_state()
    orders = await db.get_orders(pool, str(call.message.chat.id), callback_data['order'], code, tz)
    if orders:
        in_orders = True
        units_order = orders['uuid']
        id_order = orders['id']
    unit_add, unit_del = [], []
    await key_rest.set_rest(callback_data['order'], data['units'], units_order, subs_dict)
    await call.message.answer(f'Выбери заведения:', reply_markup=key_rest.rest)
    await state.update_data(orders=units_order, key=key, order=callback_data['order'],
                            subs_dict=subs_dict, unit_del=unit_del, unit_add=unit_add,
                            code=code, tz=tz, in_orders=in_orders, id_order=id_order, stc=state_now)
    await pool.close()
    await States.pizza.set()


@Config.dp.callback_query_handler(KeyRest.callback_rest.filter(), state=States.pizza)
async def stationary(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    cleaner = Clean()
    data = await state.get_data()
    orders = data['orders']
    uuid = callback_data.get('unit')
    unit_del = data['unit_del']
    unit_add = data['unit_add']
    if uuid != 'commit':
        if uuid in orders:
            orders.remove(uuid)
            unit_del.append(data['name'][uuid])
        else:
            orders.append(uuid)
            unit_add.append(data['name'][uuid])
        key = KeyRest()
        await key.set_rest(data['order'], data['units'], orders, data['subs_dict'])
        await state.update_data(orders=orders, unit_add=unit_add, unit_del=unit_del)
        await cleaner.edit_markup(call, key.rest)
    else:
        db = AsyncDatabase()
        pool = await db.create_pool()
        func_name = data['key'].func_name
        await cleaner.delete_markup(call)
        await cleaner.delete_message(call.message)
        if unit_add:
            await call.message.answer(f"\U00002705 Вы подключили уведомления о {func_name[data['order']]} "
                                      f"из следующих заведений: \n"
                                      f"{', '.join(str(r) for r in unit_add)}")
        if unit_del:
            await call.message.answer(f"\U0000274C Вы отключили уведомления о "
                                      f"{func_name[data['order']]} из следующих заведений: \n"
                                      f"{', '.join(str(r) for r in unit_del)}")
        if data['in_orders']:
            id_order = data['id_order']
            if data['orders']:
                await db.update_order(pool, data['orders'], id_order)
            else:

                await db.drop_order(pool, id_order)
        else:
            await db.add_order(pool, data['order'], data['orders'], data['user_id'],
                               str(call.message.chat.id), data['code'], data['tz'])
        key = data['key']
        await pool.close()
        if data['order'].startswith('stops'):
            await call.message.answer(f'Стопы', reply_markup=key.stops)
            await state.update_data(stc='States:rest')
            await States.stops.set()
        else:
            await call.message.answer(f'Выбери подписку:', reply_markup=key.orders)
            await state.update_data(stc='States:types')
            await States.rest.set()


@Config.dp.callback_query_handler(text='back', state='*')
async def back_work(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cleaner = Clean()
    try:
        key = data['key']
        await cleaner.delete_message(call.message)
        await call.answer()
        if data['stc'] == 'States:stops':
            await call.message.answer(f'Стопы', reply_markup=key.stops)
            await state.update_data(stc='States:rest')
            await States.stops.set()
        elif data['stc'] == 'States:rest':
            await call.message.answer(f'Выбери подписку:', reply_markup=key.orders)
            await state.update_data(stc='States:types')
            await States.rest.set()
        else:
            await call.message.answer(f'Привет, {call.message.from_user.full_name}! \n\n'
                                      f'Я - Aida. Присылаю мгновенные уведомления о стопах, тикетах, '
                                      f'днях рождения, отказах, ключевых метриках и отчетов по курьерам',
                                      reply_markup=KeyStart.type_order)
            await States.types.set()
    except KeyError:
        if await state.get_state() == 'States:out_call':
            await call.message.answer(f'Настройки приложения: \U0001F9BE', reply_markup=KeySettings.setting)
            await States.settings.set()
        else:
            await call.message.answer(f'Привет, {call.message.from_user.full_name}! \n\n'
                                      f'Я - Aida. Присылаю мгновенные уведомления о стопах, тикетах, '
                                      f'днях рождения, отказах, ключевых метриках и отчетов по курьерам',
                                      reply_markup=KeyStart.type_order)
            await States.types.set()


@Config.dp.callback_query_handler(text='exit', state="*")
async def exit_work(call: types.CallbackQuery, state: FSMContext):
    cleaner = Clean()
    await cleaner.delete_markup(call)
    await cleaner.delete_message(call.message)
    await call.answer()
    await call.message.answer(f'Управляйте ботом по команде /start \U0001F44B')
    await state.finish()


if __name__ == '__main__':
    logger = Log('MAIN')
    logger.info('START_AIDA')
    Config.scheduler.start()
    executor.start_polling(Config.dp)
