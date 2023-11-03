from database.postgres_async import AsyncDatabase
from configuration.conf import Config


async def send_premium_message():  # функция отправки рекламы free пользователям
    cfg = Config()
    db = AsyncDatabase()
    pool = await db.create_pool()
    users = await db.get_data_free_users(pool)
    names = await db.get_data_given_name(pool)
    dict_for_send = {}
    for id, chat_id, name in names:  # собираем словарь id: telegram_id, имя
        dict_for_send[id] = [chat_id, name]
    list_for_send = []
    for list_users in users:  # проходим по всем free пользователям
        for user in list_users['user_id']:  # для предусмотрения 2+ id
            if user not in list_for_send:  # для отсутствия повторений
                await cfg.bot.send_message(dict_for_send[user][0], f'Привет, {dict_for_send[user][1]}!\n'
                                                                   f'Попробуй больше функций в тарифе Premium! '
                                                                   f'14 дней бесплатно!\n'
                                                                   f'Подробнее о функциях можно почитать тут: '
                                                                   f'https://aida.kaiten.site/')
                list_for_send.append(user)  # для отсутствия повторений по отправкам сообщения
