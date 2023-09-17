from database.postgres_async import AsyncDatabase
from datetime import datetime, timedelta
from utils.connection import post_api
from loggs.logger import Log
from utils.sending import sending


async def stops_rest():
    db = AsyncDatabase()
    pool = await db.create_pool()
    logger = Log('CHANNEL')
    ch_type = {
        'Takeaway': 'Самовывоз', 'Delivery': 'Доставка', 'Dine-in': 'Ресторан'
    }
    orders = await db.select_orders(pool, 'stops_rest')
    for order in orders:
        minutes = order['timezone'] * 60 - 180
        created_before = datetime.now() - timedelta(minutes=minutes)
        dt_end = datetime.strftime(created_before, '%Y-%m-%dT%H:%M:%S')
        created_after = created_before - timedelta(minutes=10)
        dt_start = datetime.strftime(created_after, '%Y-%m-%dT%H:%M:%S')
        for i in range(0, len(order["uuid"]), 29):
            batch = order["uuid"][i:i + 29]
            uuids = ','.join(batch)
            channel = await post_api(f'https://api.dodois.io/dodopizza/{order["country"]}/'
                                     f'production/stop-sales-channels',
                                     order["access"], units=uuids, _from=dt_start, to=dt_end)
            try:
                for ch in channel['stopSalesBySalesChannels']:
                    start_date = ch['startedAt']
                    start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
                    if start_date > created_after:
                        tm = ch['startedAt'].split('T')
                        rest = ch['unitName']
                        reason = ch['reason']
                        cnl = ch['salesChannelName']
                        message = f'\U0001F534 Остановка продаж\n\n' \
                                  f'<b>{ch_type[cnl]} в {rest}</b>\n' \
                                  f'Причина: {reason}\n' \
                                  f'Время остановки: {tm[1]}\n'
                        await sending(order["chat_id"], message, logger)
                    if ch['endedAt'] is not None:
                        tm = ch['endedAt'].split('T')
                        rest = ch['unitName']
                        cnl = ch['salesChannelName']
                        message = f'\U0001F7E2 Возобновление продаж\n\n' \
                                  f'<b>{ch_type[cnl]} в {rest}</b>\n' \
                                  f'Время возобновления: {tm[1]}\n'
                        await sending(order["chat_id"], message, logger)
            except TypeError:
                logger.error(f'Type ERROR stop_channel - {order["id"]}')
            except KeyError:
                logger.error(f'Key ERROR stop_channel - {order["id"]}')
    await pool.close()


async def stops_sector():
    db = AsyncDatabase()
    pool = await db.create_pool()
    logger = Log('SECTOR')
    orders = await db.select_orders(pool, 'stops_sector')
    for order in orders:
        created_before = datetime.now() - timedelta(minutes=180)
        dt_end = datetime.strftime(created_before, '%Y-%m-%dT%H:%M:%S')
        created_after = created_before - timedelta(minutes=10)
        dt_start = datetime.strftime(created_after, '%Y-%m-%dT%H:%M:%S')
        for i in range(0, len(order["uuid"]), 29):
            batch = order["uuid"][i:i + 29]
            uuids = ','.join(batch)
            channel = await post_api(f'https://api.dodois.io/dodopizza/{order["country"]}/'
                                     f'delivery/stop-sales-sectors',
                                     order["access"], units=uuids, _from=dt_start, to=dt_end)
            try:
                for sc in channel['stopSalesBySectors']:
                    start_date = sc['startedAt']
                    try:
                        start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
                        if start_date > created_after:
                            tm = sc['startedAt'].split(' ')
                            rest = sc['unitName']
                            sector = sc['sectorName']
                            message = f'\U0001F534 Остановка сектора\n\n' \
                                      f'<b>{sector} в {rest}</b>\n' \
                                      f'Время остановки: {tm[1]}\n'
                            await sending(order["chat_id"], message, logger)
                        if sc['endedAt'] is not None and sc['endedAt'] != '':
                            tm = sc['endedAt'].split('T')
                            rest = sc['unitName']
                            sector = sc['sectorName']
                            message = f'\U0001F7E2 Возобновление сектора\n\n' \
                                      f'<b>{sector} в {rest}</b>\n' \
                                      f'Время возобновления: {tm[1]}\n'
                            await sending(order["chat_id"], message, logger)
                    except ValueError:
                        pass
            except TypeError:
                logger.error(f'Type ERROR stop_sector - {order["id"]}')
            except KeyError:
                logger.error(f'Key ERROR stop_sector - {order["id"]}')
    await pool.close()


async def stops_ings():
    db = AsyncDatabase()
    pool = await db.create_pool()
    logger = Log('INGS')
    orders = await db.select_orders(pool, 'stops_ings')
    for order in orders:
        minutes = order['timezone'] * 60 - 180
        created_before = datetime.now() - timedelta(minutes=minutes)
        dt_end = datetime.strftime(created_before, '%Y-%m-%dT%H:%M:%S')
        created_after = created_before - timedelta(minutes=10)
        dt_start = datetime.strftime(created_after, '%Y-%m-%dT%H:%M:%S')
        for i in range(0, len(order["uuid"]), 29):
            batch = order["uuid"][i:i + 29]
            uuids = ','.join(batch)
            ingredient = await post_api(f'https://api.dodois.io/dodopizza/{order["country"]}/'
                                        f'production/stop-sales-ingredients',
                                        order["access"], units=uuids, _from=dt_start, to=dt_end)
            try:
                for ing in ingredient['stopSalesByIngredients']:
                    start_date = ing['startedAt']
                    start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
                    if start_date > created_after:
                        tm = ing['startedAt'].split('T')
                        reason = ing['reason']
                        rest = ing['unitName']
                        stop_ing = ing['ingredientName']
                        message = f'\U0001F534 Остановка продаж\n\n' \
                                  f'<b>{stop_ing} в {rest}</b>\n' \
                                  f'Причина: {reason}\n' \
                                  f'Время остановки: {tm[1]}\n'
                        await sending(order["chat_id"], message, logger)
                    if ing['endedAt'] is not None:
                        tm = ing['endedAt'].split('T')
                        rest = ing['unitName']
                        stop_ing = ing['ingredientName']
                        message = f'\U0001F7E2 Возобновление продаж\n\n' \
                                  f'<b>{stop_ing} в {rest}</b>\n' \
                                  f'Время возобновления: {tm[1]}\n'
                        await sending(order["chat_id"], message, logger)
            except TypeError:
                logger.error(f'Type ERROR stop_ings - {order["id"]}')
            except KeyError:
                logger.error(f'Key ERROR stop_ings - {order["id"]}')
    await pool.close()


async def stops_key_ings():
    ings = [
        "Тесто 25", "Тесто 30", "Тесто 35",
        "Сыр моцарелла", "Пицца-соус", 'Соус Альфредо',
        "Бекон(слайс)", "Ветчина", "Говядина", "Картофель соломкой",
        "Кофе зерно", "Лук красный", "Мороженое", "Молоко",
        "Салат свежий", "Салями Пепперони", "Салями Чоризо",
        "Перец свежий", "Соус МаксТейсти(Бургер)", "Соус Барбекю",
        "Соус Чесночный ранч", "Томаты свежие", "Цыпленок филе",
        "Чеснок сухой", "Шампиньоны свежие", "Тортилья пшеничная 25см",
        "Добрый Кола 0,33", "Добрый Кола 0,5", "Маффин Три шоколада",
        "Соус Сырный порционный", "Чизкейк", "Коробка 25", "Коробка 30",
        "Коробка 35", "Стакан для кофе 250мл", "Стакан для кофе 300мл",
        "Стакан для кофе 400мл"
    ]
    db = AsyncDatabase()
    pool = await db.create_pool()
    logger = Log('INGS')
    orders = await db.select_orders(pool, 'ings')
    for order in orders:
        minutes = order['timezone'] * 60 - 180
        created_before = datetime.now() - timedelta(minutes=minutes)
        dt_end = datetime.strftime(created_before, '%Y-%m-%dT%H:%M:%S')
        created_after = created_before - timedelta(minutes=10)
        dt_start = datetime.strftime(created_after, '%Y-%m-%dT%H:%M:%S')
        for i in range(0, len(order["uuid"]), 29):
            batch = order["uuid"][i:i + 29]
            uuids = ','.join(batch)
            ingredient = await post_api(f'https://api.dodois.io/dodopizza/{order["country"]}/'
                                        f'production/stop-sales-ingredients',
                                        order["access"], units=uuids, _from=dt_start, to=dt_end)
            try:
                for ing in ingredient['stopSalesByIngredients']:
                    start_date = ing['startedAt']
                    start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
                    if start_date > created_after:
                        tm = ing['startedAt'].split('T')
                        reason = ing['reason']
                        rest = ing['unitName']
                        stop_ing = ing['ingredientName']
                        if stop_ing in ings:
                            message = f'\U0001F534 Остановка продаж\n\n' \
                                      f'<b>{stop_ing} в {rest}</b>\n' \
                                      f'Причина: {reason}\n' \
                                      f'Время остановки: {tm[1]}\n'
                            await sending(order["chat_id"], message, logger)
            except TypeError:
                logger.error(f'Type ERROR stop_ings - {order["id"]}')
            except KeyError:
                logger.error(f'Key ERROR stop_ings - {order["id"]}')
    await pool.close()
