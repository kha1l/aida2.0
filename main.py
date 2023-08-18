from loggs.logger import Log
from aiogram import executor, types
from configuration.conf import Config
from aiogram.dispatcher.filters import CommandStart
from database.postgres import Database
from utils.cleaners import Clean
from utils.stationary import Units
import time
from aiogram.dispatcher import FSMContext
from authorization.users import Users


@Config.dp.message_handler(CommandStart(), state=['*'])
async def start_func(message: types.Message, state: FSMContext):
    await state.finish()
    start_time = time.time()
    db = Database()
    cleaner = Clean()
    print(message)
    # user = Users('F98C8F18EBB7A9086119E9DFCEBCD9D4F2F00CC1420E5505C3526463BAE3DCB3')
    # await user.get_tokens()
    # account = db.check_auth(str(message.from_user.id))
    # mess = await message.answer(f'Идет сбор данных \U0001F4C0\nПодождите, пожалуйста')
    # if message.get_args():
    #     if account:
    #         units = Units(account)
    #         access_units = await units.get_units()
    #         await state.update_data(units=access_units)
    #         for unit in access_units:
    #             reach = db.check_stationary(unit['uuid'])
    #             if reach:
    #                 db.update_stationary(unit)
    #             else:
    #                 db.add_stationary(unit)
    # else:
    #     if account:
    #         units = Units(account)
    #         access_units = await units.get_units()
    #         await state.update_data(units=access_units)
    #         await cleaner.delete_message(mess)
    #         await message.answer(f'Привет, {message.from_user.full_name}! \n\n'
    #                              f'Я - Aida. Присылаю мгновенные уведомления о стопах, тикетах, '
    #                              f'днях рождения, отказах, ключевых метриках и отчетов по курьерам')
    #         print(time.time() - start_time)
    #     else:
    #         await cleaner.delete_message(mess)
    #         await message.answer(f'Привет, {message.from_user.full_name}\n\n'
    #                              f'Я - Aida. Присылаю мгновенные уведомления о стопах, тикетах,'
    #                              f'днях рождения, отказах, ключевых метриках и отчетов по курьерам\n'
    #                              f'Авторизуйтесь на странице приложения в маркетплейсе\n'
    #                              f'https://marketplace.dodois.io/apps/11ECF3AAF97D059CB9706F21406EBD11')


if __name__ == '__main__':
    logger = Log('MAIN')
    logger.info('START_AIDA')
    Config.scheduler.start()
    executor.start_polling(Config.dp)
