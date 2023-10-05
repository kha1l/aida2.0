from loggs.logger import Log
from database.postgres_async import AsyncDatabase
from datetime import datetime, timedelta
from utils.connection import post_api
from utils.sending import Send
from functions.certificates import order_certs
from functions.waiting import order_wait
from functions.later import order_later
from functions.later_rest import order_later_rest


async def send_couriers():
    logger = Log('COURIERS')
    db = AsyncDatabase()
    send = Send(db=db)
    pool = await db.create_pool()
    orders = await db.select_orders(pool, 'couriers')
    created_before = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dt_end = datetime.strftime(created_before, '%Y-%m-%dT%H:%M:%S')
    created_after = created_before - timedelta(days=1)
    dt_start = datetime.strftime(created_after, '%Y-%m-%dT%H:%M:%S')
    for order in orders:
        hour = datetime.now().hour - 3 + order['timezone']
        if hour == 18:
            for i in range(0, len(order['uuid']), 29):
                batch = order['uuid'][i:i + 29]
                uuids = ','.join(batch)
                statistics = await post_api(f'https://api.dodois.io/{order["concept"]}/{order["country"]}/delivery/statistics/',
                                            order["access"], units=uuids, _from=dt_start, to=dt_end)
                productivity = await post_api(f'https://api.dodois.io/{order["concept"]}/{order["country"]}/production/productivity',
                                              order["access"], units=uuids, _from=dt_start, to=dt_end)
                prod_dict = {}
                try:
                    skip = 0
                    take = 500
                    reach = True
                    dict_orders = {}
                    while reach:
                        orders = await post_api(f'https://api.dodois.io/{order["concept"]}/{order["country"]}/delivery/couriers-orders',
                                                order["access"], units=uuids, _from=dt_start, to=dt_end, skip=skip, take=take)
                        skip += take
                        for o in orders['couriersOrders']:
                            rest_name = o['unitName']
                            if rest_name in dict_orders:
                                values = dict_orders.get(rest_name)
                                if o['tripOrdersCount'] == 1:
                                    dict_orders[rest_name] = [values[0] + 1, values[1], values[2]]
                                elif o['tripOrdersCount'] == 2:
                                    dict_orders[rest_name] = [values[0], values[1] + 1, values[2]]
                                else:
                                    dict_orders[rest_name] = [values[0], values[1], values[2] + 1]
                            else:
                                if o['tripOrdersCount'] == 1:
                                    dict_orders[rest_name] = [1, 0, 0]
                                elif o['tripOrdersCount'] == 2:
                                    dict_orders[rest_name] = [0, 1, 0]
                                else:
                                    dict_orders[rest_name] = [0, 0, 1]
                        try:
                            if orders['isEndOfListReached']:
                                reach = False
                        except TypeError:
                            break
                    for prod in productivity['productivityStatistics']:
                        prod_dict[prod['unitName']] = prod['ordersPerCourierLabourHour']
                    for delivery in statistics['unitsStatistics']:
                        uuid = delivery['unitId']
                        rest_name = delivery['unitName']
                        avg_del = timedelta(seconds=delivery['avgDeliveryOrderFulfillmentTime'])
                        shelf = timedelta(seconds=delivery['avgHeatedShelfTime'])
                        trip = delivery['tripsCount']
                        prod_couriers = prod_dict[rest_name]
                        later = delivery['lateOrdersCount']
                        try:
                            workload = round(delivery['tripsDuration'] / delivery['couriersShiftsDuration'] * 100, 2)
                        except ZeroDivisionError:
                            workload = 0
                        if avg_del >= timedelta(seconds=2100):
                            em_del = f'\U00002757'
                        elif avg_del >= timedelta(seconds=2400):
                            em_del = f'\U0000203C'
                        else:
                            em_del = ''
                        if shelf > timedelta(seconds=180):
                            em_sh = f'\U00002757'
                        else:
                            em_sh = ''
                        if later > 0:
                            em_later = f'\U00002757'
                        else:
                            em_later = ''
                        ways = dict_orders.get(rest_name)
                        one = ways[0]
                        two = int(ways[1] / 2)
                        three = int(ways[2] / 3)
                        try:
                            perc_one = int(round(one / trip * 100, 0))
                        except ZeroDivisionError:
                            perc_one = 0
                        try:
                            perc_two = int(round(two / trip * 100, 0))
                        except ZeroDivisionError:
                            perc_two = 0
                        try:
                            perc_three = int(round(three / trip * 100, 0))
                        except ZeroDivisionError:
                            perc_three = 0
                        message = f'\U0001F69A Краткий отчет по доставке за {datetime.strftime(created_after, "%d.%m")}\n\n' \
                                  f'\U0001F355 <b>{rest_name}</b>\n' \
                                  f'Заказов на курьера в час: {prod_couriers}\n' \
                                  f'Скорость доставки: {avg_del} {em_del}\n' \
                                  f'Время на полке: {shelf} {em_sh}\n' \
                                  f'Опоздания: {later} {em_later}\n\n' \
                                  f'Поездки с 1 заказом: {one} ({perc_one}%)\n' \
                                  f'Поездки с 2 заказами: {two} ({perc_two}%)\n' \
                                  f'Поездки с 3 и более: {three} ({perc_three}%)\n' \
                                  f'Загруженность курьеров: {workload}%\n\n'
                        await send.sending_statistics(order["chat_id"], message, order["country"], uuid,
                                                      order['timezone'], logger, 'courier', order['id'],
                                                      order['concept'])
                except TypeError:
                    logger.error(f'Type ERROR statistics - {statistics}')
                except KeyError:
                    logger.error(f'Key ERROR statistics - {statistics}')
    await pool.close()


async def get_orders(dt, post, chat, user):
    logger = Log('COURIERS STATISTICS')
    db = AsyncDatabase()
    send = Send(db=db)
    pool = await db.create_pool()
    access = await db.select_user(pool, user)
    dt_end = datetime.strftime(dt.replace(hour=0, minute=0, second=0, microsecond=0), '%Y-%m-%dT%H:%M:%S')
    dt_start = dt.date() - timedelta(days=1)
    dt_start_str = datetime.strftime(dt_start, '%Y-%m-%dT%H:%M:%S')
    data = post.split('.')
    if access:
        if data[0] == 'c':
            await order_certs(data, access['access'], dt_start_str, dt_end, chat)
        elif data[0] == 'w':
            await order_wait(data, access['access'], dt_start_str, dt_end, chat)
        elif data[0] == 'l':
            dt_end = datetime.strftime(dt.replace(hour=0, minute=0, second=0, microsecond=0),
                                       '%Y-%m-%dT%H:%M:%S')
            await order_later(data, access['access'], dt_start_str, dt_end, chat)
        elif data[0] == 's':
            await order_later_rest(data, access['access'], dt_start_str, dt_end, chat)
    else:
        message = f'\U000026D4 Вам отказано в доступе!\n' \
                  f'Ссылка на подключение:\n' \
                  f'https://marketplace.dodois.io/apps/11ECF3AAF97D059CB9706F21406EBD44'
        await send.sending(chat, message, logger, 0)
    await pool.close()
