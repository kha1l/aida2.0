from loggs.logger import Log
from aiogram import executor, types
from configuration.conf import Config
from aiogram.dispatcher.filters import CommandStart
from database.postgres import Database
from utils.cleaners import Clean
from utils.stationary import Units, add_stationary
from aiogram.dispatcher import FSMContext
from authorization.users import Users, DataUser


@Config.dp.message_handler(CommandStart(), state=['*'])
async def start_func(message: types.Message, state: FSMContext):
    await state.finish()
    db = Database()
    cleaner = Clean()
    code = message.get_args()
    user_id = str(message.from_user.id)
    mess = await message.answer(f'Идет сбор данных \U0001F4C0\nПодождите, пожалуйста')
    stationary = []
    if code:
        user = Users(code)
        account = db.check_auth(user_id, user.sub)
        await user.get_tokens()
        if not account:
            data = DataUser(user.access)
            await data.get_person()
            id = db.add_user(user_id, message.from_user.username, message.from_user.first_name, user.sub)
            db.add_person(id, data)
            db.add_tokens(id, user.access, user.refresh)
            access_units = await add_stationary(user.access, id)
            await state.update_data(units=access_units)
            await cleaner.delete_message(mess)
            await message.answer(f'Привет, {message.from_user.full_name}! \n\n'
                                 f'Я - Aida. Присылаю мгновенные уведомления о стопах, тикетах, '
                                 f'днях рождения, отказах, ключевых метриках и отчетов по курьерам')
            print(access_units)
        else:
            access = db.get_tokens(account)
            access_units = await add_stationary(access, account)
            await state.update_data(units=access_units)
            await cleaner.delete_message(mess)
            await message.answer(f'Привет, {message.from_user.full_name}! \n\n'
                                 f'Я - Aida. Присылаю мгновенные уведомления о стопах, тикетах, '
                                 f'днях рождения, отказах, ключевых метриках и отчетов по курьерам')
            print(access_units)
    else:
        accounts = db.check_auth_id(user_id)
        if accounts:
            for acc in accounts:
                units = Units(acc)
                access_units = await units.get_units()
                await state.update_data(units=access_units)
                await cleaner.delete_message(mess)
                await message.answer(f'Привет, {message.from_user.full_name}! \n\n'
                                     f'Я - Aida. Присылаю мгновенные уведомления о стопах, тикетах, '
                                     f'днях рождения, отказах, ключевых метриках и отчетов по курьерам')
            print(stationary)
        else:
            await cleaner.delete_message(mess)
            await message.answer(f'Привет, {message.from_user.full_name}\n\n'
                                 f'Я - Aida. Присылаю мгновенные уведомления о стопах, тикетах,'
                                 f'днях рождения, отказах, ключевых метриках и отчетов по курьерам\n'
                                 f'Авторизуйтесь на странице приложения в маркетплейсе\n'
                                 f'https://marketplace.dodois.io/apps/11ECF3AAF97D059CB9706F21406EBD11')


if __name__ == '__main__':
    logger = Log('MAIN')
    logger.info('START_AIDA')
    Config.scheduler.start()
    executor.start_polling(Config.dp)
