from loggs.logger import Log
from aiogram import executor, types
from configuration.conf import Config
from aiogram.dispatcher.filters import CommandStart
from database.postgres_async import AsyncDatabase
from utils.cleaners import Clean
from utils.stationary import add_stationary, Stationary
from aiogram.dispatcher import FSMContext
from authorization.users import Users, DataUser
from bot.keyboard import KeyStart, KeyTypes
from bot.states import States


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
            await state.update_data(units=access_units)
            await cleaner.delete_message(mess)
            await message.answer(f'Привет, {message.from_user.full_name}! \n\n'
                                 f'Я - Aida. Присылаю мгновенные уведомления о стопах, тикетах, '
                                 f'днях рождения, отказах, ключевых метриках и отчетов по курьерам',
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
            await state.update_data(units=access_units)
            await cleaner.delete_message(mess)
            await message.answer(f'Привет, {message.from_user.full_name}! \n\n'
                                 f'Я - Aida. Присылаю мгновенные уведомления о стопах, тикетах, '
                                 f'днях рождения, отказах, ключевых метриках и отчетов по курьерам',
                                 reply_markup=KeyStart.type_order)
            await States.types.set()
    else:
        accounts = await db.check_auth(pool, user_id)
        if accounts:
            units = await db.select_stationary(pool, accounts['id'])
            rests = Stationary(units)
            access_units = rests.process_units()
            await cleaner.delete_message(mess)
            await state.update_data(units=access_units)
            await message.answer(f'Привет, {message.from_user.full_name}! \n\n'
                                 f'Я - Aida. Присылаю мгновенные уведомления о стопах, тикетах, '
                                 f'днях рождения, отказах, ключевых метриках и отчетов по курьерам',
                                 reply_markup=KeyStart.type_order)
            await States.types.set()
        else:
            await cleaner.delete_message(mess)
            await message.answer(f'Привет, {message.from_user.full_name}\n\n'
                                 f'Я - Aida. Присылаю мгновенные уведомления о стопах, тикетах,'
                                 f'днях рождения, отказах, ключевых метриках и отчетов по курьерам\n'
                                 f'Авторизуйтесь на странице приложения в маркетплейсе\n'
                                 f'https://marketplace.dodois.io/apps/11ECF3AAF97D059CB9706F21406EBD11')
    await pool.close()


@Config.dp.callback_query_handler(KeyStart.callback.filter(), state=States.types)
async def subscribe(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    cleaner = Clean()
    await cleaner.delete_message(call.message)
    subs = {}
    data = await state.get_data()
    for item in data["units"]:
        sub = item['subs']
        uuid = item['uuid']
        if sub in subs:
            subs[sub].append(uuid)
        else:
            subs[sub] = [uuid]
    await state.update_data(units=data["units"], subs=subs)
    key = KeyTypes(callback_data['type'], subs)
    await key.set_key()
    await call.message.answer(f'Выбери подписку:', reply_markup=key.orders)
    await States.rest.set()


@Config.dp.callback_query_handler(KeyTypes.callback_type.filter(), state=States.rest)
async def stationary(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    data = await state.get_data()
    print(data)
    print(callback_data)
    await state.finish()


@Config.dp.callback_query_handler(text='back', state=[States.rest])
async def back_work(call: types.CallbackQuery, state: FSMContext):
    cleaner = Clean()
    await cleaner.delete_message(call.message)
    await call.answer()
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
